#card image render using pygame
import pygame
from constants import CARD_WIDTH, CARD_HEIGHT, SUITS, RANKS

cache= {}
backSide= None

RED    = (200, 30,  30)
BLACK  = (20,  20,  20)
CREAM  = (255, 252, 240)
BORDER = (180, 170, 140)
GOLD   = (212, 175,  55)

_PIP_LAYOUTS = {
    1:  [(0.5, 0.5)],
    2:  [(0.5, 0.22), (0.5, 0.78)],
    3:  [(0.5, 0.20), (0.5, 0.50), (0.5, 0.80)],
    4:  [(0.25, 0.22), (0.75, 0.22), (0.25, 0.78), (0.75, 0.78)],
    5:  [(0.25, 0.22), (0.75, 0.22), (0.5,  0.50), (0.25, 0.78), (0.75, 0.78)],
    6:  [(0.25, 0.20), (0.75, 0.20), (0.25, 0.50), (0.75, 0.50), (0.25, 0.80), (0.75, 0.80)],
    7:  [(0.25, 0.18), (0.75, 0.18), (0.5,  0.34), (0.25, 0.50), (0.75, 0.50), (0.25, 0.78), (0.75, 0.78)],
    8:  [(0.25, 0.18), (0.75, 0.18), (0.5,  0.32), (0.25, 0.48), (0.75, 0.48), (0.5,  0.64), (0.25, 0.80), (0.75, 0.80)],
    9:  [(0.25, 0.15), (0.75, 0.15), (0.25, 0.37), (0.75, 0.37), (0.5, 0.50), (0.25, 0.63), (0.75, 0.63), (0.25, 0.85), (0.75, 0.85)],
    10: [(0.25, 0.13), (0.75, 0.13), (0.5,  0.27), (0.25, 0.42), (0.75, 0.42), (0.25, 0.58), (0.75, 0.58), (0.5,  0.73), (0.25, 0.87), (0.75, 0.87)],
}


def suit_color(suit):
    return RED if suit in ('♥', '♦') else BLACK


def pip_font_size(count, w):
    base = {1:44, 2:36, 3:32, 4:30, 5:28, 6:26, 7:24, 8:22, 9:20, 10:18}
    return max(int(base.get(count, 18) * w / CARD_WIDTH), 10)


def build_card(rank, suit, w=None, h=None):
    w = w or CARD_WIDTH
    h = h or CARD_HEIGHT
    key = (rank, suit, w, h)
    if key in cache:
        return cache[key]

    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    rad  = max(int(10 * w / CARD_WIDTH), 6)

    # Drop shadow
    shadow = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 45), (3, 3, w - 1, h - 1), border_radius=rad)
    surf.blit(shadow, (0, 0))

    # Card face
    pygame.draw.rect(surf, CREAM,  (0, 0, w, h), border_radius=rad)
    pygame.draw.rect(surf, BORDER, (0, 0, w, h), 2, border_radius=rad)

    color = suit_color(suit)
    scale = w / CARD_WIDTH
    pad   = max(int(6 * scale), 4)

    # ── Corner labels ──────────────────────────────────────────────────────
    r_size = max(int(16 * scale), 9)
    s_size = max(int(13 * scale), 8)

    f_r = pygame.font.SysFont("georgia,times new roman,serif", r_size, bold=True)
    f_s = pygame.font.SysFont("segoeuisymbol,dejavusans,arial", s_size)

    t_rank = f_r.render(rank, True, color)
    t_suit = f_s.render(suit, True, color)

    # Top-left
    surf.blit(t_rank, (pad, pad))
    surf.blit(t_suit, (pad, pad + t_rank.get_height() + 1))

    # Bottom-right (rotated 180°)
    t_rank_r = pygame.transform.rotate(t_rank, 180)
    t_suit_r = pygame.transform.rotate(t_suit, 180)
    by = h - pad - t_rank_r.get_height() - t_suit_r.get_height() - 1
    surf.blit(t_rank_r, (w - pad - t_rank_r.get_width(), by))
    surf.blit(t_suit_r, (w - pad - t_suit_r.get_width(), by + t_rank_r.get_height() + 1))

    # ── Centre content ─────────────────────────────────────────────────────
    mx = max(int(18 * scale), 12)
    my = max(int(30 * scale), 20)
    cw = w - 2 * mx
    ch = h - 2 * my

    if rank in ('J', 'Q', 'K'):
        ls = max(int(62 * scale), 28)
        f_l = pygame.font.SysFont("georgia,times new roman,serif", ls, bold=True)
        t_l = f_l.render(rank, True, color)
        surf.blit(t_l, t_l.get_rect(center=(w // 2, h // 2)))

    elif rank == 'A':
        as_ = max(int(66 * scale), 30)
        f_a = pygame.font.SysFont("segoeuisymbol,dejavusans,arial", as_, bold=True)
        t_a = f_a.render(suit, True, color)
        surf.blit(t_a, t_a.get_rect(center=(w // 2, h // 2)))

    else:
        count = int(rank)
        pip_sz = pip_font_size(count, w)
        f_pip  = pygame.font.SysFont("segoeuisymbol,dejavusans,arial", pip_sz)
        for fx, fy in _PIP_LAYOUTS.get(count, []):
            t_pip = f_pip.render(suit, True, color)
            px = mx + int(fx * cw)
            py = my + int(fy * ch)
            surf.blit(t_pip, t_pip.get_rect(center=(px, py)))

    cache[key] = surf
    return surf


def get_card_surf(rank, suit):
    """Alias used by the Monte Carlo animator."""
    return build_card(rank, suit)


def build_back(w=None, h=None):
    global _back_surf
    w = w or CARD_WIDTH
    h = h or CARD_HEIGHT
    key = (w, h)
    if key in cache:
        return cache[key]

    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    rad  = max(int(10 * w / CARD_WIDTH), 6)
    color = (30, 20, 80)

    # Shadow
    shadow = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 45), (3, 3, w - 1, h - 1), border_radius=rad)
    surf.blit(shadow, (0, 0))

    # Back face
    pygame.draw.rect(surf, color, (0, 0, w, h), border_radius=rad)
    pygame.draw.rect(surf, GOLD,  (0, 0, w, h), 2, border_radius=rad)

    ins = max(int(6 * w / CARD_WIDTH), 4)
    pygame.draw.rect(surf, GOLD, (ins, ins, w - 2*ins, h - 2*ins), 1, border_radius=max(rad - 3, 4))

    pat = pygame.Surface((w, h), pygame.SRCALPHA)
    gap = max(int(11 * w / CARD_WIDTH), 7)
    for i in range(-h, w + h, gap):
        pygame.draw.line(pat, (*GOLD, 35), (i, 0), (i + h, h), 1)
        pygame.draw.line(pat, (*GOLD, 35), (i + h, 0), (i, h), 1)
    surf.blit(pat, (0, 0))

    pygame.draw.rect(surf, GOLD, (0, 0, w, h), 2, border_radius=rad)
    pygame.draw.rect(surf, GOLD, (ins, ins, w - 2*ins, h - 2*ins), 1, border_radius=max(rad - 3, 4))

    cache[key] = surf
    if w == CARD_WIDTH and h == CARD_HEIGHT:
        backSide = surf
    return surf


def get_back_surf():
    """Alias used by the Monte Carlo animator."""
    return backSide or build_back()


def init_all():
    for s in SUITS:
        for r in RANKS:
            build_card(r, s)
    build_back()


# Alias for Monte Carlo animator compatibility
def build_card_back(w=None, h=None):
    return build_back(w, h)


# Alias used by blackjack.py entry point
def init_sprites():
    init_all()
