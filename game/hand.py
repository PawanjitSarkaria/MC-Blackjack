from game.deck import cardValues

def handValue (cards):
    total = sum(cardValues[r] for r, _ in cards)
    aces= sum(1 for r, _ in cards if r == 'A')
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def isSoft(cards):
    #ace is being counted as 11
    total = sum(cardValues[r] for r, _ in cards)
    aces = sum(1 for r, _ in cards if r == 'A')
    drops = 0
    # if all aces are dropped to 1, then returns false(not soft) and then if at least 1 ace wasnt dropped returns true(is soft)
    while total > 21 and aces-drops > 0:
        total -= 10
        drops += 1
    return (aces - drops) > 0

def isBust(cards):
    return handValue(cards) > 21

def isBlackJack(cards):
    return len(cards) == 2 and handValue(cards) == 21