import pygame

class Enemy:
    def __init__(self, enemy_type, path, wave=1):
        self.type = enemy_type
        self.path = path
        self.index = 0
        self.x, self.y = self.path[0]

        # Enemy stats
        if enemy_type == 1:
            self.max_hp = 25
            self.speed = 1.2
            image_path = "resources/Enemy_Cone Idle_01.png"  # Green enemy
            self.reward = 10
        elif enemy_type == 2:
            self.max_hp = 45
            self.speed = 0.9
            image_path = "resources/Enemy_Yellow_Idle01.png"  # Yellow enemy
            self.reward = 15
        elif enemy_type == 3:
            self.max_hp = 70
            self.speed = 0.7
            image_path = "resources/Trooper01_Idle01.png"    # Red enemy
            self.reward = 25
        else:
            raise ValueError("Invalid enemy type")

        self.health = self.max_hp

        # Smooth wave scaling (logical and controlled)
        hp_multiplier = 1.0 + 0.08 * (wave - 1)  # +10% HP per wave
        speed_multiplier = 1.0 + 0.02 * (wave - 1)  # +3% speed per wave

        self.max_hp = int(self.max_hp * hp_multiplier)
        self.health = self.max_hp
        self.speed *= speed_multiplier

        self.alive = True
        self.reached_end = False


        # Load and prepare image (preserve aspect ratio)
        try:
            original_image = pygame.image.load(image_path).convert_alpha()
        except pygame.error:
            print(f"Could not load image: {image_path}")
            original_image = pygame.Surface((40, 40), pygame.SRCALPHA)
            original_image.fill((255, 0, 255))  # Magenta fallback

        # Scale image to desired size while preserving aspect ratio
        desired_width = 70  # Adjust this size as needed for your game
        scale_factor = desired_width / original_image.get_width()
        new_height = int(original_image.get_height() * scale_factor)
        self.image = pygame.transform.smoothscale(original_image, (desired_width, new_height))

        # Store image dimensions for centering
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def move(self):
        if self.index >= len(self.path) - 1:
            self.reached_end = True
            self.alive = False
            return

        move_left = self.speed

        while move_left > 0 and self.index < len(self.path) - 1:
            target_x, target_y = self.path[self.index + 1]
            dx = target_x - self.x
            dy = target_y - self.y
            dist = (dx * dx + dy * dy) ** 0.5

            if dist == 0:
                self.index += 1
                continue

            if dist <= move_left:
                # consume remaining distance to reach waypoint
                self.x, self.y = target_x, target_y
                self.index += 1
                move_left -= dist
            else:
                # move partially toward waypoint
                self.x += (dx / dist) * move_left
                self.y += (dy / dist) * move_left
                move_left = 0

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            return self.reward  # Reward for killing
        return 0

    def draw(self, screen):
        # Draw the enemy image centered at (self.x, self.y)
        offset_x = self.width // 2
        offset_y = self.height // 2
        screen.blit(self.image, (self.x - offset_x, self.y - offset_y))

        # Draw health bar above the enemy
        bar_width = 40
        bar_height = 6
        bar_x = self.x - bar_width // 2
        bar_y = self.y - offset_y - 10  # 10 pixels above the enemy

        # Background (red)
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        # Foreground (green)
        health_ratio = max(0, self.health / self.max_hp)
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
        # Border
        pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 2)

    def max_health(self):
        return self.max_hp

def create_enemy(enemy_type, path, wave=1):
    return Enemy(enemy_type, path, wave)