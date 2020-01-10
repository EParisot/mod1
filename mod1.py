import click
import numpy as np

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
    fig.update_layout(scene=dict(aspectratio=dict(x=2, y=2, z=0.5)),
                      scene_camera=camera)
    go_offline.plot(fig, filename='mod1.html',validate=True, auto_open=True)

def vispy_draw_landscape(xi, yi, zi):
    import vispy.plot as vp
    from vispy import color
    fig = vp.Fig(show=False)
    # colormap
    cnorm = zi / abs(np.amax(zi))
    c = color.get_colormap("terrain").map(cnorm).reshape(zi.shape + (-1,))
    c = c.flatten().tolist()
    c = list(map(lambda x,y,z,w:(x,y,z,w), c[0::4],c[1::4],c[2::4],c[3::4]))
    # actual plot
    suface = fig[0, 0].surface(zi)
    suface.mesh_data.set_vertex_colors(c)
    fig.show()

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
    # plotly
    plotly_draw_landscape(xi.reshape(final_shape),
                   yi.reshape(final_shape),
                   zi.reshape(final_shape),
                   n_points)
    # vispy
    vispy_draw_landscape(xi.reshape(final_shape),
                   yi.reshape(final_shape),
                   zi.reshape(final_shape))


if __name__ == "__main__":
    main()
