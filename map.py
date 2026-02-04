import pygame

TILE_SIZE = 40  # smaller tile for bigger grid
GRID_WIDTH = 30
GRID_HEIGHT = 17

class GameMap:
    def __init__(self):
        self.buildable = [[True for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
        self.path_tiles = []

    def is_buildable(self, tile):
        x, y = tile
        return self.buildable[x][y] and (tile not in self.path_tiles)

    def is_traversable(self, tile):
        x, y = tile
        return self.buildable[x][y]

    def occupy_tile(self, tile):
        x, y = tile
        self.buildable[x][y] = False

    def set_path(self, path_tiles):
        self.path_tiles = path_tiles

    def draw(self, screen, path_tiles=None):
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                color = (50,50,50) if self.is_buildable((x,y)) else (80,80,80)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (30,30,30), rect, 1)
        if path_tiles:
            for x, y in path_tiles:
                rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, (0,100,255), rect)