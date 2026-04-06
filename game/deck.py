import random
from constants import SUITS, RANKS

cardValues = {r: min(10, i+1) if r!= 'A' else 11 for i, r in enumerate(RANKS)}

fullDeck= [(r, s) for s in SUITS for r in RANKS]

class InfiniteDeck:
    #Every card draw is equally likely whether it has been drawn all ready
    def __init__(self):
        self.cards = fullDeck

    def draw(self):
        return fullDeck[random.randint(0, 51)]
    
    def reset(self):
        pass 

class FiniteDeck:
    #cards are drawn without replacement and then deck is reset after every game
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        self.cards = list(fullDeck)
        random.shuffle(self.cards)

    def draw(self):
        if not self.cards:
            self.reset()
        return self.cards.pop()
    
def makeDeck(infinite: bool):
    return InfiniteDeck() if infinite else FiniteDeck()