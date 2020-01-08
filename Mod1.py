import pygame
import time
from math import radians, sin, cos, tan, sqrt
 

#Algorithm to convert 3D coordinates into 2D screen coordinates
def get_2d(x, y, z):
    x -= cam_coords.x
    y -= cam_coords.y
    z -= cam_coords.z
    oldx = x
    oldy = y
    #turning camera
    x = x * cos(radians(rx)) - z * sin(radians(rx))
    z = z * cos(radians(rx)) + oldx * sin(radians(rx))
    y = y * cos(radians(ry)) - z * sin(radians(ry))
    z = z * cos(radians(ry)) + oldy * sin(radians(ry))
    z -= depth
    #eye coordinates
    class EyeCoords(object): 
        def __init__(self):
            self.x = 0
            self.y = 0
            self.z = -depth
    eye_coords = EyeCoords()
    try:
        x = x + (0 - z) * (x - eye_coords.x) / (z - eye_coords.z)
    except:
        x = cam_coords.x
    try:
        y = y + (0 - z) * (y - eye_coords.y) / (z - eye_coords.z)
    except:
        y = cam_coords.y
    x += xSize / 2
    y = ySize / 2 - y
    if z <= eye_coords.z:
        return "error"
    return int(x), int(y)


def build_landscape(landscape_detail):
    landscape = []
    for x in range(0, 100, landscape_detail):
        for z in range(0, 100, landscape_detail):
            landscape.append((x, 0, z))
    return landscape


if __name__ == "__main__":

    # init stuff
    pygame.init()
 
    xSize, ySize = 800, 400
    screen = pygame.display.set_mode((xSize, ySize))
    pygame.display.set_caption("Mod1")

    #generating flat landscape
    landscape_detail = 2
    landscape = build_landscape(landscape_detail)

    #distance between theorical screen and eye (changes fov)
    depth = 400
    #rotation about y axis
    ry = -30
    #rotation about x axis
    rx = 0

    #camera coordinates
    class CameraCoords(object):
        def __init__(self):
            self.x = 50
            self.y = 80
            self.z = -50
    cam_coords = CameraCoords()

    # main loop
    clock = pygame.time.Clock()
    fc = 0
    done = False
    while not done:
        fc += 1
        # input events
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    depth *= 1.1
                elif event.button == 5 and depth / 2 > 0:
                    depth /= 1.1
        if keys[pygame.K_ESCAPE]:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
        else:
            delta_x, delta_y = pygame.mouse.get_rel()
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
            rx += delta_x / 30
            ry -= delta_y / 30
            if ry > 90:
                ry = 90
            if ry < -90:
                ry = -90
        if keys[pygame.K_w]:
            cam_coords.x += sin(radians(rx))
            cam_coords.z += cos(radians(rx))
        if keys[pygame.K_a]:
            cam_coords.x += sin(radians(270 - rx))
            cam_coords.z += -cos(radians(270 - rx))
        if keys[pygame.K_s]:
            cam_coords.x += -sin(radians(180 - rx))
            cam_coords.z += cos(radians(180 - rx))
        if keys[pygame.K_d]:
            cam_coords.x += sin(radians(90 - rx))
            cam_coords.z += -cos(radians(90 - rx))
        if keys[pygame.K_SPACE]:
            cam_coords.y += 1
        if keys[pygame.K_LCTRL]:
            cam_coords.y -= 1

        #white background
        screen.fill([0,0,0])
        
        #animate landscape
        for i in range(len(landscape)):
            landscape[i] = (landscape[i][0], 30 + 4 * cos(5 * radians(landscape[i][2] + landscape[i][0] - fc)), landscape[i][2])
        
        #rendering landscape
        render = []
        for i in range(len(landscape)):
            render.append(get_2d(landscape[i][0], landscape[i][1], landscape[i][2]))

        max_val = int(100 / landscape_detail) + 1
        for i in range(len(landscape) - max_val):
            if (i + 1) % (max_val - 1) != 0 and (i + max_val) % (max_val - 1) != 0:
                # set polygone color
                color = [150 - (landscape[i][1] / 100) * 150, 100 + (landscape[i][1] / 100) * 100, 50]
                # print polygone
                try:
                    outline = pygame.draw.polygon(screen, color, (render[i], render[i+1], render[i+max_val], render[i+max_val-1]), 0)
                except ValueError:
                    pass
        fps = int(10 * clock.get_fps()) / 10
        fpsLabel = pygame.font.SysFont("monospace", 15).render(str(fps), 1, (0,0,0))
        #displays fps
        screen.blit(fpsLabel, (0,0))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
