import numpy as np
from scipy.special import comb

import matplotlib as mpl
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def bernstein_poly(i, n, t):
    return comb(n, i) * (t**(n - i)) * (1 - t)**i


def bezier_curve(points, nTimes=1000):
    nPoints = len(points)
    xPoints = np.array([p[0] for p in points])
    yPoints = np.array([p[2] for p in points])
    zPoints = np.array([p[1] for p in points]) # switch

    t = np.linspace(0.0, 1.0, nTimes)

    polynomial_array = np.array(
        [bernstein_poly(i, nPoints - 1, t) for i in range(0, nPoints)])

    xvals = np.dot(xPoints, polynomial_array)
    yvals = np.dot(yPoints, polynomial_array)
    zvals = np.dot(zPoints, polynomial_array) * 4 # trick to be fixed

    res = []
    for i, _ in enumerate(xvals):
        res.append([xvals[i], zvals[i], yvals[i]]) # note switch here

    return res

if __name__ == "__main__":
    nPoints = 3
    points = np.random.rand(nPoints, 3) * 100
    
    points[0][0] = 0
    points[0][1] = 0
    points[0][2] = 0

    points[1][2] = 0
 
    points[-1][0] = 100
    points[-1][1] = 0
    points[-1][2] = 0

    xpoints = [p[0] for p in points]
    ypoints = [p[2] for p in points]
    zpoints = [p[1] for p in points]

    curve = bezier_curve(points, nTimes=1000)

    xvals = []
    yvals = []
    zvals = []
    for pt in curve:
        xvals.append(pt[0])
        yvals.append(pt[2])
        zvals.append(pt[1])

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.plot(xvals, yvals, zvals, label='bezier')
    ax.plot(xpoints, ypoints, zpoints, "ro")
    for nr in range(len(points)):
        ax.text(points[nr][0], points[nr][1], points[nr][2], nr)

    plt.show()
