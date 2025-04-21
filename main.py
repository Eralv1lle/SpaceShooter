import sys
from random import choice, randint, uniform

import pygame.transform

from settings import *


def draw_text(text, size, color, pos, surf: pygame.Surface, direction='topleft'):
    font = pygame.font.Font(None, size)
    text_surf = font.render(text, True, color)

    if direction == 'center':
        text_rect = text_surf.get_rect(center=pos)
    else:
        text_rect = text_surf.get_rect(topleft=pos)
    surf.blit(text_surf, text_rect)


class Shooter(pygame.sprite.DirtySprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)

        self.pos = pos
        self.speed = 10
        self.health = 3
        self.score = 0
        self.collected_boosts = 0

        self.image = pygame.image.load('images/shooter.png').convert_alpha()
        self.rect = self.image.get_rect(center=self.pos)

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 10: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH-10: self.rect.x += self.speed

    def update(self):
        self.move()


class Bullet(pygame.sprite.DirtySprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)

        self.pos = pos
        self.speed = 5

        self.image = pygame.image.load('images/bullet.png').convert_alpha()
        self.rect = self.image.get_rect(center=self.pos)

    def move(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

    def update(self):
        self.move()

class Asteroid(pygame.sprite.DirtySprite):
    def __init__(self, *groups):
        super().__init__(*groups)

        self.speed = 5
        self.direction = uniform(-0.3, 0.3)
        self.image = choice(asteroids_images)
        self.rect = self.image.get_rect(topleft=(randint(0, SCREEN_WIDTH - self.image.get_width()), -self.image.get_height() - 100))

    def move(self):
        self.rect.y += self.speed
        self.rect.x += self.speed * self.direction
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction = -self.direction
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def update(self):
        self.move()


class Boost(pygame.sprite.DirtySprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.speed = randint(3, 5)
        self.type = choice(['health', 'protect'])

        if self.type == 'health':
            self.image = pygame.image.load('images/health_boost.jpg').convert_alpha()
        else:
            self.image = pygame.image.load('images/protect_boost.jpg').convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))

        self.rect = self.image.get_rect(topleft=(randint(0, SCREEN_WIDTH - self.image.get_width()), -self.image.get_height() - 100))

    def move(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def update(self):
        self.move()

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('SpaceShooter')
        self.running = True
        self.game_over = False
        self.clock = pygame.time.Clock()

        self.spawn_asteroids = pygame.USEREVENT + 1
        pygame.time.set_timer(self.spawn_asteroids, 500)

        self.spawn_boosts = pygame.USEREVENT + 2
        pygame.time.set_timer(self.spawn_boosts, randint(5000, 15000))

        self.bg = pygame.image.load('images/bg.jpg').convert()
        self.bg = pygame.transform.scale(self.bg, (600, 800))

        self.all_sprites = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.boosts = pygame.sprite.Group()

        self.player = Shooter((SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100), self.all_sprites)
        self.best_score = 0
        self.heart = pygame.image.load('images/heart.png')
        self.heart = pygame.transform.scale(self.heart, (60, 60))

        self.protect = pygame.image.load('images/protect.png')
        self.protect = pygame.transform.scale(self.protect, (150, 150))
        self.protect_rect = self.protect.get_rect()
        self.stop_protect = 0
        self.start_protect = False

    def setup_protect(self):
        self.screen.blit(self.protect, (self.player.rect.x - 34, self.player.rect.y - 36))

    def restart_game(self):
        self.game_over = False
        self.player = Shooter((SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100), self.all_sprites)
        self.stop_protect = 0
        self.start_protect = False

    def check_collisions(self):
        for _ in pygame.sprite.groupcollide(self.asteroids, self.bullets, True, True, collided=pygame.sprite.collide_mask):
            self.player.score += 1

        for _ in pygame.sprite.spritecollide(self.player, self.asteroids, True, collided=pygame.sprite.collide_mask):
            self.player.health -= 1 if not self.start_protect else 0
            if self.player.health == 0:
                if self.player.score > self.best_score:
                    self.best_score = self.player.score
                self.player.kill()
                self.asteroids.empty()
                self.bullets.empty()
                self.boosts.empty()
                self.all_sprites.empty()
                self.game_over = True

        for boost in pygame.sprite.spritecollide(self.player, self.boosts, True, collided=pygame.sprite.collide_mask):
            self.player.collected_boosts += 1
            if boost.type == 'health':
                if self.player.health < 3:
                    self.player.health += 1
            else:
                self.stop_protect = pygame.time.get_ticks() + 5000
                self.start_protect = True

    def write_text(self):
        if not self.game_over:
            draw_text(f'Score: {self.player.score}', 50, 'white', (10, 10), self.screen)
            draw_text(f'Best Score: {self.best_score}', 40, 'white', (10, 50), self.screen)
            draw_text(f'Health:', 50, 'white', (430, 10), self.screen)
        else:
            draw_text(f'Game Over!', 100, 'white', (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 70), self.screen, 'center')
            draw_text(f'Final score: {self.player.score}', 50, 'white', (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), self.screen, 'center')
            draw_text(f'Collected boosts: {self.player.collected_boosts}', 50, 'white', (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50), self.screen, 'center')
            draw_text(f'To restart press R', 50, 'white', (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100), self.screen, 'center')

        if self.start_protect:
            draw_text(f'Protect: {round((self.stop_protect - pygame.time.get_ticks()) / 1000, 2)}', 50, 'white', (10, SCREEN_HEIGHT - 70), self.screen)

    def draw_lives(self):
        x = 400
        for _ in range(self.player.health):
            self.screen.blit(self.heart, (x, 40))
            x += 60

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.game_over:
                        Bullet((self.player.rect.centerx, self.player.rect.top), self.all_sprites, self.bullets)
                    if event.key == pygame.K_r and self.game_over:
                        self.restart_game()
                if event.type == self.spawn_asteroids and not self.game_over:
                    Asteroid(self.asteroids, self.all_sprites)
                if event.type == self.spawn_boosts and not self.game_over:
                    Boost(self.boosts, self.all_sprites)
                    pygame.time.set_timer(self.spawn_boosts, randint(5000, 15000))

            self.screen.blit(self.bg, (0, 0))

            if self.start_protect:
                self.setup_protect()
                if pygame.time.get_ticks() > self.stop_protect:
                    self.start_protect = False
                    self.stop_protect = 0

            self.check_collisions()
            self.write_text()
            self.draw_lives()
            self.all_sprites.draw(self.screen)
            self.all_sprites.update()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()