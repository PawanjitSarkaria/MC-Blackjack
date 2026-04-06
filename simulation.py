"""
Triple-buffer game pipeline:
  Slot A (animating) → game currently being shown
  Slot B (queued)    → next game, fully computed, ready instantly
  Slot C (computing) → game being computed in a background thread

When Slot A finishes:
  A ← B
  B ← C (atomic swap)
  C ← start computing next game in thread
"""
import threading
import queue
from game.animation import runGame
from game.deck import makeDeck


class SimulationPipeline:
    def __init__(self, policy_idx, infinite_deck, balance, bet_fn):
        """
        bet_fn: callable that returns current bet (read live so changes apply)
        """
        self.policy_idx   = policy_idx
        self.infinite     = infinite_deck
        self.balance      = balance
        self.bet_fn       = bet_fn

        self._deck        = makeDeck(infinite_deck)
        self._lock        = threading.Lock()

        # Slot B: the queued game (events, result, delta)
        self._queued      = None
        # Slot C result lands here
        self._compute_q   = queue.Queue(maxsize=1)
        self._running     = True
        self._thread      = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _compute_game(self):
        bet = max(1, self.bet_fn())
        events, result, delta = runGame(self._deck, self.policy_idx, self.balance, bet)
        return events, result, delta, bet

    def _worker(self):
        """Background thread: keep computing games and pushing to _compute_q."""
        while self._running:
            try:
                game = self._compute_game()
                self._compute_q.put(game, timeout=1)
            except Exception:
                pass

    def _pull_computed(self):
        """Non-blocking drain of the compute queue into slot B."""
        try:
            self._queued = self._compute_q.get_nowait()
        except queue.Empty:
            pass

    def get_next_game(self):
        """
        Called when the animator finishes a game and wants the next one.
        Returns (events, result, delta, bet) immediately from slot B,
        then refills slot B from the compute thread.
        """
        # Try to get from slot B; if empty, block briefly (race condition edge case)
        if self._queued is None:
            self._pull_computed()

        if self._queued is None:
            # Last resort: compute synchronously (should almost never happen)
            game = self._compute_game()
        else:
            game = self._queued
            self._queued = None

        # Immediately try to refill slot B from background thread
        self._pull_computed()
        return game

    def reconfigure(self, policy_idx, infinite_deck, balance):
        """Called when user changes settings. Drains and restarts."""
        self._running = False
        # drain
        try:
            while True:
                self._compute_q.get_nowait()
        except queue.Empty:
            pass

        self.policy_idx  = policy_idx
        self.infinite    = infinite_deck
        self.balance     = balance
        self._deck       = makeDeck(infinite_deck)
        self._queued     = None
        self._running    = True
        self._thread     = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
