# headsup display
import pygame
from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, GOLD, WHITE, BLACK, DARK_GREY,
                    TEXT, PANEL, PANEL_SIDES, WIN,
                    LOSE, PUSH, GREEN_BUTTON, GB_HOVER,
                    RED_BUTTON, RB_HOVER, BLUE_BUTTON, BB_HOVER,
                    ORANGE_BUTTON, OB_HOVER, POLICIES, GREY,
                    CREAM, LIGHT_GREY, DARK_RED, SPEED_OPTIONS)

_fonts = {}


def _font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont("arial,helvetica", size, bold=bold)
    return _fonts[key]


def _panel(surf, x, y, w, h, alpha=210, radius=8):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, (*PANEL, alpha), (0, 0, w, h), border_radius=radius)
    pygame.draw.rect(s, (*PANEL_SIDES, 180), (0, 0, w, h), 1, border_radius=radius)
    surf.blit(s, (x, y))


def _text(surf, txt, x, y, size=16, color=WHITE, bold=False, anchor="left"):
    f = _font(size, bold)
    t = f.render(str(txt), True, color)
    if anchor == "center":
        r = t.get_rect(center=(x, y))
    elif anchor == "right":
        r = t.get_rect(right=x, centery=y)
    else:
        r = t.get_rect(topleft=(x, y))
    surf.blit(t, r)
    return r


def _button(surf, rect, label, color, hover_color, mouse_pos,
            text_color=WHITE, size=15, bold=True, radius=6, selected=False):
    x, y, w, h = rect
    hovered = pygame.Rect(rect).collidepoint(mouse_pos)
    c = hover_color if hovered else color
    if selected:
        pygame.draw.rect(surf, GOLD, (x-2, y-2, w+4, h+4), border_radius=radius+2)
    pygame.draw.rect(surf, c, rect, border_radius=radius)
    pygame.draw.rect(surf, (255, 255, 255, 60), rect, 1, border_radius=radius)
    _text(surf, label, x + w//2, y + h//2, size, text_color, bold, anchor="center")
    return hovered


class HUD:
    def __init__(self):
        self.balance = 1000
        self.bet = 50
        self.games_played = 0
        self.wins = 0
        self.losses = 0
        self.pushes = 0
        self.policy_idx = 0
        self.infinite_deck = True
        self.speed_idx = 0          # index into SPEED_OPTIONS

        self._bet_input_active = False
        self._bet_input_str = ""

        # Button rects (assigned during draw)
        self.btn_play_pause = pygame.Rect(0, 0, 0, 0)
        self.btn_bet        = pygame.Rect(0, 0, 0, 0)
        self.btn_menu       = pygame.Rect(0, 0, 0, 0)
        self.btn_speed      = pygame.Rect(0, 0, 0, 0)

        # Resolve flash
        self._flash_text  = ""
        self._flash_color = WHITE
        self._flash_alpha = 0

    def record_result(self, result, delta):
        self.games_played += 1
        self.balance = max(0, self.balance + delta)
        if result in ("win", "blackjack"):
            self.wins += 1
        elif result == "lose":
            self.losses += 1
        else:
            self.pushes += 1

        label_map = {"win":       "WIN +$" + str(abs(delta)), "blackjack": "BLACKJACK! +$" + str(abs(delta)), "lose":      "LOSE -$" + str(abs(delta)), "push":      "PUSH"}
        color_map = {"win": WIN, "blackjack": WIN, "lose": LOSE, "push": PUSH}
        self._flash_text  = label_map.get(result, "")
        self._flash_color = color_map.get(result, WHITE)
        self._flash_alpha = 255

    def reset(self, starting_balance):
        self.balance = starting_balance
        self.games_played = 0
        self.wins = 0
        self.losses = 0
        self.pushes = 0
        self._flash_alpha = 0

    def effective_bet(self):
        return min(self.bet, self.balance) if self.balance > 0 else 0

    def current_speed(self):
        return SPEED_OPTIONS[self.speed_idx]

    def draw(self, surf, running, mouse_pos):
        W = SCREEN_WIDTH

        # ── Top-left: stats panel ──────────────────────────────────────────
        _panel(surf, 10, 10, 220, 130)
        _text(surf, "GAMES PLAYED", 20, 18, 11, TEXT, bold=True)
        _text(surf, f"{self.games_played:,}", 20, 34, 28, GOLD, bold=True)

        _text(surf, "W",  20,  72, 12, WIN,  bold=True)
        _text(surf, "L",  82,  72, 12, LOSE, bold=True)
        _text(surf, "P",  144, 72, 12, PUSH, bold=True)
        _text(surf, str(self.wins),   20,  88, 16, WIN,  bold=True)
        _text(surf, str(self.losses), 82,  88, 16, LOSE, bold=True)
        _text(surf, str(self.pushes), 144, 88, 16, PUSH, bold=True)

        total = self.wins + self.losses + self.pushes
        wr = f"{self.wins / total * 100:.1f}%" if total > 0 else "--"
        _text(surf, f"Win rate  {wr}", 20, 112, 12, TEXT)

        # ── Top-right: balance panel ───────────────────────────────────────
        _panel(surf, W - 230, 10, 220, 80)
        _text(surf, "BALANCE", W - 220, 18, 11, TEXT, bold=True)
        bal_color = WIN if self.balance > 0 else LOSE
        _text(surf, f"${self.balance:,}", W - 120, 50, 28, bal_color, bold=True, anchor="center")

        # ── Policy + deck strip (top-center) ──────────────────────────────
        _panel(surf, W//2 - 180, 10, 360, 52)
        _text(surf, POLICIES[self.policy_idx], W//2, 24, 13, GOLD, bold=True, anchor="center")
        deck_str = "Infinite deck" if self.infinite_deck else "Single deck"
        _text(surf, deck_str, W//2, 44, 12, TEXT, anchor="center")

        # ── Resolve flash (center screen) ──────────────────────────────────
        if self._flash_alpha > 0:
            self._flash_alpha = max(0, self._flash_alpha - 3)
            f = _font(52, bold=True)
            t = f.render(self._flash_text, True, self._flash_color)
            t.set_alpha(self._flash_alpha)
            r = t.get_rect(center=(W//2, SCREEN_HEIGHT//2 - 10))
            surf.blit(t, r)

        # ── Bottom control strip ───────────────────────────────────────────
        strip_y = SCREEN_HEIGHT - 68
        _panel(surf, 10, strip_y, W - 20, 58, alpha=230, radius=10)

        # Play / Pause
        pp_label = "⏸  PAUSE" if running else "▶  PLAY"
        pp_color = RED_BUTTON if running else GREEN_BUTTON
        pp_hover = RB_HOVER if running else GB_HOVER
        self.btn_play_pause = (20, strip_y + 8, 130, 40)
        _button(surf, self.btn_play_pause, pp_label, pp_color, pp_hover, mouse_pos, size=14)

        # Bet label + input field
        _text(surf, "BET", 170, strip_y + 15, 11, TEXT, bold=True)
        bet_rect = (168, strip_y + 28, 80, 22)
        bet_bg = (50, 50, 50) if not self._bet_input_active else (70, 60, 20)
        pygame.draw.rect(surf, bet_bg, bet_rect, border_radius=4)
        pygame.draw.rect(surf, GOLD if self._bet_input_active else PANEL_SIDES, bet_rect, 1, border_radius=4)
        bet_display = ("$" + self._bet_input_str + "|") if self._bet_input_active else f"${self.bet}"
        _text(surf, bet_display, 172, strip_y + 39, 14, GOLD, bold=True)
        self.btn_bet = bet_rect

        # Chip quick-select buttons
        for i, chip in enumerate([10, 25, 50, 100]):
            cx = 260 + i * 52
            cr = (cx, strip_y + 8, 46, 40)
            _button(surf, cr, f"${chip}", (60, 60, 60), (80, 80, 80), mouse_pos, size=13)

        # ── Speed button — cycles 1x → 2x → 5x → 10x ─────────────────────
        speed = SPEED_OPTIONS[self.speed_idx]
        spd_label = f"▶▶  {speed}x"
        # Color shifts warmer as speed increases so state is obvious at a glance
        spd_colors = {
            1:  ((50,  50,  50),  (70,  70,  70)),
            2:  ((40,  100, 170), (55,  120, 200)),
            5:  ((150, 90,  10),  (180, 110, 20)),
            10: ((160, 30,  30),  (190, 50,  50)),
        }
        sc, sh = spd_colors.get(speed, ((50, 50, 50), (70, 70, 70)))
        spd_rect = (W - 270, strip_y + 8, 100, 40)
        _button(surf, spd_rect, spd_label, sc, sh, mouse_pos,
                size=14, selected=(speed > 1))
        self.btn_speed = pygame.Rect(spd_rect)

        # Menu button (only visible when simulation is not running)
        if not running:
            self.btn_menu = pygame.Rect(W - 158, strip_y + 8, 120, 40)
            _button(surf, self.btn_menu, "☰  MENU",
                    BLUE_BUTTON, BB_HOVER, mouse_pos, size=14)
        else:
            self.btn_menu = pygame.Rect(0, 0, 0, 0)

    def handle_click(self, pos, running):
        """Returns action string or None."""
        if pygame.Rect(self.btn_play_pause).collidepoint(pos):
            return "toggle_play"

        if pygame.Rect(self.btn_bet).collidepoint(pos):
            self._bet_input_active = True
            self._bet_input_str = str(self.bet)
            return "bet_focus"

        if not running and pygame.Rect(self.btn_menu).collidepoint(pos):
            return "open_menu"

        # Speed button — cycle through SPEED_OPTIONS
        if self.btn_speed.collidepoint(pos):
            self.speed_idx = (self.speed_idx + 1) % len(SPEED_OPTIONS)
            return "speed_changed"

        # Chip buttons
        strip_y = SCREEN_HEIGHT - 68
        for i, chip in enumerate([10, 25, 50, 100]):
            cx = 260 + i * 52
            cr = pygame.Rect(cx, strip_y + 8, 46, 40)
            if cr.collidepoint(pos):
                self.bet = chip
                return "bet_set"

        self._bet_input_active = False
        return None

    def handle_key(self, event):
        if not self._bet_input_active:
            return
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            try:
                v = int(self._bet_input_str)
                self.bet = max(1, min(v, self.balance))
            except ValueError:
                pass
            self._bet_input_active = False
        elif event.key == pygame.K_ESCAPE:
            self._bet_input_active = False
        elif event.key == pygame.K_BACKSPACE:
            self._bet_input_str = self._bet_input_str[:-1]
        elif event.unicode.isdigit() and len(self._bet_input_str) < 6:
            self._bet_input_str += event.unicode

    def draw_hand_values(self, surf, player_val, dealer_val, dealer_hidden):
        if player_val:
            _text(surf, f"Total: {player_val}", 10, 520, 16, GOLD, bold=True)
        if dealer_val:
            label = f"Total: {dealer_val}" if not dealer_hidden else "Total: ?"
            _text(surf, label, 10, 148, 16, GOLD, bold=True)
