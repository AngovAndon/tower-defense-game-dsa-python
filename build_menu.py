import pygame
from dataclasses import dataclass

from algorithms import quick_sort, binary_search_max_affordable_index


@dataclass(frozen=True)
class TowerOption:
    name: str
    cost: int


class BuildMenu:
    """Tower build menu. Options are sorted by cost using our custom Quick Sort.
    Affordable options are determined via a binary-search cutoff and rendered enabled;
    unaffordable options are rendered disabled (grayed out).
    """

    def __init__(self, x, y):
        self.rects = []
        self.x = x
        self.y = y

        # Intentionally NOT in cost order (sorting is done algorithmically).
        unsorted_options = [
            TowerOption("Sniper", 100),
            TowerOption("Shotgun", 150),
            TowerOption("Bazooka", 50),
        ]

        # Sort by cost using our custom quick sort (ascending).
        self.options = quick_sort(unsorted_options)

        for i in range(len(self.options)):
            self.rects.append(pygame.Rect(x, y + i * 40, 160, 35))

    def handle_click(self, pos, coins):
        # Determine affordability cutoff using binary search (rightmost cost <= coins).
        max_affordable = binary_search_max_affordable_index(self.options, coins)

        for i, rect in enumerate(self.rects):
            if rect.collidepoint(pos):
                if i <= max_affordable:
                    return self.options[i].name
                return None
        return None

    def draw(self, screen, font, coins):
        max_affordable = binary_search_max_affordable_index(self.options, coins)

        for i, rect in enumerate(self.rects):
            enabled = i <= max_affordable

            bg = (100, 100, 100) if enabled else (60, 60, 60)
            fg = (255, 255, 255) if enabled else (180, 180, 180)

            pygame.draw.rect(screen, bg, rect)
            opt = self.options[i]
            text = font.render(f"{opt.name} (${opt.cost})", True, fg)
            screen.blit(text, (rect.x + 5, rect.y + 5))
