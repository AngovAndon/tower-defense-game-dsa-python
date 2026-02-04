import pygame
import math

class TowerMenu:
    def __init__(self, x, y, tower, refund_ratio=0.60):
        self.tower = tower
        self.refund = math.floor(tower.cost * refund_ratio)

        self.w = 210
        self.h = 75

        self.rect = pygame.Rect(x, y, self.w, self.h)
        self.btn_range = pygame.Rect(x + 10, y + 10, self.w - 20, 25)
        self.btn_sell  = pygame.Rect(x + 10, y + 40, self.w - 20, 25)

    def handle_click(self, pos):
        if self.btn_range.collidepoint(pos):
            return "toggle_range"
        if self.btn_sell.collidepoint(pos):
            return "sell"
        if self.rect.collidepoint(pos):
            return "inside"
        return "outside"

    def draw(self, screen, font, show_range_now):
        pygame.draw.rect(screen, (40, 40, 40), self.rect)
        pygame.draw.rect(screen, (20, 20, 20), self.rect, 2)

        pygame.draw.rect(screen, (80, 80, 120), self.btn_range)
        label = "Hide Radius" if show_range_now else "Show Radius"
        screen.blit(font.render(label, True, (255, 255, 255)),
                    (self.btn_range.x + 8, self.btn_range.y + 4))

        pygame.draw.rect(screen, (120, 60, 60), self.btn_sell)
        screen.blit(font.render(f"Remove (+${self.refund})", True, (255, 255, 255)),
                    (self.btn_sell.x + 8, self.btn_sell.y + 4))
