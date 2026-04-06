# calculates events of a game and return what to animate
#game logic and animation are seperated

from game.hand import handValue, isBust, isBlackJack, isSoft
from game.policies import POLICIES

#possible events
dealPlayer = 'dealPlayer'
dealDealer = 'dealDealer'
playerHit = 'playerHit'
dealerHit = 'dealerHit'
dealerFlip = 'dealerFlip' #flip face down card
resolve = 'resolve' 

def dealerPolicy(cards):
    #dealer stick on 17+
    v = handValue(cards)
    if v >= 17:
        return True
    return False

def runGame(deck, policyID, balance, bet):
    '''
    runs 1 complete game returns( events, resultStr, betret)
    reultStr: "win" , "lose", "push", "blackjack"
    betret = bet return negative means we lost, 0 means it was pushed, more poitive means we won
    '''
    policy= POLICIES[policyID]
    events = []

    #initial: deal 2 cards each
    p_hand = []
    d_hand = []

    c= deck.draw(); p_hand.append(c)
    events.append({"type": dealPlayer, "card": c, "faceUP": True})

    c= deck.draw(); d_hand.append(c)
    events.append({"type": dealDealer, "card": c, "faceUP": True})

    c= deck.draw(); p_hand.append(c)
    events.append({"type": dealPlayer, "card": c, "faceUP": True})

    c= deck.draw(); d_hand.append(c)
    events.append({"type": dealDealer, "card": c, "faceUP": False}) #dealers hidden card

    #check if player has blackjack
    if isBlackJack(p_hand):
        events.append({"type": dealerFlip, "card": d_hand[1]})
        #if dealer has balckjack
        if isBlackJack(d_hand):
            events.append({"type":resolve, "result": "push", "betret": 0, "p_hand": list(p_hand), "d_hand": list(d_hand)})
            return events, "push", 0
        betret = int (bet * 1.5)
        events.append({"type": resolve, "result": "blackjack", "betret": betret, "p_hand": list(p_hand), "d_hand": list(d_hand)})
        return events, "blackjack", betret
    
    #player turn
    #policy true= stick, false= hit
    while not policy(p_hand) and not isBust(p_hand):
        c= deck.draw(); p_hand.append(c)
        events.append({"type": playerHit, "card": c, "faceUp": True})

    #revel dealer card
    events.append({"type": dealerFlip, "card": d_hand[1]})

    if isBust(p_hand):
        events.append({"type": resolve, "result": "lose", "betret": -bet, "p_hand": list(p_hand), "d_hand": list(d_hand)})
        return events, "lose", -bet
    
    #dealer turn
    while dealerPolicy(d_hand):
        c= deck.draw(); d_hand.append(c)
        events.append({"type": dealerHit, "card": c, "faceUp": True})

    #resolve
    pv = handValue(p_hand)
    dv = handValue(d_hand)
    if isBust(d_hand) or pv > dv:
        result, retbet = "win", bet
    elif pv < dv:
        result, retbet = "lose", -bet
    else:
        result, retbet = "push", 0
    
    events.append({"type": resolve, "result": result, "betret": retbet, "p_hand": list(p_hand), "d_hand": list(d_hand)})
    
    return events, result, retbet