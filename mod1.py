import click
import numpy as np
import time

from panda3d_visu import panda3d_draw_landscape


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
def build_landscape(n_points):
    xi = range(n_points)
    yi = range(n_points)
    xi, yi = np.meshgrid(xi, yi)
    xi, yi = xi.flatten(), yi.flatten()
    return xi, yi

def euclidean_distance(xa, ya, xb, yb):
    # substract over x
    dx = np.subtract.outer(xa, xb)
    # substract over y
    dy = np.subtract.outer(ya, yb)
    # euclidean dist
    return np.sqrt((dx)**2 + (dy)**2)

# Interpolation
def simple_idw(x, y, z, xi, yi):
    # Compute distance matrix
    dist = euclidean_distance(x, y, xi, yi)
    # In IDW, weights are 1 / distance !! TWEAKED !!
    weights = 1.0 / (dist + 1e-12)**3
    # Make weights sum to one
    weights /= weights.sum(axis=0)
    # Multiply the weights for each interpolated point by all observed Z-values
    zi = np.dot(weights.T, z)
    return zi

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
    xi, yi = build_landscape(n_points)
    # IDW interpolation
    zi = simple_idw(x, y, z, xi, yi)
    final_shape = (n_points, n_points)

    panda3d_draw_landscape((xi.reshape(final_shape),
                           yi.reshape(final_shape),
                           zi.reshape(final_shape)), n_points)

if __name__ == "__main__":
    main()
