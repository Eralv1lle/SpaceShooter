import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 600, 800

asteroids_images = []

for i in range(1, 16):
    asteroids_images.append(pygame.image.load(f'images/asteroids/asteroid{i}.png'))
print(asteroids_images)