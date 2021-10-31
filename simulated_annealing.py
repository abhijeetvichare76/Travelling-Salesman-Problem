# simulated annealing

import numpy as np
from numpy.lib.npyio import save

# Rastrigin function with inbuilt optional noise
def rastrigin(x, y, noise=False, nsr=1):
    z = 20 + (x**2 - 10 * np.cos(2 * np.pi * x)) + (y**2 - 10 * np.cos(2 * np.pi * y))

    if noise:
        return z + (nsr * 70 * (np.random.rand(*z.shape) - 0.5))
    else:
        return z

#acceptance probability for minimization
#Exponent evaluates to lower values for better successors, hence increasing probability of jump
def acceptance_probability(new_objective_function, old_objective_function, T):

    return 1 - np.exp( (new_objective_function - old_objective_function) / T)

#Neighbour centered around current point
def neighbor_2d(x, y, low=0, high=100):
    return (x + (high * (np.random.rand() - 0.5)), y + (high * (np.random.rand() - 0.5)))


# Objective function placeholder
def objective_function_2d(x,y):
    #Add true to parameters to induce noise
    #return rastrigin(x,y,True)
    return rastrigin(x,y)

#Simulated annealing for 2D
def simulated_annealing_2d(x0, y0, objective_function, save_hist=False):
    #Initial position
    x = x0
    y = y0
    old_objective_function = objective_function(x,y)
    #Temperature, threshold and rate of cooling
    T = 1.0
    T_min = 0.000001
    alpha = 0.7

    #Saving history
    if save_hist:
        hist = [(x,y, old_objective_function)]
    
    #Annealing
    while T > T_min:
        i = 1
        #Number of iterations
        while i < 10000:
            #Finf neighbour
            (new_x,new_y) = neighbor_2d(x,y)
            new_objective_function = objective_function_2d(new_x, new_y)

            ap = acceptance_probability(new_objective_function, old_objective_function, T)
            
            #If solution better, jump
            if new_objective_function < old_objective_function:
                x = new_x
                y = new_y
                old_objective_function = new_objective_function

                if save_hist:
                    hist.append((x,y,old_objective_function))

            #If worse off, jump with probability
            elif ap > np.random.rand():
                x = new_x
                y = new_y
                old_objective_function = new_objective_function

                if save_hist:
                    hist.append((x,y, old_objective_function))

            i += 1
        #Cooling
        T *= alpha

    #Saving history
    if save_hist:
        return x, y, old_objective_function, np.array(hist)

    return x, y, old_objective_function


#Plotting solutions
import matplotlib.pyplot as plt
from matplotlib import cm 
from mpl_toolkits.mplot3d import Axes3D 
X = np.linspace(-5.12, 5.12, 100)     
Y = np.linspace(-5.12, 5.12, 100)     
X, Y = np.meshgrid(X, Y) 

#Rastrigin visualization data samples
Z = (X**2 - 10 * np.cos(2 * np.pi * X)) + \
  (Y**2 - 10 * np.cos(2 * np.pi * Y)) + 20

x_final, y_final, objective_function_final, pos = simulated_annealing_2d(4, 4, rastrigin, True)
xs = []
ys = []
zs = []
for p in pos:
    xs.append(p[0])
    ys.append(p[1])
    zs.append(p[2])
#Printing final solutions
out_text = "Final Solution X: " + str(x_final) +" Y: " + str(y_final) + " Value: " + str(objective_function_final)
print(out_text)
fig = plt.figure() 
fig.suptitle('Simulated Annealing')
ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax1.set_title('Accepted solutions')
ax1.scatter(xs,ys,zs, label = 'accepted solutions')
ax1.scatter([x_final],[y_final],[objective_function_final],marker='x',c='red', label = 'final solution')
ax1.legend()
ax1.set_xlabel('X value')
ax1.set_ylabel('Y value')
# plt.savefig('rastrigin_graph.png')
ax1 = fig.add_subplot(1, 2, 2, projection='3d')
ax1.set_title('Rastragin function')
ax1.plot_surface(X, Y, Z, rstride=1, cstride=1,
  cmap=cm.nipy_spectral, linewidth=0.08,
  antialiased=True)
ax1.set_xlabel('X value')
ax1.set_ylabel('Y value')
ax1.text2D(-1.5, -0.5, out_text, transform=ax1.transAxes)
plt.show()
