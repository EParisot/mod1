import pygame
from math import radians, sin, cos, tan, sqrt

#camera coordinates
class CameraCoords(object):
    def __init__(self, x=25, y=50, z=-50, rx=0, ry=-30, depth=400):
        self.x = x
        self.y = y
        self.z = z
        self.rx = rx #rotation around x axis
        self.ry = ry #rotation around y axis
        self.depth = depth

#eye coordinates
class EyeCoords(object): 
    def __init__(self, depth):
        self.x = 0
        self.y = 0
        self.z = -depth

#Algorithm to convert 3D coordinates into 2D screen coordinates
def get_2d(x, y, z, cam_coords, screenSize):
    x -= cam_coords.x
    y -= cam_coords.y
    z -= cam_coords.z
    oldx = x
    oldy = y
    #turning camera
    x = x * cos(radians(cam_coords.rx)) - z * sin(radians(cam_coords.rx))
    z = z * cos(radians(cam_coords.rx)) + oldx * sin(radians(cam_coords.rx))
    y = y * cos(radians(cam_coords.ry)) - z * sin(radians(cam_coords.ry))
    z = z * cos(radians(cam_coords.ry)) + oldy * sin(radians(cam_coords.ry))
    z -= cam_coords.depth
    # create eye corrd object
    eye_coords = EyeCoords(cam_coords.depth)
    try:
        x = x + (0 - z) * (x - eye_coords.x) / (z - eye_coords.z)
    except:
        x = cam_coords.x
    try:
        y = y + (0 - z) * (y - eye_coords.y) / (z - eye_coords.z)
    except:
        y = cam_coords.y
    x += screenSize[0] / 2
    y = screenSize[1] / 2 - y
    if z <= eye_coords.z:
        return "error"
    return int(x), int(y)

def parse_file(filename):
    data = []
    with open(filename) as f:
        for line in f:
            line_data = line.split(' ')
            if len(line_data) == 3:
                try:
                    data.append(list(map(int, line_data)))
                except:
                    print("Invalid data : %s Ignored Point" % line, flush=True)
            else:
                print("Incomplete data : %s Ignored Point" % line, flush=True)
    return data

def build_landscape(filename, landscape_detail):
    map_data = parse_file(filename)
    print(map_data, flush=True)
    landscape = []
    for x in range(0, 50, landscape_detail):
        for z in range(0, 50, landscape_detail):
            for i in range(len(map_data)):
                if x == map_data[i][0] and z == map_data[i][2]:
                    landscape.append((x, map_data[i][1], z))
                else:
                    landscape.append((x, 0, z))
    return landscape

def handle_events(cam_coords):
    done = False
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                cam_coords.depth *= 1.1
            elif event.button == 5 and cam_coords.depth / 2 > 0:
                cam_coords.depth /= 1.1
    if keys[pygame.K_ESCAPE]:
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
    else:
        delta_x, delta_y = pygame.mouse.get_rel()
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        cam_coords.rx += delta_x / 30
        cam_coords.ry -= delta_y / 30
        if cam_coords.ry > 90:
            cam_coords.ry = 90
        if cam_coords.ry < -90:
            cam_coords.ry = -90
    if keys[pygame.K_w]:
        cam_coords.x += sin(radians(cam_coords.rx))
        cam_coords.z += cos(radians(cam_coords.rx))
    if keys[pygame.K_a]:
        cam_coords.x += sin(radians(270 - cam_coords.rx))
        cam_coords.z += -cos(radians(270 - cam_coords.rx))
    if keys[pygame.K_s]:
        cam_coords.x += -sin(radians(180 - cam_coords.rx))
        cam_coords.z += cos(radians(180 - cam_coords.rx))
    if keys[pygame.K_d]:
        cam_coords.x += sin(radians(90 - cam_coords.rx))
        cam_coords.z += -cos(radians(90 - cam_coords.rx))
    if keys[pygame.K_SPACE]:
        cam_coords.y += 1
    if keys[pygame.K_LCTRL]:
        cam_coords.y -= 1
    return done
