import sys
from random import choice, randint

import pygame

from settings import *



class Shooter(pygame.sprite.DirtySprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)

        self.pos = pos
        self.speed = 10
        # self.spawn_bullets = False

        self.image = pygame.image.load('images/shooter.png').convert_alpha()
        self.rect = self.image.get_rect(center=self.pos)

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 10: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH-10: self.rect.x += self.speed

        # if keys[pygame.K_SPACE]:
        #     self.spawn_bullets = True
        # else:
        #     self.spawn_bullets = False

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
        self.speed = randint(2, 4)

        self.image = choice(asteroids_images)
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
        self.clock = pygame.time.Clock()
        self.spawn_bullets = pygame.USEREVENT + 1
        pygame.time.set_timer(self.spawn_bullets, 200)

        self.spawn_asteroids = pygame.USEREVENT + 2
        pygame.time.set_timer(self.spawn_asteroids, 200)

        self.bg = pygame.image.load('images/bg.jpg').convert()
        self.bg = pygame.transform.scale(self.bg, (600, 800))

        self.all_sprites = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        self.player = Shooter((SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50), self.all_sprites)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    Bullet((self.player.rect.centerx, self.player.rect.top), self.all_sprites, self.bullets)
                if event.type == self.spawn_asteroids:
                    Asteroid(self.asteroids, self.all_sprites)

            self.screen.blit(self.bg, (0, 0))

            self.all_sprites.draw(self.screen)
            self.all_sprites.update()

            pygame.display.flip()

            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()