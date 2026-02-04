import pygame
import math
import os
from bullet import Bullet

# Correct path to resources
RESOURCES_PATH = os.path.join(os.path.dirname(__file__), "resources")

class Tower:
    sprites = {}          # Class-level storage for scaled sprites
    shoot_sound = None    # Class-level sound (loaded once)

    def __init__(self, tower_type, x, y, tile):
        self.type = tower_type
        self.x = x
        self.y = y
        self.tile = tile
        self.range = 100
        self.damage = 10
        self.fire_rate = 60
        self.cost = 0
        self.timer = 0
        self.angle = 0

        # -------------------------
        # Tower stats by type
        # -------------------------
        if tower_type == "Bazooka":
            self.damage = 10
            self.range = 100
            self.cost = 50
            self.fire_rate = 60
        elif tower_type == "Sniper":
            self.damage = 25
            self.range = 200
            self.cost = 100
            self.fire_rate = 90
        elif tower_type == "Shotgun":
            self.damage = 5
            self.range = 80
            self.cost = 150
            self.fire_rate = 45
        else:
            raise ValueError(f"Unknown tower type: {tower_type}")

        # -------------------------
        # Load sound ONCE
        # -------------------------
        if Tower.shoot_sound is None:
            try:
                Tower.shoot_sound = pygame.mixer.Sound(
                    os.path.join(RESOURCES_PATH, "laser.mp3")
                )
                Tower.shoot_sound.set_volume(0.4)
            except pygame.error as e:
                print(f"Error loading laser sound: {e}")
                Tower.shoot_sound = None

        # -------------------------
        # Load and scale sprite ONCE per type
        # -------------------------
        if self.type not in Tower.sprites:
            if self.type == "Bazooka":
                img_path = os.path.join(RESOURCES_PATH, "BazookaEnergyx2_01.png")
            elif self.type == "Sniper":
                img_path = os.path.join(RESOURCES_PATH, "Sniper 01.png")
            elif self.type == "Shotgun":
                img_path = os.path.join(RESOURCES_PATH, "Shotgun Idle.png")

            try:
                raw_image = pygame.image.load(img_path).convert_alpha()
            except pygame.error as e:
                print(f"Error loading tower image {img_path}: {e}")
                raw_image = pygame.Surface((80, 80), pygame.SRCALPHA)
                raw_image.fill((128, 128, 128))

            # Scale (bigger than tiles, keep aspect ratio)
            orig_w, orig_h = raw_image.get_size()
            desired_width = 80
            scale_factor = desired_width / orig_w
            new_height = int(orig_h * scale_factor)

            Tower.sprites[self.type] = pygame.transform.smoothscale(
                raw_image, (desired_width, new_height)
            )

        self.original_sprite = Tower.sprites[self.type]

    # -------------------------
    # Shooting logic
    # -------------------------
    def shoot(self, enemies, bullets):
        self.timer += 1
        if self.timer < self.fire_rate:
            return
        self.timer = 0

        for enemy in enemies:
            distance = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if distance <= self.range:
                dx = enemy.x - self.x
                dy = enemy.y - self.y
                self.angle = math.degrees(math.atan2(dy, dx))

                bullets.append(Bullet(self.x, self.y, enemy, self.damage))

                # 🔊 Play sound
                if Tower.shoot_sound:
                    Tower.shoot_sound.play()

                break

    # -------------------------
    # Draw tower
    # -------------------------
    def draw(self, screen, show_range=False):
        rotated_sprite = pygame.transform.rotate(
            self.original_sprite, -self.angle
        )
        rect = rotated_sprite.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated_sprite, rect)

        if show_range:
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (int(self.x), int(self.y)),
                self.range,
                2
            )


def create_tower(tower_type, x, y, tile):
    return Tower(tower_type, x, y, tile)
