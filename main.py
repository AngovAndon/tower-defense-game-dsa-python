import pygame
from structures import Queue, Stack
from enemy import create_enemy
from tower import create_tower
from map import GameMap, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT
from scores import load_scores, save_score
from build_menu import BuildMenu
from graph import generate_path, path_to_pixels
from tower_menu import TowerMenu
import random
pygame.init()
pygame.mixer.init()


pygame.mixer.music.load("resources/CaveBeast.mp3")
pygame.mixer.music.set_volume(1.0)  
pygame.mixer.music.play(-1)          


SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense - Smooth Path")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 26)

MENU, GAME, LEADERBOARD, GAME_OVER = 0, 1, 2, 3
state = MENU

enemy_queue = Queue()
tower_stack = Stack()
game_map = GameMap()
build_menu = None
pending_tile = None

selected_tower = None
show_range = False
tower_menu = None

coins = 200
score = 0
health = 20

wave = 1
MAX_WAVES = 5

towers = []
enemies = []
bullets = []

current_path_tiles = []
current_path_pixels = []

spawn_timer = 0
spawn_interval = 30  # frames @60fps = 0.30 seconds between spawns

SPAWN_GAP_PIXELS = 24

# ------------------- WAVE SYSTEM -------------------
def start_wave(wave_number):
    global current_path_tiles, current_path_pixels
    global spawn_timer, spawn_interval

    global selected_tower, show_range, tower_menu
    selected_tower = None
    show_range = False
    tower_menu = None

    enemy_queue.clear()
    enemies.clear()
    spawn_timer = 0
    spawn_interval = max(20, 36 - wave_number)  # slightly faster spawns in later waves

    # Blocked tiles = all towers placed so far (from previous waves too)
    blocked = {t.tile for t in towers}

    # Try multiple times because start/end are random and can fail
    current_path_tiles = None
    for _ in range(80):
        current_path_tiles = generate_path(blocked)
        if current_path_tiles:
            break

    if not current_path_tiles:
        # If it fails (rare), keep previous path and just continue
        return

    game_map.set_path(current_path_tiles)
    current_path_pixels = path_to_pixels(current_path_tiles, TILE_SIZE)

    enemy_count = 5 + wave_number * 3

    enemy_types = []
    for i in range(enemy_count):
        enemy_type = min(3, (i // 3) + 1)
        enemy_types.append(enemy_type)

    random.shuffle(enemy_types)

    for enemy_type in enemy_types:
        enemy_queue.enqueue(create_enemy(enemy_type, current_path_pixels, wave_number))



# ------------------- RESET GAME -------------------
def reset_game():
    global coins, score, health, wave
    global towers, bullets, enemies, enemy_queue, tower_stack
    global current_path_tiles, current_path_pixels, build_menu, pending_tile
    global selected_tower, show_range, tower_menu
    global game_map  # <-- IMPORTANT

    coins = 200
    score = 0
    health = 20
    wave = 1

    towers = []
    bullets = []
    enemies = []

    tower_stack.clear()
    enemy_queue.clear()

    build_menu = None

    selected_tower = None
    show_range = False
    tower_menu = None

    pending_tile = None

    game_map = GameMap()  # <-- now it truly resets the global map
    current_path_tiles = []
    current_path_pixels = []

    start_wave(wave)

# ------------------- DRAW PATH -------------------
def draw_path(screen, path_pixels):
    if len(path_pixels) >= 2:
        pygame.draw.lines(screen, (0,150,255), False, path_pixels, 6)

# ------------------- MAIN LOOP -------------------
running = True
while running:
    screen.fill((30,30,30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # -------- MENU --------
        if state == MENU and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                reset_game()
                state = GAME
            elif event.key == pygame.K_l:
                state = LEADERBOARD

            elif event.key == pygame.K_q:
                running = False
            
        # -------- LEADERBOARD --------
        elif state == LEADERBOARD and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                state = MENU

        # -------- GAME OVER --------
        elif state == GAME_OVER and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                state = MENU

        # -------- GAME --------
        elif state == GAME:
            # --- UNDO LAST TOWER (STACK POP) ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    last = tower_stack.pop()
                    if last is not None:

                        # remove from active towers list (source of truth)
                        if last in towers:
                            towers.remove(last)

                        # free the tile (becomes buildable again)
                        tx, ty = last.tile
                        game_map.buildable[tx][ty] = True

                        # refund 60% (same rule as selling)
                        coins += int(last.cost * 0.6)

                        # if undo removed the selected tower, close its menu
                        if selected_tower == last:
                            selected_tower = None
                            tower_menu = None
                            show_range = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                clicked_tile = (mx // TILE_SIZE, my // TILE_SIZE)

                # 1) If tower menu is open, handle it first
                if tower_menu and selected_tower:
                    action = tower_menu.handle_click((mx, my))

                    if action == "toggle_range":
                        show_range = not show_range

                    elif action == "sell":
                        coins += tower_menu.refund

                        # free tile
                        game_map.buildable[selected_tower.tile[0]][selected_tower.tile[1]] = True

                        # remove from towers list
                        if selected_tower in towers:
                            towers.remove(selected_tower)

                        # remove from stack so undo doesn't bring it back
                        if selected_tower in tower_stack.items:
                            tower_stack.items.remove(selected_tower)

                        # clear selection/menu
                        selected_tower = None
                        tower_menu = None
                        show_range = False

                        build_menu = None
                        pending_tile = None

                    elif action == "outside":
                        # close menu if clicked outside
                        tower_menu = None

                # 2) If build_menu is open, handle buying (your existing code)
                elif build_menu:
                    choice = build_menu.handle_click((mx, my), coins)
                    if choice and pending_tile:
                        tower = create_tower(
                            choice,
                            pending_tile[0] * TILE_SIZE + TILE_SIZE // 2,
                            pending_tile[1] * TILE_SIZE + TILE_SIZE // 2,
                            pending_tile
                        )
                        if coins >= tower.cost:
                            coins -= tower.cost
                            towers.append(tower)
                            tower_stack.push(tower)
                            game_map.buildable[pending_tile[0]][pending_tile[1]] = False

                    build_menu = None
                    pending_tile = None

                # 3) Otherwise: click tower -> open tower menu, else open build menu like normal
                else:
                    clicked = None
                    for t in towers:
                        if t.tile == clicked_tile:
                            clicked = t
                            break

                    if clicked:
                        selected_tower = clicked
                        show_range = False
                        tower_menu = TowerMenu(
                            min(mx, SCREEN_WIDTH - 230),
                            min(my, SCREEN_HEIGHT - 90),
                            clicked
                        )
                    else:
                        selected_tower = None
                        tower_menu = None
                        show_range = False

                        if game_map.is_buildable(clicked_tile):
                            build_menu = BuildMenu(min(mx, SCREEN_WIDTH - 160), min(my, SCREEN_HEIGHT - 120))
                            pending_tile = clicked_tile

    # ------------------- DRAW STATES -------------------
    if state == MENU:
        screen.blit(font.render("TOWER DEFENSE", True, (255,255,255)), (SCREEN_WIDTH//2-100, 200))
        screen.blit(font.render("ENTER - Start", True, (200,200,200)), (SCREEN_WIDTH//2-80, 250))
        screen.blit(font.render("L - Leaderboard", True, (200,200,200)), (SCREEN_WIDTH//2-80, 290))
        screen.blit(font.render("Q - Quit Game", True, (200,200,200)), (SCREEN_WIDTH//2-80, 330))


    elif state == GAME:
        game_map.draw(screen)
        draw_path(screen, current_path_pixels)

        # spawn enemies (timed + entrance gating)
        spawn_timer += 1
        if spawn_timer >= spawn_interval and not enemy_queue.is_empty():
            sx, sy = current_path_pixels[0]

            # Find the enemy closest to the start (lowest index, then nearest distance)
            def d2_to_start(e):
                dx = e.x - sx
                dy = e.y - sy
                return dx * dx + dy * dy

            entrance_clear = True
            if enemies:
                closest = min(enemies, key=lambda e: (e.index, d2_to_start(e)))
                if d2_to_start(closest) < (SPAWN_GAP_PIXELS * SPAWN_GAP_PIXELS):
                    entrance_clear = False

            if entrance_clear:
                spawn_timer = 0
                e = enemy_queue.dequeue()
                e.x, e.y = sx, sy
                e.index = 0
                enemies.append(e)
            else:
                # keep trying next frame (don't reset timer so it spawns ASAP when clear)
                spawn_timer = spawn_interval

        # update enemies
        for enemy in enemies[:]:
            enemy.move()
            if enemy.reached_end:
                health -= 1
                enemies.remove(enemy)
            elif not enemy.alive:
                enemies.remove(enemy)

        # towers shoot
        for tower in towers:
            tower.shoot(enemies, bullets)

        # bullets
        for bullet in bullets[:]:
            reward = bullet.move()
            if reward:
                coins += reward
                score += reward
            if not bullet.alive:
                bullets.remove(bullet)

        # draw entities
        for enemy in enemies:
            enemy.draw(screen)
        for tower in towers:
            tower.draw(
                screen,
                show_range=(tower is selected_tower and show_range)
            )
        for bullet in bullets:
            bullet.draw(screen)

        if build_menu:
            build_menu.draw(screen, font, coins)

        if tower_menu and selected_tower:
            tower_menu.draw(screen, font, show_range_now=show_range)

        # UI
        ui_text = f"Health: {health}   Coins: {coins}   Score: {score}   Wave: {wave}/{MAX_WAVES}"
        screen.blit(font.render(ui_text, True, (255,255,255)), (10,10))

        # GAME OVER
        if health <= 0:
            save_score(score)
            state = GAME_OVER

        # NEXT WAVE
        if enemy_queue.is_empty() and not enemies:
            if wave < MAX_WAVES:
                wave += 1
                start_wave(wave)
            else:
                save_score(score)
                state = LEADERBOARD

    elif state == GAME_OVER:
        screen.blit(font.render("GAME OVER", True, (255,80,80)), (SCREEN_WIDTH//2-80, SCREEN_HEIGHT//2-50))
        screen.blit(font.render("Press ENTER to return to menu", True, (200,200,200)), (SCREEN_WIDTH//2-130, SCREEN_HEIGHT//2-10))

    elif state == LEADERBOARD:
        screen.blit(font.render("LEADERBOARD", True, (255,255,255)), (SCREEN_WIDTH//2-80, 150))
        scores = load_scores()
        for i, s in enumerate(scores):
            screen.blit(font.render(f"{i+1}. {s}", True, (200,200,200)), (SCREEN_WIDTH//2-50, 200 + i*30))
        screen.blit(font.render("ESC - Back", True, (180,180,180)), (SCREEN_WIDTH - 500, 150))

    pygame.display.update()
    clock.tick(60)

pygame.quit()