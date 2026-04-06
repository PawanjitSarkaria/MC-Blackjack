from game.hand import handValue, isSoft

#True means stick, false means hit

def policy1(cards):
    #stick if hand >= 17, elese hit
    return handValue(cards) >= 17

def policy2 (cards):
    #stick if hand >= 17 hard, hit unless 21
    v= handValue(cards)
    if v == 21:
        return True
    if v >= 17 and not isSoft(cards):
        return True
        #hard 17+
    return False
    #either soft 17+ or less than 17

def policy3(cards):
    #always stick
    return True

POLICIES= [policy1, policy2, policy3]