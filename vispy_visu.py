from collections import deque
import numpy as np
import vispy
from vispy import app, scene, geometry
from vispy.visuals import transforms
from vispy import color

n_points = 100

def new_drop(x, y):
    drop = scene.visuals.Sphere(radius=1,  color=(0, 0, 0.6, 0.6))
    drop.transform = transforms.STTransform(translate=(0., 0., 0.), scale=(1., 1., 1.))
    tr = np.array(drop.transform.translate)
    tr[0] = x
    tr[1] = y
    tr[2] = n_points
    drop.transform.translate = tr
    return drop

def vispy_loop(landscape):
    # buid canvas and camera
    canvas = scene.SceneCanvas(title="Mod1", size=(800,600), keys='interactive')
    view = canvas.central_widget.add_view()
    view.camera = scene.cameras.TurntableCamera(center=(50, 50, 50), scale_factor=200)

    xi = landscape[0]
    yi = landscape[1]
    zi = landscape[2]
    # draw landscape
    surface = scene.visuals.GridMesh(xi, yi, zi, colors=None, shading='smooth')
    surface.transform = transforms.STTransform(translate=(0., 0., 0.), scale=(1., 1., 1))

    # landscape colors
    surface.shininess = 0
    color_norm = zi / abs(np.amax(zi))
    colormap = color.get_colormap("terrain").map(color_norm).reshape(zi.shape + (-1,))
    colormap = colormap.flatten().tolist()
    colormap = list(map(lambda x,y,z,w:(x,y,z,w), 
                                colormap[0::4], 
                                colormap[1::4], 
                                colormap[2::4], 
                                colormap[3::4]))
    surface.mesh_data.set_vertex_colors(colormap)

    # start drawing
    view.add(surface)
    canvas.show()

    drops = deque(maxlen=n_points)
    def rain(event):
        # add a new drop
        drop = new_drop(np.random.randint(0, n_points), np.random.randint(0, n_points))
        drops.append(drop)
        view.add(drop)
        # update drops
        for drop in drops:
            tr = np.array(drop.transform.translate)
            if tr[2] > 0:
                alt = tr[2] - zi[int(tr[1])][int(tr[0])]
                if alt > 1:
                    tr[2] -= 1
                elif alt >= 0.1:
                    tr[2] -= alt
                else:
                    if int(tr[1]) - 1 > 0 and zi[int(tr[1]) - 1][int(tr[0])] < tr[2]:
                        tr[1] -= 1
                        tr[2] = zi[int(tr[1])][int(tr[0])]
                    if int(tr[1]) + 1 < n_points and zi[int(tr[1]) + 1][int(tr[0])] < tr[2]:
                        tr[1] += 1
                        tr[2] = zi[int(tr[1])][int(tr[0])]
                    if int(tr[0]) - 1 > 0 and zi[int(tr[1])][int(tr[0]) - 1] < tr[2]:
                        tr[0] -= 1
                        tr[2] = zi[int(tr[1])][int(tr[0])]
                    if int(tr[0]) + 1 < n_points and zi[int(tr[1]) - 1][int(tr[0]) + 1] < tr[2]:
                        tr[0] += 1
                        tr[2] = zi[int(tr[1])][int(tr[0])]
                drop.transform.translate = tr
    # set loop timed callback
    timer = app.Timer(interval=1/60, connect=rain)
    timer.start()
    
    app.run()