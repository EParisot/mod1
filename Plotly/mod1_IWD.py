import numpy as np
import plotly.offline as go_offline
import plotly.graph_objects as go

# file input parsing
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
            if clean_data:
                data_list.append(clean_data)
    return data_list

def build_lanscape(n_points):
    # flat land
    xi = range(n_points)
    yi = range(n_points)
    xi, yi = np.meshgrid(xi, yi)
    xi, yi = xi.flatten(), yi.flatten()
    return xi, yi

def euclidean_distance(x1, y1, x2, y2):
    d = np.sqrt( (x1 - x2)**2 + (y1 - y2)**2 )
    return d

def simple_idw(x, y, z, xi, yi):
    dist = distance_matrix(x, y, xi, yi)
    # In IDW, weights are 1 / distance !!TWEAKED
    weights = 1 / (dist + 1e-12) ** 2
    # Make weights sum to one
    weights /= weights.sum(axis=0)
    # Multiply the weights for each interpolated point by all observed Z-values
    zi = np.dot(weights.T, z)
    return zi

def distance_matrix(x0, y0, x1, y1):
    obs = np.vstack((x0, y0)).T
    interp = np.vstack((x1, y1)).T

    # Make a distance matrix between pairwise observations
    # Note: from <http://stackoverflow.com/questions/1871536>
    # (Yay for ufuncs!)
    d0 = np.subtract.outer(obs[:,0], interp[:,0])
    d1 = np.subtract.outer(obs[:,1], interp[:,1])

    return np.hypot(d0, d1)

def draw_landscape(xi, yi, zi, n_points):
    fig=go.Figure()
    fig.add_trace(go.Surface(x=xi, y=yi, z=zi))
    fig.update_layout(scene=dict(aspectratio=dict(x=2, y=2, z=0.5)))
    go_offline.plot(fig, filename='3d_terrain.html',validate=True, auto_open=True)

if __name__ == "__main__":
    n_points = 100
    # read input
    points_list = parse_file("../maps/map0.mod1")
    x = np.array([point[0] for point in points_list])
    y = np.array([point[1] for point in points_list])
    z = np.array([point[2] for point in points_list])
    print(x, y, z)
    # init landscape
    xi, yi = build_lanscape(n_points)
    
    # interpolation
    zi = simple_idw(x, y, z, xi, yi)
    #zi = np.zeros(n_points * n_points, dtype="int8")
    
    print(xi.shape, yi.shape, zi.shape)
    
    # plotly
    final_shape = (n_points, n_points)
    draw_landscape(xi.reshape(final_shape),
                   yi.reshape(final_shape),
                   zi.reshape(final_shape),
                   n_points)