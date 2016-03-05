'''
Created on Feb 6, 2016

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms.similar_graphs_mining.sketch_matrix import SketchMatrix
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

def plot_2d(data, x_axis, y_axis, out_eps_file=None):
    def find_value(x):
        for d in data:
            if d[x_axis] == x:
                return d[y_axis]
        return 0.
    
    X = np.array(sorted(list(set(map(lambda d: d[x_axis], data)))))
    Y = np.array(sorted(map(lambda x: find_value(x), X)))
    
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.plot(X, Y, '-')
    
    if out_eps_file:
        plt.savefig(out_eps_file, format='eps')
    
    plt.show()
    
def plot_3d(data, x_axis, y_axis, z_axis, out_eps_file=None, azim=0., elev=0.):
    '''Plot data in 3D.
    :param data: A list of dictionaries.
    :param x_axis: A string representing the data property for the x axis.
    :param y_axis: A string representing the data property for the y axis.
    :param z_axis: A string representing the data property for the z axis.
    '''
    def accuracy(x, y):
        for d in data:
            if d[x_axis] == x and d[y_axis] == y:
                return d[z_axis]
        return 0.

    vector_accuracy = np.vectorize(accuracy)
    
    X = np.array(sorted(list(set(map(lambda x: x[x_axis], data)))))
    Y = np.array(sorted(list(set(map(lambda x: x[y_axis], data)))))
    X, Y = np.meshgrid(X, Y)
    Z = vector_accuracy(X, Y)
    
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    
    font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 7}

    plt.rc('font', **font)
    
    surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0, antialiased=False)
    ax.view_init(azim=azim, elev=elev)
    
    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)
    ax.set_zlabel(z_axis)

    ax.zaxis.set_major_locator(LinearLocator(10))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
    
    fig.colorbar(surf, shrink=0.5, aspect=5)
    if out_eps_file:
        fig.savefig(out_eps_file, format='eps')
    
    plt.show()

# models = [
# ]
# 
# plot_3d(models, "infl_point", "wl_iterations", "auc", "auc", -90, 69)