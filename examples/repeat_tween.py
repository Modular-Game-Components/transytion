import transytion as ty
from dataclasses import dataclass
from transytion.ease_funcs import inout, quad
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

ball = Ball(screen.get_width() / 4, screen.get_height() / 4)

fall = ty.Tween(1.0,
                ball,
                {"y" : 3 * screen.get_height() / 4.0},
                ease_func=inout(quad))

right = ty.Tween(1.0,
                 ball,
                 {"x" : 3 * screen.get_width() / 4.0},
                 ease_func=inout(quad))

rise = ty.Tween(1.0,
                ball,
                {"y" : screen.get_height() / 4.0},
                ease_func=inout(quad))

left = ty.Tween(1.0,
                ball,
                {"x" : screen.get_width() / 4.0},
                ease_func=inout(quad))


cycle = ty.chain([fall, right, rise, left])
rpts = ty.repeat(cycle)

ty.default_manager.add(rpts) # Added it to the world.

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
