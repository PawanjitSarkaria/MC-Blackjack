#draw table
import pygame
from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, CARD_WIDTH, CARD_HEIGHT, DEALER, PLAYER, CARD_START, FELT, DARK_FELT, LINING, GOLD, WHITE, TEXT)

background = None

def drawOval(surf, color, cx, cy, W, H, width=2):
    rect = pygame.Rect(cx - W, cy - H, 2*W, 2*H)
    pygame.draw.ellipse(surf, color, rect, width)

def TableBuild(w, h):
    global background
    surf = pygame.Surface((w, h))

    #MAIN BACKGROUND
    surf.fill(FELT)

    # make darker rectanlge indside
    pygame.draw.rect(surf, DARK_FELT, (60, 100, w-120, h-200))

    #border oval
    drawOval(surf, LINING, w//2, h//2, w//2-30, h//2-20, 3)
    drawOval(surf, GOLD, w//2, h//2, w//2-32, h//2-22, 1)

    #dealer zone lable
    font= pygame.font.SysFont("arial", 14)
    t= font.render("DEALER", True, GOLD)
    surf.blit(t, (CARD_START, DEALER-28))

    #player zone
    t2= font.render("PLAYER", True, GOLD)
    surf.blit(t2,(CARD_START, PLAYER-28))

    #center divider and circle
    pygame.draw.line(surf, LINING, (60, h//2), (w-60, h//2 +10), 1)
    drawOval(surf, LINING, w//2, h//2+10, 60, 40, 2)

    background= surf
    return surf

def drawTable(screen, table_surf):
    screen.blit(table_surf, (0, 0))
