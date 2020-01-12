import click
from collections import deque
import numpy as np
import time

def parse_point(line_data):
    data = line_data.split(' ')
    if len(data) == 3:
        try:
            int_data = list(map(int, data))
        except:
            print("Invalid data : %s Ignored Point" % line_data, flush=True)
            return None
    else:
        print("Incomplete data : %s Ignored Point" % line_data, flush=True)
        return None
    return int_data

def parse_file(filename):
    data_list = []
    with open(filename) as f:
        for line in f:
            clean_data = parse_point(line)
            if clean_data and clean_data not in data_list:
                data_list.append(clean_data)
    return data_list

# Build flat land
def build_lanscape(n_points):
    xi = range(n_points)
    yi = range(n_points)
    xi, yi = np.meshgrid(xi, yi)
    xi, yi = xi.flatten(), yi.flatten()
    return xi, yi

def euclidean_distance(xa, ya, xb, yb):
    dx = np.subtract.outer(xa, xb)
    dy = np.subtract.outer(ya, yb)
    return np.sqrt((dx)**2 + (dy)**2)

# Interpolation
def simple_idw(x, y, z, xi, yi):
    # Compute distance matrix
    dist = euclidean_distance(x, y, xi, yi)
    # In IDW, weights are 1 / distance !! TWEAKED !!
    weights = 1 / (dist + 1e-12)**3
    # Make weights sum to one
    weights /= weights.sum(axis=0)
    # Multiply the weights for each interpolated point by all observed Z-values
    zi = np.dot(weights.T, z)
    return zi

def plotly_draw_landscape(xi, yi, zi, n_points):
    import plotly.offline as go_offline
    import plotly.graph_objects as go
    fig=go.Figure()
    #TODO change colorscale to custom
    colorscale = [
        [0.0, "rgb(77, 38, 0)"],
        [0.1, "rgb(153, 102, 51)"],
        [0.3, "rgb(134, 179, 0)"],
        [0.6, "rgb(51, 153, 51)"],
        [1.0, "rgb(204, 255, 255)"]]
    #camera
    camera = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=0.0, y=-2.5, z=0.7))
    fig.add_trace(go.Surface(x=xi, y=yi, z=zi, colorscale=colorscale, showscale=False))
    fig.update_layout(scene=dict(aspectratio=dict(x=1, y=1, z=0.5)),
                      scene_camera=camera)
    go_offline.plot(fig, filename='mod1.html',validate=True, auto_open=True)

def vispy_loop(landscape):
    import vispy
    from vispy import app, scene, geometry
    from vispy.visuals import transforms
    from vispy import color

    xi = landscape[0]
    yi = landscape[1]
    zi = landscape[2]

    canvas = scene.SceneCanvas(title="Mod1", size=(800,600), keys='interactive')
    view = canvas.central_widget.add_view()
    view.camera = scene.cameras.TurntableCamera(center=(50, 50, 50), scale_factor=200)

    surface = scene.visuals.GridMesh(xi, yi, zi, colors=None, shading='smooth')
    surface.transform = transforms.STTransform(translate=(0., 0., 0.), scale=(1., 1., 0.5))
    tr = np.array(surface.transform.translate)
    tr[2] += 50
    surface.transform.translate = tr

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

    view.add(surface)
    canvas.show()

    def new_drop(x, y):
        drop = scene.visuals.Sphere(radius=0.1,  color=(0, 0, 1, 1))
        drop.transform = transforms.STTransform(translate=(0., 0., 0.), scale=(1., 1., 1.))
        tr = np.array(drop.transform.translate)
        tr[0] = x
        tr[1] = y
        tr[2] = 100
        drop.transform.translate = tr
        return drop

    drops = deque(maxlen=50)
    def rain(var):
        # add a new drop
        drop = new_drop(np.random.randint(0, 99), np.random.randint(0, 99))
        drops.append(drop)
        view.add(drop)
        # update drops
        for drop in drops:
            tr = np.array(drop.transform.translate)
            tr[2] -= 1
            drop.transform.translate = tr

    timer = app.Timer(interval=0, connect=rain)
    timer.start()
    
    app.run()


@click.command()
@click.argument("filename", default="maps/map0.mod1", type=click.Path(exists=True))
def main(filename):
    n_points = 100
    # read input
    points_list = parse_file(filename)
    x = np.array([point[0] for point in points_list])
    y = np.array([point[1] for point in points_list])
    z = np.array([point[2] for point in points_list])
    # append border's null values
    for j in range(n_points):
        for i in range(n_points):
            if j == 0 or j == n_points - 1 or i == 0 or i == n_points - 1:
                x = np.append(x, i)
                y = np.append(y, j)
                z = np.append(z, 0)
    # init landscape
    xi, yi = build_lanscape(n_points)
    # IDW interpolation
    zi = simple_idw(x, y, z, xi, yi)
    final_shape = (n_points, n_points)
    """# plotly
    plotly_draw_landscape(xi.reshape(final_shape),
                   yi.reshape(final_shape),
                   zi.reshape(final_shape),
                   n_points)"""
    # vispy
    vispy_loop((xi.reshape(final_shape),
                   yi.reshape(final_shape),
                   zi.reshape(final_shape)))

if __name__ == "__main__":
    main()
