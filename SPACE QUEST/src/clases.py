import pygame
from config import *
import random
import sqlite3
import tkinter as tk
from tkinter import simpledialog

# Cargar imágenes
player_image = pygame.image.load("./assets/player.png")
obstacle_image_1 = pygame.image.load("./assets/enemy_1.png")
obstacle_image_2 = pygame.image.load("./assets/enemy_2.png")
obstacle_image_3 = pygame.image.load("./assets/enemy_3.png")
obstacle_image_4 = pygame.image.load("./assets/enemy_4.png")
obstacle_image_5 = pygame.image.load("./assets/enemy_5.png")
obstacle_image_6 = pygame.image.load("./assets/enemy_6.png")
background_image_1 = pygame.image.load("./assets/bg_1.png")
background_image_2 = pygame.image.load("./assets/bg_2.png")
background_image_3 = pygame.image.load("./assets/bg_3.png")
planet_1 = pygame.image.load("./assets/planeta_1.png")
planet_2 = pygame.image.load("./assets/planeta_2.png")
planet_3 = pygame.image.load("./assets/planeta_3.png")
planet_4 = pygame.image.load("./assets/planeta_4.png")


# Datos
levels_data = [
    {"title": "Nivel 1", "speed": 2.5, "generation_interval": 2.0, "distance_min": 300, "distance_max": 500, "multiplicador":1},
    {"title": "Nivel 2", "speed": 3.0, "generation_interval": 1.5, "distance_min": 500, "distance_max": 800, "multiplicador":2},
    {"title": "Nivel 3", "speed": 5.0, "generation_interval": 1, "distance_min": 800, "distance_max": 1000, "multiplicador":3},
    {"title": "Nivel 4", "speed": 6.0, "generation_interval": .7, "distance_min": 1200, "distance_max": 2000, "multiplicador":4}
]

level_to_planet = {
        "Nivel 1": planet_1,
        "Nivel 2": planet_2,
        "Nivel 3": planet_3,
        "Nivel 4": planet_4,
    }


def get_background():
    backgrounds = [background_image_1, background_image_2, background_image_3]
    return random.choice(backgrounds)

def get_planet(level):
    return level_to_planet.get(level, planet_1)


def crear_tabla_puntuaciones():
    conn = sqlite3.connect('./src/puntuaciones.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS puntuaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jugador TEXT NOT NULL,
            puntuacion INTEGER NOT NULL,
            nivel INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def insertar_puntuacion(jugador, puntuacion, nivel):
    conn = sqlite3.connect('./src/puntuaciones.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO puntuaciones (jugador, puntuacion, nivel) VALUES (?, ?, ?)", (jugador, puntuacion, nivel))
    conn.commit()
    conn.close()

def obtener_mejores_puntuaciones(cantidad=10):
    conn = sqlite3.connect('./src/puntuaciones.db')
    cursor = conn.cursor()

    cursor.execute("SELECT jugador, puntuacion FROM puntuaciones ORDER BY puntuacion DESC LIMIT ?", (cantidad))
    mejores_puntuaciones = cursor.fetchall()

    conn.close()
    return mejores_puntuaciones

def obtener_high_scores():
    conn = sqlite3.connect('./src/puntuaciones.db')
    cursor = conn.cursor()
    cursor.execute("SELECT jugador, nivel, puntuacion FROM puntuaciones ORDER BY puntuacion DESC LIMIT 10")
    high_scores = cursor.fetchall()
    conn.close()

    return high_scores

def print_high_scores():
    conn = sqlite3.connect('./src/puntuaciones.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM puntuaciones ORDER BY puntuacion DESC LIMIT 10")
    
    rows = cursor.fetchall()

    print("{:<10} {:<20} {:<10} {:<10}".format("ID", "Jugador", "Puntuación", "Nivel"))
    
    for row in rows:
        print("{:<10} {:<20} {:<10} {:<10}".format(*row))

    conn.close()

def mostrar_ventana_modal():
    root = tk.Tk()
    root.withdraw()
    user_input = simpledialog.askstring("Input", "Nombre del jugador:")

    if user_input:
        if len(user_input) < 4:
            return user_input
        else:
            return mostrar_ventana_modal()
    else:
        return mostrar_ventana_modal()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.original_image = self.image.copy()
        
        self.rect = self.image.get_rect(center=(32, HEIGHT // 2))

        self.speed = 3
        self.invincible_timer = 0
        self.rotation_angle = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def rotate_player(self):
        self.image = pygame.transform.rotate(self.original_image, self.rotation_angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def rotate_animation(self):
        self.rotation_angle += 1
        self.rect.x += 5
        self.rotate_player() 
        self.invincible_timer = FPS   
        if self.rotation_angle >= 180:
            self.rotation_angle = 180
            
            return True 
        return False


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.random_image = random.choice([obstacle_image_1, obstacle_image_2, obstacle_image_3, obstacle_image_4,obstacle_image_5,obstacle_image_6])
        self.image = self.random_image
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        self.rect.y = random.randrange(HEIGHT - self.rect.height)
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed

class MainMenu:
    def __init__(self):
        self.font = pygame.font.Font(None, 64)
        self.play_text = self.font.render("Jugar", True, WHITE)
        self.play_rect = self.play_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.exit_text = self.font.render("Exit", True, WHITE)
        self.exit_rect = self.exit_text.get_rect(center=(WIDTH // 2, HEIGHT // 1.5))

    def display_menu(self, screen):
        screen.blit(background_image_2, (0, 0))

        self.draw_high_scores(screen)

        title_text = self.font.render("Space Quest", True, WHITE)

        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))

        screen.blit(title_text, title_rect)
        screen.blit(self.play_text, self.play_rect)
        screen.blit(self.exit_text, self.exit_rect)
    
    def draw_high_scores(self, screen):
        high_scores = obtener_high_scores()
        font = pygame.font.Font(None, 30)
        column_font = pygame.font.Font(None, 36)

        start_x, start_y = 10, 50
        space_between_scores = 40

        background_rect = pygame.Rect(start_x, start_y, 460, 600)
        pygame.draw.rect(screen, GRAY, background_rect)

        column_names = ["Jugador", "Nivel", "Puntuación"]
        for i, column_name in enumerate(column_names):
            name_surface = column_font.render(column_name, True, BLACK)
            name_rect = name_surface.get_rect(topleft=(start_x + i * 150, start_y))
            screen.blit(name_surface, name_rect)

        for i, (jugador, nivel, puntuacion) in enumerate(high_scores):
            name_text = f"{jugador:<15}"
            name_surface = font.render(name_text, True, BLACK)
            name_rect = name_surface.get_rect(topleft=(start_x, start_y + (i + 1) * space_between_scores))
            screen.blit(name_surface, name_rect)
            level_text = f"{nivel:<15}"
            level_surface = font.render(level_text, True, BLACK)
            level_rect = level_surface.get_rect(topleft=(start_x + 150, start_y + (i + 1) * space_between_scores))
            screen.blit(level_surface, level_rect)
            score_text = f"{puntuacion}"
            score_surface = font.render(score_text, True, BLACK)
            score_rect = score_surface.get_rect(topleft=(start_x + 300, start_y + (i + 1) * space_between_scores))
            screen.blit(score_surface, score_rect)







class LevelSelector:
    def __init__(self, levels):
        self.levels = levels
        self.selected_level = None
        self.font = pygame.font.Font(None, 36)
        self.buttons = []

        self.create_buttons()

    def create_buttons(self):
        button_height = 50
        vertical_spacing = 16

        for index, level in enumerate(self.levels, start=1):
            button_rect = pygame.Rect(WIDTH // 2 - 100, 100 + (index - 1) * (button_height + vertical_spacing), 200, button_height)
            button_text = self.font.render(level["title"], True, BLACK)
            text_rect = button_text.get_rect(center=button_rect.center)

            self.buttons.append((button_rect, button_text, level))

    def draw(self, screen):
        screen.blit(background_image_3, (0, 0))

        for button in self.buttons:
            pygame.draw.rect(screen, LIGHT_GRAY, button[0])
            screen.blit(button[1], button[1].get_rect(center=button[0].center))

    def handle_events(self):
        selecting_level = True

        while selecting_level:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons:
                        if button[0].collidepoint(event.pos):
                            self.selected_level = button[2]
                            selecting_level = False





class GameOverMenu:
    def __init__(self):
        self.font = pygame.font.Font(None, 64)
        self.retry_text = self.font.render("Volver al menú", True, WHITE)
        self.retry_rect = self.retry_text.get_rect(center=(WIDTH // 2, HEIGHT * 3 // 4))

    def display_game_over(self, screen, lives, score, distance, target_distance):
        screen.blit(background_image_3, (0, 0))
        game_over_text = self.font.render("Game Over", True, WHITE)
        lives_text = self.font.render(f"Vidas restantes: {max(lives, 0)}/3", True, WHITE)
        score_text = self.font.render(f"Puntos: {score}p", True, WHITE)
        distance_text = self.font.render(f"Distancia recorrida: {distance} km", True, WHITE)
        target_distance_text = self.font.render(f"Distancia objetivo: {target_distance} km", True, WHITE)

        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        lives_rect = lives_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 75))
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 25))
        distance_rect = distance_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25))
        target_distance_rect = target_distance_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 75))

        screen.blit(game_over_text, game_over_rect)
        screen.blit(lives_text, lives_rect)
        screen.blit(score_text, score_rect)
        screen.blit(distance_text, distance_rect)
        screen.blit(target_distance_text, target_distance_rect)
        screen.blit(self.retry_text, self.retry_rect)

        pygame.display.flip()

        return self.retry_rect

class WinGameMenu:
    def __init__(self):
        self.font = pygame.font.Font(None, 32)
        self.win_text = self.font.render("¡Felicidades, Ganaste!", True, WHITE)
        self.score_text = self.font.render("Puntos: {score}p", True, WHITE)
        self.return_text = self.font.render("Volver al menú", True, WHITE)
        self.return_rect = self.return_text.get_rect(center=(WIDTH // 2, HEIGHT // 1.5))

        self.add_score_button_visible = False
        self.add_score_button_rect = pygame.Rect(WIDTH - 250, HEIGHT // 2 - 25, 200, 50)
        self.add_score_text = self.font.render("Agregar Puntuación", True, BLACK)

    def display_win_game(self, screen, lives, score, distance, level, high_scores):
        screen.blit(background_image_1, (0, 0))
        win_text_rect = self.win_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        score_text_rect = self.score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.score_text = self.font.render(f"Puntos: {score}p", True, WHITE)
        screen.blit(self.win_text, win_text_rect)
        screen.blit(self.score_text, score_text_rect)
        screen.blit(self.return_text, self.return_rect)

        
        if self.score_is_high_score(score, high_scores):
            self.draw_add_score_button(screen)

        pygame.display.flip()
        return self.return_rect

    def score_is_high_score(self, score, high_scores):
        if not high_scores or len(high_scores) < 10:
            return True  
        return score > min(high_scores)


    def draw_add_score_button(self, screen):
        pygame.draw.rect(screen, LIGHT_GRAY, self.add_score_button_rect)
        screen.blit(self.add_score_text, self.add_score_button_rect.move(5, 5))

    def insertar_puntuacion(self, jugador, puntuacion, nivel):
       
        conn = sqlite3.connect('./src/puntuaciones.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO puntuaciones (jugador, puntuacion, nivel) VALUES (?, ?, ?)", (jugador, puntuacion, nivel))
        conn.commit()
        conn.close()


# Clase para el juego
class Game:
    def __init__(self):
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)
        self.lives = 3
        self.clock = pygame.time.Clock()
        self.score = 0
        self.distance_target = random.randint(50, 100)
        self.distance_covered = 0
        self.obstacle_speed = 3.0
        self.obstacle_spawn_timer = 0
        self.obstacle_generation_interval = 2.0
        self.background = get_background()
        self.planeta = get_planet("Nivel 1")
        self.level = ""
        self.multiplicador = 1

    def set_level_parameters(self, level_data):
        self.distance_target = random.randint(level_data.get("distance_min", 600), level_data.get("distance_max", 800))
        self.obstacle_speed = level_data.get("speed", 3.0)
        self.obstacle_generation_interval = level_data.get("generation_interval", 2.0)
        self.planeta = get_planet(level_data.get("title", "Nivel 1"))
        self.level = level_data.get("title", "Nivel 1")
        self.multiplicador = level_data.get("multiplicador", 1)

    def start_game(self, screen):
        running = True
        running_time = 0

        rotation_animation_started = False

        wait_time_after_rotation = 0

        game_win = False

        while running and self.lives > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and self.player.rect.top > 0:
                self.player.rect.y -= self.player.speed
            if keys[pygame.K_DOWN] and self.player.rect.bottom < HEIGHT:
                self.player.rect.y += self.player.speed

            if self.player.invincible_timer > 0 and not rotation_animation_started:
                self.player.invincible_timer -= 1
                if self.player.invincible_timer % 10 < 5:
                    self.player.image.set_alpha(0)
                else:
                    self.player.image.set_alpha(255)
            else:
                self.player.image.set_alpha(255)

            self.all_sprites.update()

            # Colisiones
            hits = pygame.sprite.spritecollide(self.player, self.obstacles, True)
            if hits:
                if self.player.invincible_timer == 0:
                    self.lives -= 1
                    self.player.invincible_timer = FPS
            else:
                # Incrementar puntuación por cada segundo
                running_time += 1
                if running_time % FPS == 0:
                    self.score += 5

            # Generar obstáculos aleatorios
            if self.obstacle_spawn_timer <= 0:
                if not rotation_animation_started and not game_win:
                    self.generate_obstacles()
                self.obstacle_spawn_timer = self.obstacle_generation_interval

            self.obstacle_spawn_timer -= 1 / FPS

            for obstacle in self.obstacles:
                if obstacle.rect.right < 0:
                    self.score += 2 
                    obstacle.kill()

            if running_time % FPS == 0:
                self.distance_covered += 10

            if self.distance_covered >= self.distance_target and not rotation_animation_started:
                rotation_animation_started = True
                self.player.speed = 0
                self.player.rect.centery = HEIGHT // 2

            if rotation_animation_started and self.player.rotation_angle < 180:
                if self.player.rotate_animation():
                    wait_time_after_rotation = FPS * 2
                    rotation_animation_started = False
                    game_win = True
                    self.score += 200
            else:
                if wait_time_after_rotation > 0:
                    wait_time_after_rotation -= 1
                else:
                    if game_win:
                        running  = False


            # Renderizar y refrescar pantalla
            screen.blit(self.background, (0, 0))

            if rotation_animation_started or game_win:
                screen.blit(self.planeta, (WIDTH - (self.planeta.get_width()//2), HEIGHT // 2 - self.planeta.get_height() // 2))

            self.all_sprites.draw(screen)

            font = pygame.font.Font(None, 36)
            lives_text = font.render(f"Vidas: {max(self.lives, 0)}/3", True, WHITE)
            screen.blit(lives_text, (10, 10))

            score_text = font.render(f"Puntos: {self.score}p", True, WHITE)
            screen.blit(score_text, (WIDTH - 150, 10))

            distance_target_text = font.render(f"Objetivo: {self.distance_target} km", True, WHITE)
            screen.blit(distance_target_text, (WIDTH // 2 - 80, 10))

            distance_covered_text = font.render(f"Recorrido: {self.distance_covered} km", True, WHITE)
            screen.blit(distance_covered_text, (WIDTH // 2 - 80, 50))

            pygame.display.flip()

            # Controlar la velocidad del juego
            self.clock.tick(FPS)


        if game_win:
            puntuacion_final = self.score + self.multiplicador*100
            win_game_menu = WinGameMenu()
            return_rect = win_game_menu.display_win_game(screen, self.lives, puntuacion_final, self.distance_covered, self.level, obtener_high_scores())
            pygame.display.flip()

            waiting_for_input = True
            while waiting_for_input:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        
                        if return_rect.collidepoint(event.pos):
                            waiting_for_input = False
                            running = False
                        elif win_game_menu.add_score_button_rect.collidepoint(event.pos):
                            waiting_for_input = False
                            win_game_menu.insertar_puntuacion(mostrar_ventana_modal(), puntuacion_final, self.level)
                            running = False
                        
                    elif event.type == pygame.QUIT:
                        waiting_for_input = False
                        running = False
                pygame.time.delay(50)

            self.reset_game()
        else:
            # Pantalla de Game Over
            game_over_menu = GameOverMenu()
            retry_rect = game_over_menu.display_game_over(screen, self.lives, self.score, self.distance_covered, self.distance_target)
            pygame.display.flip()
            waiting_for_input = True
            while waiting_for_input:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN and retry_rect.collidepoint(event.pos):
                        waiting_for_input = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        waiting_for_input = False
                        running = False
                    elif event.type == pygame.QUIT:
                        waiting_for_input = False
                        running = False
                pygame.time.delay(50)
            # Reinicia las instancias del juego para volver al menú principal
            self.reset_game()

    def generate_obstacles(self):
        num_obstacles = random.choices([1, 2, 3, 4], weights=[0.3, 0.4, 0.2, 0.1])[0]

        for _ in range(num_obstacles):
            obstacle_speed = self.obstacle_speed + random.uniform(0, 1)
            obstacle = Obstacle(obstacle_speed)
            self.all_sprites.add(obstacle)
            self.obstacles.add(obstacle)

    def reset_game(self):
        self.all_sprites.empty()
        self.obstacles.empty()
        self.player = Player()
        self.all_sprites.add(self.player)
        self.lives = 3
        self.score = 0
        self.distance_target = random.randint(600, 800)
        self.distance_covered = 0
        self.obstacle_speed = 3.0
        self.obstacle_spawn_timer = 0
        self.obstacle_generation_interval = 2.0
        self.background = get_background()

