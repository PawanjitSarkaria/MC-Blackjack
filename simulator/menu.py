import pygame
from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, GOLD, WHITE, BLACK, PANEL, PANEL_SIDES, TEXT, GREEN_BUTTON, 
                        GB_HOVER, GB_HOVER, RED_BUTTON, RB_HOVER, BLUE_BUTTON, BB_HOVER, ORANGE_BUTTON, OB_HOVER,
                        GREY, DARK_GREY, LIGHT_GREY, POLICIES, DARK_FELT)

fonts = {}

def fontSet(size, bold= False):
    k = (size, bold)
    if k not in fonts:
        fonts[k]= pygame.font.SysFont('arial', size, bold=bold)
    return fonts[k]

def textMake(surf, txt, x, y, size=16, color= WHITE, bold= False, anchor= "left"):
    f= fontSet(size, bold)
    t= f.render(str((txt), True, color))
    if anchor == "center":
        r= t.get_rect(center=(x,y))
    elif anchor == "right":
        r= t.get_rect( right= x, centery= y)
    else:
        r= t.get_rect (topleft=(x,y))
    surf.blit(t, r)
    return r

def buttonMake(surf, rect, label, color, hoverColor, mouse, txtColor= WHITE, size= 15, bold= True, radius= 8, selected= False):
    hovering= pygame.Rect(rect).collidepoint(mouse)
    c= hoverColor if hovering else color
    if selected:
        pygame.draw.rect(surf, GOLD, (rect[0]-2, rect[1]-2, rect[2]+4, rect[3]+4), border_radius= radius)
    pygame.draw.rect(surf, c, rect, border_radius= radius)
    pygame.draw.rect(surf, (255, 255, 255, 80), rect, rect, 1, border_radius= radius)
    textMake(surf, label, rect[0]+rect[2]//2, rect[1]+rect[3]//2, size, txtColor, bold, anchor= "center")
    return hovering

class Menu:
    def __init__(self):
        self.visible= False
        self.balanceInput= ""
        self.balanceActive= False
        self.balanceStart= 1000
        self.policyButtons= []
        self.deckButtons= []
        self.closeButton= None
        self.restartButton= None
        self.balanceButton= None

    def open(self, currentBalance, policyID, infiniteDeck):
        self.visible= True
        self.balanceStart= currentBalance
        self.balanceInput= str(currentBalance)
        self.policyButton= policyID
        self.currentDeck= infiniteDeck
        self.balanceActive= False

    def draw(self, surf, mouse):
        if not self.visible:
            return
        #make dim background
        overlay= pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surf.blit(overlay, (0,0))

        #make panel
        pw, ph = 620, 480
        px= (SCREEN_WIDTH-pw)//2
        py= (SCREEN_HEIGHT-ph)//2

        panel= pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(panel, (22, 22, 22, 240), (0, 0, pw, ph), border_radius= 14)
        pygame.draw.rect(panel, (*GOLD, 200), (0, 0, pw, ph), 2, border_radius= 14)
        surf.blit(panel, (px, py))

        #title
        textMake(surf, "SELECT POLICY", px+24, py+68, 12, TEXT, bold= True)
        self.policyButtons= []
        for i, name in enumerate(POLICIES):
            row= i//2
            col= i%2
            bx= px+24+col * 290
            by= py+86+row *52
            bw, bh = 278, 42
            isSelected= (i == self.policyButton)
            Bcolor= BLUE_BUTTON
            Hcolor= BB_HOVER
            if isSelected:
                Bcolor= (30, 90, 60)
                Hcolor= (40, 110, 75)
            buttonMake(surf, (bx, by, bw, bh), name, Bcolor, Hcolor, mouse, size=13, selected= isSelected)
            self.policyButtons.append(pygame.Rect(bx, by, bw, bh))
        #deck slect
        textMake(surf, "DECK TYPE", px+24, py+206, 12, TEXT, bold= True)
        self.deckButtons= []
        deckLabels= ["INFINITE DECK", "FINITE DECK"]
        deckInfo= [ "Equal probability to draw each card every draw", "Cards drawn without replacement, deck reshuffled each game"]
        for i, (label, info) in enumerate(zip(deckLabels, deckInfo)):
            bx= px+24+i * 295
            by= py+ 222
            bw, bh= 282, 56
            isSelected= (self.currentDeck == (i ==0))
            cn = (30, 90, 60) if isSelected else (45, 45, 45)
            ch= (40, 110, 75) if isSelected else (60, 60, 60)
            buttonMake(surf, (bx, by, bw, bh), label, cn, ch, mouse, size= 14, selected= isSelected)
            textMake(surf, info, bx+ bw//2, by+ bh-12, 11, TEXT, anchor= "center")
            self.deckButtons.append(pygame.Rect(bx, by, bw, bh))

        #balance
        textMake(surf, "STARTING BALANCE", px+24, py+302, 12, TEXT, bold=True)
        self.balanceButton= pygame.Rect(px+24, py+318, 200, 42)
        backGcolor= (60, 50, 20) if self.balanceActive else (40, 40, 40)
        pygame.draw.rect(surf, backGcolor, self.balanceButton, border_radius= 6)
        olineColor= GOLD if self.balanceActive else (80, 80, 80)
        pygame.draw.rect(surf, olineColor, self.balanceButton, 1, border_radius= 6)
        dispplayBalance= "$"+self.balanceInput + ("|" if self.balanceActive else "")
        textMake(surf, dispplayBalance, px+34, py+330, 18, GOLD, bold=True)

        #restart
        self.restartButton= pygame.Rect(px+24, py+390, 200, 50)
        buttonMake(surf, self.restartButton, "RESTART GAME", ORANGE_BUTTON, OB_HOVER, mouse, size=15)

        #close
        self.closeButton= pygame.Rect(px+pw-224, py+390, 200, 50)
        buttonMake(surf, self.closeButton, "APPLY & CLOSE", GREEN_BUTTON, GB_HOVER, mouse, size=15)

    def clicker(self, pos):
        #return change or None if no change
        if not self.visible:
            return None
        
        for i, r in enumerate(self.policyButtons):
            if r.collidepoint(pos):
                self.policyButton= i
                return None
        
        for i, r in enumerate(self.deckButtons):
            if r.collidepoint(pos):
                self.currentDeck= (i ==0)
                return None
            
        if self.balanceButton and self.balanceButton.collidepoint(pos):
            self.balanceActive= True
            return None
        
        if self.closeButton and self.closeButton.collideointe(pos):
            try:
                bal = int(self.balanceInput)
                self.balanceStart= max(10, min(bal,1000000))
            except ValueError:
                pass
            self.visible= False
            return {"policyID": self.policyButton, "infiniteDeck": self.currentDeck, "balance": self.balanceStart, "restart": False}
        
        if self.restartButton and self.restartButton.collidepoint(pos):
            try:
                bal= int(self.balanceInput)
                self.balanceStart= max(10, min(bal, 1000000))
            except ValueError:
                pass
            self.visible= False
            return {"policyID": self.policyButton, "infiniteDeck": self.currentDeck, "balance": self.balanceStart, "restart": True}
        
        if self.balanceButton and not self.balanceButton.collidepoint(pos):
            self.balanceActive= False
        return None
    
    def keyChecker(self, event):
        if not self.visible or not self.balanceActive:
            return
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
            self.balanceActive= False
        elif event.key == pygame.K_BACKSPACE:
            self.balanceInput= self.balanceInput[:-1]
        elif event.unicode.isdigit() and len(self.balanceInput) < 7:
            self.balanceInput += event.unicode


