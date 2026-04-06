# animation event queues and card slide/flip
# speed multiplier is apllied and scales all timing

import pygame
import time
from constants import (CARD_WIDTH, CARD_HEIGHT, CARD_START, DEALER, PLAYER,
                    SLIDE_CARD, DELAY, RESOLVE,
                    SCREEN_WIDTH, WIN, LOSE, PUSH)
from simulator.cardDesign import build_card, build_card_back
from game.animation import (dealPlayer, dealDealer, dealerFlip,
                        playerHit, dealerHit, resolve)

CARD_SPACING = 26


class AnimCard:
    """A card being displayed — tracks position, face, and slide tween."""
    def __init__(self, rank, suit, face_up,
                start_x, start_y, target_x, target_y,
                slide_ms=SLIDE_CARD):
        self.rank    = rank
        self.suit    = suit
        self.face_up = face_up
        self.x       = float(start_x)
        self.y       = float(start_y)
        self.tx      = float(target_x)
        self.ty      = float(target_y)
        self.sliding = True
        self.slide_start = time.monotonic()
        self._slide_ms   = max(slide_ms, 1)   # never zero

    def update(self):
        if self.sliding:
            elapsed = (time.monotonic() - self.slide_start) * 1000
            t = min(elapsed / self._slide_ms, 1.0)
            t = 1 - (1 - t) ** 3   # ease-out cubic
            self.x = self.x + (self.tx - self.x) * t if t < 1 else self.tx
            self.y = self.y + (self.ty - self.y) * t if t < 1 else self.ty
            if t >= 1:
                self.sliding = False

    def draw(self, surf):
        card_surf = build_card(self.rank, self.suit) if self.face_up else build_card_back()
        surf.blit(card_surf, (int(self.x), int(self.y)))

    def is_settled(self):
        return not self.sliding


class Animator:
    def __init__(self):
        self.reset()

    def reset(self):
        self.player_cards    = []
        self.dealer_cards    = []
        self._events         = []
        self._event_idx      = 0
        self._next_event_time = 0
        self._resolve_result  = None
        self._resolve_timer   = 0
        self._resolve_duration = RESOLVE
        self._card_slide_ms   = SLIDE_CARD
        self._card_delay_ms   = DELAY
        self._done            = False
        self._paused          = False
        self._pause_remaining = 0

    def load_game(self, events, speed=1):
        """Load a new set of pre-computed events. Speed scales all timings."""
        speed = max(1, speed)
        self.player_cards     = []
        self.dealer_cards     = []
        self._events          = events
        self._event_idx       = 0
        self._next_event_time = pygame.time.get_ticks() + max(80 // speed, 10)
        self._resolve_result  = None
        self._resolve_timer   = 0
        self._done            = False
        # Scale timings by speed multiplier
        self._card_slide_ms    = max(SLIDE_CARD  // speed, 15)
        self._card_delay_ms    = max(DELAY  // speed, 15)
        self._resolve_duration = max(RESOLVE     // speed, 120)

    def pause(self):
        if not self._paused:
            self._paused = True
            self._pause_remaining = max(0, self._next_event_time - pygame.time.get_ticks())

    def resume(self):
        if self._paused:
            self._paused = False
            self._next_event_time = pygame.time.get_ticks() + self._pause_remaining

    def is_done(self):
        return self._done

    def _card_target(self, cards_list, zone_y):
        n   = len(cards_list)
        bx  = CARD_START + n * CARD_SPACING
        return bx, zone_y

    def update(self):
        if self._paused or self._done:
            return

        now = pygame.time.get_ticks()

        for c in self.player_cards + self.dealer_cards:
            c.update()

        # Countdown resolve timer
        if self._resolve_result is not None:
            if now - self._resolve_timer > self._resolve_duration:
                self._done = True
            return

        if self._event_idx >= len(self._events):
            return

        if now < self._next_event_time:
            return

        ev = self._events[self._event_idx]
        self._event_idx += 1
        self._process_event(ev, now)

    def _process_event(self, ev, now):
        etype = ev["type"]

        if etype in (dealPlayer, playerHit):
            r, s  = ev["card"]
            tx, ty = self._card_target(self.player_cards, PLAYER)
            c = AnimCard(r, s, ev["face_up"], SCREEN_WIDTH // 2, DEALER - 60, tx, ty, slide_ms=self._card_slide_ms)
            self.player_cards.append(c)
            self._next_event_time = now + self._card_delay_ms

        elif etype in (dealDealer, dealerHit):
            r, s  = ev["card"]
            tx, ty = self._card_target(self.dealer_cards, DEALER)
            c = AnimCard(r, s, ev["face_up"], SCREEN_WIDTH // 2, DEALER - 60, tx, ty, slide_ms=self._card_slide_ms)
            self.dealer_cards.append(c)
            self._next_event_time = now + self._card_delay_ms

        elif etype == dealerFlip:
            for c in self.dealer_cards:
                if not c.face_up:
                    r, s   = ev["card"]
                    c.rank = r
                    c.suit = s
                    c.face_up = True
                    break
            self._next_event_time = now + self._card_delay_ms

        elif etype == resolve:
            self._resolve_result = ev["result"]
            self._resolve_timer  = now

    def get_resolve_info(self):
        """Returns (result_str, flash_color, alpha) or None."""
        if self._resolve_result is None:
            return None
        elapsed = pygame.time.get_ticks() - self._resolve_timer
        t = min(elapsed / max(self._resolve_duration, 1), 1.0)
        if t < 0.3:
            alpha = int(255 * (t / 0.3))
        elif t < 0.7:
            alpha = 255
        else:
            alpha = int(255 * (1 - (t - 0.7) / 0.3))

        color_map = {"win": WIN, "blackjack": WIN, "lose": LOSE, "push": PUSH}
        return (self._resolve_result,
                color_map.get(self._resolve_result, WIN),
                alpha)

    def draw(self, surf):
        for c in self.dealer_cards:
            c.draw(surf)
        for c in self.player_cards:
            c.draw(surf)
