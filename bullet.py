import pygame
import math
import os

RESOURCES_PATH = os.path.join(os.path.dirname(__file__), "resources")

class Bullet:
    def __init__(self, x, y, target, damage):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = 8  
        self.alive = True

        image_path = os.path.join(RESOURCES_PATH, "Bullet_Rainbow1_PuftDank02.png")
        
        try:
            self.original_image = pygame.image.load(image_path).convert_alpha()
        except pygame.error as e:
            print(f"Could not load bullet image: {e}")
            self.original_image = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, (255, 255, 0), (8, 8), 8)

        desired_width = 24
        aspect_ratio = self.original_image.get_height() / self.original_image.get_width()
        new_height = int(desired_width * aspect_ratio)
        self.original_image = pygame.transform.smoothscale(self.original_image, (desired_width, new_height))

        self.image = self.original_image 
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

        self.angle = 0

    def move(self):
        if not self.target.alive:
            self.alive = False
            return 0

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)

        if dist <= self.speed:
            self.alive = False
            return self.target.take_damage(self.damage)

        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed

        self.angle = math.degrees(math.atan2(dy, dx))

        self.image = pygame.transform.rotate(self.original_image, -self.angle)  # - because pygame rotates CCW
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

        return 0

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

  