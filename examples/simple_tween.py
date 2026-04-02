import transytion as ty
from dataclasses import dataclass
from transytion.ease_funcs import quad
import pygame


pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

@dataclass
class Ball:
    x: float
    y: float

ball = Ball(screen.get_width() / 2.0, 0.0)

# 4 second qudratic fall to center of screen.
fall = ty.Tween(1.0, # Duration of tween is 4 seconds.
                  ball, # What object to mess with.
                  {"y" : screen.get_height() / 2}, # Animate what to where.
                  ease_func=quad) # How to animate it (defaults to linear)

ty.default_manager.add(fall) # Added it to the world.

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ty.default_manager.update(dt)
 
    screen.fill((0,0,0))
    pygame.draw.circle(screen, "red", (ball.x, ball.y), 40)

    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()
