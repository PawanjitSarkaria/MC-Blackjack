"""
State machine:
  IDLE    → waiting for user to press Play
  RUNNING → auto-advancing games
  PAUSED  → animation frozen, menu accessible
  MENU    → settings overlay open
"""
import sys
import pygame
from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, GOLD, NEXT_GAME, SPEED_OPTIONS)
from simulator.cardDesign import init_sprites
from simulator.table import TableBuild, drawTable
from simulator.animationQueue import Animator
from simulator.display import HUD
from simulator.menu import Menu
from simulation import SimulationPipeline
from game.hand import handValue

STATE_IDLE    = "idle"
STATE_RUNNING = "running"
STATE_PAUSED  = "paused"
STATE_MENU    = "menu"


def hand_total(anim_cards):
    cards = [(c.rank, c.suit) for c in anim_cards if c.face_up]
    return handValue(cards) if cards else None


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock  = pygame.time.Clock()

    init_sprites()

    table_surf = TableBuild(SCREEN_WIDTH, SCREEN_HEIGHT)
    animationQueue   = animationQueue()
    hud        = HUD()
    menu       = Menu()

    state         = STATE_IDLE
    pipeline      = None
    _next_game_at = 0
    _pending      = None   # (result_str, delta) waiting to be recorded

    # ── Pipeline helpers ──────────────────────────────────────────────────────
    def start_pipeline():
        nonlocal pipeline
        if pipeline:
            pipeline.stop()
        pipeline = SimulationPipeline(
            policy_idx    = hud.policy_idx,
            infinite_deck = hud.infinite_deck,
            balance       = hud.balance,
            bet_fn        = hud.effective_bet,
        )

    def load_next_game():
        nonlocal _next_game_at, _pending
        if pipeline is None:
            return
        speed = hud.current_speed()
        events, result, delta, bet = pipeline.get_next_game()
        animationQueue.load_game(events, speed=speed)
        pipeline.balance = hud.balance
        _next_game_at = 0
        _pending = (result, delta)

    # ── Fonts for idle screen ─────────────────────────────────────────────────
    font_title = pygame.font.SysFont("arial,helvetica", 40, bold=True)
    font_sub   = pygame.font.SysFont("arial,helvetica", 18)

    running_loop = True
    while running_loop:
        mouse_pos = pygame.mouse.get_pos()
        clock.tick(FPS)

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_loop = False

            elif event.type == pygame.KEYDOWN:
                hud.handle_key(event)
                menu.handle_key(event)
                if event.key == pygame.K_SPACE:
                    if state == STATE_RUNNING:
                        state = STATE_PAUSED
                        animationQueue.pause()
                    elif state in (STATE_IDLE, STATE_PAUSED):
                        if state == STATE_IDLE:
                            start_pipeline()
                            load_next_game()
                        state = STATE_RUNNING
                        animationQueue.resume()
                elif event.key == pygame.K_ESCAPE:
                    if state == STATE_MENU:
                        state = STATE_PAUSED if animationQueue.player_cards else STATE_IDLE
                        menu.visible = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if menu.visible:
                    result = menu.handle_click(event.pos)
                    if result:
                        hud.policy_idx    = result["policy_idx"]
                        hud.infinite_deck = result["infinite_deck"]
                        if result["restart"] or result["balance"] != hud.balance:
                            hud.reset(result["balance"])
                            animationQueue.reset()
                            if pipeline:
                                pipeline.stop()
                            pipeline = None
                            state = STATE_IDLE
                        else:
                            if pipeline:
                                pipeline.reconfigure(
                                    hud.policy_idx,
                                    hud.infinite_deck,
                                    hud.balance,
                                )
                            state = STATE_PAUSED if animationQueue.player_cards else STATE_IDLE
                        menu.visible = False
                else:
                    action = hud.handle_click(event.pos, state == STATE_RUNNING)
                    if action == "toggle_play":
                        if state == STATE_RUNNING:
                            state = STATE_PAUSED
                            animationQueue.pause()
                        elif state == STATE_IDLE:
                            start_pipeline()
                            load_next_game()
                            state = STATE_RUNNING
                        elif state == STATE_PAUSED:
                            state = STATE_RUNNING
                            animationQueue.resume()
                    elif action == "open_menu":
                        menu.open(hud.balance, hud.policy_idx, hud.infinite_deck)
                        menu.visible = True
                        state = STATE_MENU
                    elif action == "speed_changed":
                        # Speed change takes effect on the next game load;
                        # nothing extra needed here.
                        pass

        # ── Update ────────────────────────────────────────────────────────────
        if state == STATE_RUNNING:
            animationQueue.update()

            if animationQueue.is_done():
                # Record result from the game that just finished
                if _pending:
                    result_str, delta = _pending
                    hud.record_result(result_str, delta)
                    _pending = None

                # Schedule next game with speed-adjusted gap
                if _next_game_at == 0:
                    speed = hud.current_speed()
                    gap   = max(NEXT_GAME // speed, 40)
                    _next_game_at = pygame.time.get_ticks() + gap

                if pygame.time.get_ticks() >= _next_game_at:
                    if hud.balance <= 0:
                        state = STATE_IDLE
                    else:
                        load_next_game()

        # ── Draw ──────────────────────────────────────────────────────────────
        drawTable(screen, table_surf)
        animationQueue.draw(screen)

        # Hand value overlays
        pv = hand_total(animationQueue.player_cards) if animationQueue.player_cards else None
        dv = hand_total(animationQueue.dealer_cards) if animationQueue.dealer_cards else None
        dealer_hidden = any(not c.face_up for c in animationQueue.dealer_cards)
        hud.draw_hand_values(screen, pv, dv, dealer_hidden)

        hud.draw(screen, state == STATE_RUNNING, mouse_pos)

        # Resolve flash overlay
        ri = animationQueue.get_resolve_info()
        if ri:
            result_s, flash_col, alpha = ri
            label_map = {"win": "WIN", "blackjack": "BLACKJACK!", "lose": "LOSE", "push": "PUSH"}
            label = label_map.get(result_s, "")
            f = pygame.font.SysFont("arial,helvetica", 58, bold=True)
            t = f.render(label, True, flash_col)
            t.set_alpha(alpha)
            r = t.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            screen.blit(t, r)

        # Idle title screen
        if state == STATE_IDLE and not animationQueue.player_cards:
            title_s = font_title.render(TITLE, True, GOLD)
            tr = title_s.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60))
            screen.blit(title_s, tr)
            sub_lines = [
                "Press PLAY or SPACE to start the simulation.",
                "Open MENU to change policy, deck type, or starting balance.",
            ]
            for i, line in enumerate(sub_lines):
                st = font_sub.render(line, True, (200, 200, 200))
                sr = st.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 10 + i * 28))
                screen.blit(st, sr)

        if menu.visible:
            menu.draw(screen, mouse_pos)

        pygame.display.flip()

    if pipeline:
        pipeline.stop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
