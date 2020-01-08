import pygame
import time
from math import radians, sin, cos, tan, sqrt
from utils import CameraCoords, build_landscape, get_2d, handle_events
import click

@click.command()
@click.argument('filename', type=click.Path(exists=True))
def main(filename):
    # init pygame stuff
    pygame.init()
    screenSize = (400, 400)
    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("Mod1")

    # init cam coords
    cam_coords = CameraCoords()

    #generating landscape
    landscape_detail = 1
    landscape = build_landscape(filename, landscape_detail)

    # main loop
    clock = pygame.time.Clock()
    fc = 0
    done = False
    while not done:
        fc += 1
        # input events
        done = handle_events(cam_coords)

        #white background
        screen.fill([0,0,0])
        
        """#animate landscape
        for i in range(len(landscape)):
            landscape[i] = (landscape[i][0],
                            30 + 4 * cos(5 * radians(landscape[i][2] + landscape[i][0] - fc)),
                            landscape[i][2])"""
        
        #rendering landscape
        render = []
        for i in range(len(landscape)):
            render.append(get_2d(landscape[i][0],
                                 landscape[i][1],
                                 landscape[i][2],
                                 cam_coords,
                                 screenSize))

        max_val = int(50 / landscape_detail) + 1
        for i in range(len(landscape) - max_val):
            if (i + 1) % (max_val - 1) != 0 and (i + max_val) % (max_val - 1) != 0:
                # set polygone color
                color = [150 - (landscape[i][1] / 100) * 150,
                         100 + (landscape[i][1] / 100) * 100,
                         50]
                # print polygone
                try:
                    outline = pygame.draw.polygon(screen,
                                                  color,
                                                  (render[i],
                                                   render[i+1],
                                                   render[i+max_val],
                                                   render[i+max_val-1]),
                                                  0)
                except TypeError:
                    pass
                
        fps = int(10 * clock.get_fps()) / 10
        fpsLabel = pygame.font.SysFont("monospace", 15).render(str(fps), 1, (255,255,255))
        #displays fps
        screen.blit(fpsLabel, (0,0))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
