import numpy as np

E_fiber = 70e9 #Gpa
E_matrix = 4e9 #Gpa
fracture_energy_fiber = Gpc = 10 #J/m2
fracture_energy_matrix = Gmc =400 #J/m2

#1) caluclate max fracture energy that allows crack deflexion from matrix in the fiber
E1 = E_fiber
E2 = E_matrix 

alpha = (E1 - E2)/ (E1+ E2) #around 0.89
#read on graph
gd_gc_ratio = 2.0
min_gic = 2 * Gpc
print(min_gic)


#2) caluclate max fracture energy that allows crack deflexion from fiber in the matrix

E2 = E_fiber
E1 = E_matrix 

alpha = (E1 - E2)/ (E1+ E2) #around -0.89
#read on graph
gd_gc_ratio = 0.5
min_gic = 0.5 * Gmc
print(min_gic)