from vpython import scene, quad, sphere, vertex, vec, color, compound

from collections import deque
import numpy as np
import time

run = True
def mouseDown(ev):
    global run
    run = not run

water_color = vec(0, 0, 0.6)

def get_color(h):
    if h < 5:
        curr_color = vec(102, 51, 0) / 255
    elif h < 10:
        curr_color = vec(153, 204, 0) / 255
    elif h < 70:
        curr_color = vec(0, 153, 0) / 255
    elif h < 100:
        curr_color = vec(255, 255, 255) / 255
    return curr_color

def draw_map(xi, yi, zi, n_points):
    terrain = []
    for row in range(n_points):
        for col in range(n_points):
            if row != n_points-1 and col != n_points-1:
                a = vertex( pos=vec(xi[row][col], yi[row][col], zi[row][col]), color=get_color(zi[row][col]))
                b = vertex( pos=vec(xi[row][col+1], yi[row][col+1], zi[row][col+1]), color=get_color(zi[row][col+1]))
                c = vertex( pos=vec(xi[row+1][col+1], yi[row+1][col+1], zi[row+1][col+1]), color=get_color(zi[row+1][col+1]))
                d = vertex( pos=vec(xi[row+1][col], yi[row+1][col], zi[row+1][col]), color=get_color(zi[row+1][col]))
                terrain.append(quad(vs=[a,b,c,d]))
    compound(terrain)
    water = []
    for row in range(n_points):
        for col in range(n_points):
            if row != n_points-1 and col != n_points-1:
                a = vertex( pos=vec(xi[row][col], yi[row][col], 0), color=water_color, opacity=0.3)
                b = vertex( pos=vec(xi[row][col+1], yi[row][col+1], 0), color=water_color, opacity=0.3)
                c = vertex( pos=vec(xi[row+1][col+1], yi[row+1][col+1], 0), color=water_color, opacity=0.3)
                d = vertex( pos=vec(xi[row+1][col], yi[row+1][col], 0), color=water_color, opacity=0.3)
                water.append(quad(vs=[a,b,c,d]))
    water_comp = compound(water, pos=vec(n_points / 2, n_points / 2, 0))
    return water_comp

def is_empty(drops, x, y, z):
    for drop in drops:
        if drop.pos.x == x and drop.pos.y == y and drop.pos.z == z:
            return False
    return True

def update_drops(drops, levels, zi, n_points):
    start_flood = False
    for i, drop in enumerate(drops):
        drop_pos = drop.pos
        if drop_pos.z > 0:
            alt = drop_pos.z - (zi[int(drop_pos.y)][int(drop_pos.x)] if levels < zi[int(drop_pos.y)][int(drop_pos.x)] else levels)
            if alt > 1:
                drop.pos.z -= 1
            elif alt >= 0.1:
                drop.pos.z = (zi[int(drop_pos.y)][int(drop_pos.x)] if levels < zi[int(drop_pos.y)][int(drop_pos.x)] else levels)
            else:
                if int(drop_pos.y) - 1 >= 0 and \
                        is_empty(drops, int(drop_pos.x), int(drop_pos.y) - 1, zi[int(drop_pos.y) - 1][int(drop_pos.x)]) and \
                        (zi[int(drop_pos.y) - 1][int(drop_pos.x)] if levels < zi[int(drop_pos.y) - 1][int(drop_pos.x)] else levels) < drop_pos.z:
                    drop.pos.y -= 1
                    drop.pos.z = (zi[int(drop_pos.y)][int(drop_pos.x)] if levels < zi[int(drop_pos.y)][int(drop_pos.x)] else levels)
                elif int(drop_pos.y) + 1 < n_points and \
                        is_empty(drops, int(drop_pos.x), int(drop_pos.y) + 1, zi[int(drop_pos.y) + 1][int(drop_pos.x)]) and \
                        (zi[int(drop_pos.y) + 1][int(drop_pos.x)] if levels < zi[int(drop_pos.y) + 1][int(drop_pos.x)] else levels) < drop_pos.z:
                    drop.pos.y += 1
                    drop.pos.z = (zi[int(drop_pos.y)][int(drop_pos.x)] if levels < zi[int(drop_pos.y)][int(drop_pos.x)] else levels)
                elif int(drop_pos.x) - 1 >= 0 and \
                        is_empty(drops, int(drop_pos.x) - 1, int(drop_pos.y), zi[int(drop_pos.y)][int(drop_pos.x) - 1]) and \
                        (zi[int(drop_pos.y)][int(drop_pos.x) - 1] if levels < zi[int(drop_pos.y)][int(drop_pos.x) - 1] else levels) < drop_pos.z:
                    drop.pos.x -= 1
                    drop.pos.z = (zi[int(drop_pos.y)][int(drop_pos.x)] if levels < zi[int(drop_pos.y)][int(drop_pos.x)] else levels)
                elif int(drop_pos.x) + 1 < n_points and \
                        is_empty(drops, int(drop_pos.x) + 1, int(drop_pos.y), zi[int(drop_pos.y)][int(drop_pos.x) + 1]) and \
                        (zi[int(drop_pos.y)][int(drop_pos.x) + 1] if levels < zi[int(drop_pos.y)][int(drop_pos.x) + 1] else levels) < drop_pos.z:
                    drop.pos.x += 1
                    drop.pos.z = (zi[int(drop_pos.y)][int(drop_pos.x)] if levels < zi[int(drop_pos.y)][int(drop_pos.x)] else levels)
                else:
                    drops.pop(i)
                    drop.visible = False
                    start_flood = True
    return start_flood


def vpython_draw_landscape(landscape):
    xi = landscape[0]
    yi = landscape[1]
    zi = landscape[2]
    n_points = len(zi[0])

    scene.background = vec(0.95, 0.95, 0.95)
    scene.width = 1200
    scene.height = 600
    scene.center = vec(n_points / 2, n_points / 2, 0)
    scene.forward = vec(0, 0.5, -0.2)
    scene.bind("mousedown", mouseDown)

    # draw map
    water_comp = draw_map(xi, yi, zi, n_points)

    drops = []
    levels = 0.0
    while True:
        while not run:
            scene.waitfor('redraw')
        # create drops
        x = np.random.randint(0, n_points)
        y = np.random.randint(0, n_points)
        drop = sphere(pos=vec(x, y, n_points), radius=0.5, color=water_color, opacity=0.3)
        drops.append(drop)
        # update drops
        start_flood = update_drops(drops, levels, zi, n_points)
        # flood water
        if start_flood == True and levels < n_points:
            water_comp.pos.z += 0.01
            levels += 0.01
        # TODO wave(s)

        # set speed
        time.sleep(1/60)