import transytion as ty
from dataclasses import dataclass
from transytion.ease_funcs import bounce
import pygame
import vidmaker

video = vidmaker.Video(path="simple_tween.mp4", 
                       fps=60, 
                       resolution=(1280, 720))


pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

@dataclass
class Ball:
    x: float
    y: float
    r: float

ball = Ball(screen.get_width() / 2.0, 0.0 - 40, 40)

def stop_rec():
    video.export(verbose=True)
    pygame.quit()
    exit()

# 4 second qudratic fall to center of screen.
fall = ty.Tween(duration=1.0, # Duration of tween is 4 seconds.
                obj=ball, # What object to mess with.
                targets={"y" : screen.get_height() / 2}, # Animate what to where.
                ease_func=bounce,
                callback=stop_rec
                )

ty.default_manager.add(fall) # Added it to the world.

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ty.default_manager.update(dt)
 
    screen.fill((0,0,0))
    pygame.draw.circle(screen, "red", (ball.x, ball.y), ball.r)

    pygame.display.flip()
    dt = clock.tick(60) / 1000

    video.update(pygame.surfarray.pixels3d(screen).swapaxes(0, 1), 
                 inverted=False)

pygame.quit()
