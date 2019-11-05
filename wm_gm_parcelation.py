# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 19:07:17 2017

@author: jljnh
"""

#import dipy
import os
import nibabel as nib
import numpy as np


#%%

v_x = [-1,-1,-1,-1,-1,-1,-1,-1,-1,       0, 0, 0, 0, 0, 0, 0, 0,     1, 1, 1, 1, 1, 1, 1, 1, 1  ]
v_y = [ 0,-1, 1, 0, 0,-1,-1, 1, 1,      -1, 1, 0, 0,-1,-1, 1, 1,     0,-1, 1, 0, 0,-1,-1, 1, 1  ]
v_z = [ 0, 0, 0,-1, 1,-1, 1,-1, 1,       0, 0,-1, 1,-1, 1,-1, 1,     0, 0, 0,-1, 1,-1, 1,-1, 1  ]

avance = zip(v_x , v_y , v_z)

## verifica su es una casilla disponible
def avaliable (i,j,k, data):    
    if 0 <= i < data.shape[0] and 0 <= j < data.shape[1] and 0<= k < data.shape[2] :
        if data[int (i)][int(j)][int(k)] ==1:
            return 1        
    else:
        return 0


#### hace una matriz 3d a una tabla de n x 3, que tiene las coordenadas de los puntos que forman parte de la corteza
def matrix_to_coordenate_array(data):
    total = np.where(data == 1)
    return np.transpose(total)


import random

###  escoge n_regions al azar de una tabla de coordenadas
def choose_random_regions(coor , n_regions , my_data):
    d = coor.shape
    
    idi = random.sample(range(d[0]) , n_regions)
    
    regions = []
    centroids = []
    n_centroids =  [1 ] * n_regions
    for i in idi:
        regions.append( [coor[i] ])
        centroids.append( np.array(coor[i] )  )
    
    return[regions, centroids , n_centroids]


#### agrega a un arreglo los vecinos posibles de un punto current, y lo marca con idi como id
def add_avaliable_neighboors(array , current ,my_data  , idi):
    
    append = array.append
    for i ,j,k in avance:
        if avaliable(current[0]  +i , current[1] + j, current[2] + k , my_data ) :
            append([current[0]  +i , current[1] + j, current[2] + k])
            
    

## marca todos los vecinos y agrega a la frontera los vecinos de vecinos

def add_all_neighboors2(my_data , idi):
    frontier  = np.where(my_data == idi)
    frontier = np.transpose(frontier)
    vecinos = [(x+i , y+j , z +k)  for x,y,z  in frontier for i,j,k in avance ]
    vecinos = set(vecinos)
    
    agrego= 0
    for x,y,z  in vecinos :
        if avaliable(x,y,z , my_data):
            agrego = 1
            my_data[x][y][z] = idi
    
    return agrego
    
    
## checa si los elementos en la frontera estan disponibles
def get_avaiable_frontier(array , my_data , idi):
    
    while len(array) != 0:
        try:
            my_random = random.randint(0 , len(array) -1)
            dato = array[my_random]
            del array[my_random]
            
            if avaliable(dato[0] , dato[1] , dato[2] , my_data) == 1:
                return dato
        
    
        except:
            print array
            print len(array) , not array
    return [-1,-1,-1]
    
    ## a partir de randon_regions, las infla en un nodo cada una de las regiones

def inflate_regions_random(random_region , my_data ,centroids , n_centroids ):
    
     d = len(random_region)
     
     for i in range(d):
         
         if len(random_region[i])  == 0:
             continue
         current  = get_avaiable_frontier(random_region[i] , my_data , i+2)
       
         
         #print "*-*-*-* " , current
         if current[0] != -1 :
             add_avaliable_neighboors(random_region[i] , current , my_data , i+2 )
             my_data[int(current[0])] [int(current[1])] [int(current[2])]  = i+2
             centroids[i] = centroids[i] +  np.array(current)
             n_centroids[i] += 1
          #   print "---" , counter


#### el algoritmo que hace crecer las regiones nodo a nodo de forma aleatoria
def create_random_regions(my_data , random_origin  , centroids , n_centroids):
    
    points = np.count_nonzero(my_data == 1)
  
    while points != 0:
        inflate_regions_random(random_origin , my_data , centroids , n_centroids)
        zeros =  check_empty_array(random_origin) 
        print zeros
        if zeros == len(random_origin):
            break


#####
## infla una cubierta cada region
def inflate_uniform_region( my_data  , mini, maxi ,active):
    
    d = len(active)
    
    for i in xrange(d):
        if active[i] == 1:
            agrego = add_all_neighboors2(my_data , i+2 )
            
            cuantos = np.count_nonzero(my_data == i+2)
            if agrego ==0:
                active[i] = 0
                if cuantos < mini:
                    my_data[my_data == i+2] = 1
                    continue
            
            if cuantos > maxi:    
                active[i] = 0
               
        
    print np.count_nonzero(active == 0) , " desativados "
            
            

def check_empty_array(array):
    
    idi =0
    for i in array:
        if len(i) == 0 :
            idi = idi+1
    
    return idi




### algoritmo que hace crecer a capas las regiones dadas
def expand_uniform_regions( my_data , mini ,maxi,active , n_regions):
    
    for i in range(5):
        
        iterations = 0
        eliminados =0
        active = np.repeat(1 , n_regions)
        while eliminados != n_regions :
            print "iteracion -->" , iterations 
            iterations += 1
            
            inflate_uniform_region(my_data , mini,maxi , active)
            
            eliminados = np.count_nonzero(active == 0)
            print eliminados ,  ' - ' , n_regions  
        

def median_points(v):
    v = list(v)
    for i in range(len(v)):
        v[i] = list(v[i])
   
    vv = sorted(v)
    m = len(vv) / 2
    
    return vv[m]

def get_color_region(coor , my_data):
    col = [0] * len(coor)
    i = 0
    for x,y,z in coor:
        
        col[i] = my_data[int(x)][int(y)][int(z)]
        i = i+1
        
    return col



########################################## MAIN 
#%%

import sys
import copy
argumentos = sys.argv


#os.chdir('/home/juanitovh/Documents/tracto/Sample-data/Masks-and-Segmentations')
#os.chdir('D:\\tracto\\Masks-and-Segmentations')
#archivos = os.listdir(os.getcwd())

img = nib.load(argumentos[1])

img2 = copy.deepcopy(img)

#img = nib.load(argumentos[1])




data = img.get_data()



data2 = img2.get_data()
data3 = np.copy(data)



n_regions_old  = argumentos[2]
n_regions = n_regions_old * 1.6
n_regions = int(n_regions)


cortex = matrix_to_coordenate_array(data)
regions , centroids , n_centroids = choose_random_regions(cortex, n_regions  ,data)
create_random_regions(data , regions , centroids , n_centroids)


#%%

"""
for i in range(len(centroids)):
    centroids[i] = centroids[i] / n_centroids[i] 
    for j in range(3):
        centroids[i][j] = int(centroids[i][j])
"""
#%%


centroids22 = []

for i in range(n_regions):
    aux = np.where(data  == i+2 )
    aux = np.transpose(aux)
    median  = median_points(aux)
    centroids22.append(median)


centroids2 = centroids22

#data2 = np.copy(data3)
i = 0
for x,y,z in centroids2:
    data2[x][y][z] = i+2
    i +=1
    
#%%
active = np.repeat(1 , n_regions)
print np.count_nonzero(data2 == 1) ######################
min_region = np.count_nonzero(data2 == 1)/ float (n_regions_old)

max_region = min_region  
min_region= min_region * 0.7

print "intervalo de confianza " , min_region , " ----" , max_region
expand_uniform_regions( data2  , min_region ,max_region ,active , n_regions)

#%%

col = get_color_region(cortex , data2)

#%%
maxi = -1
mini = float('inf')
vvv = []
regiones_nula = 0
for i in range(n_regions):
    xx = np.count_nonzero(data2 == i+2) 
    maxi = max(xx , maxi)
    #print xx  , " - " , i+2
    vvv.append(xx)
    if xx == 0:
        regiones_nula +=1
    else:
         mini = min(xx , mini)

print "regiones inservibles = " , regiones_nula 
print "min - max"  , mini , " - " , maxi

print "regiones activas " , np.count_nonzero(data2 == 1)



print "total regiones" , n_regions - regiones_nula , 'de  ' , n_regions_old , "que queriamos"


#%%
v2 =np.array(vvv)

v2 = v2[v2!=0] 

#%%

import matplotlib.pyplot as plt

plt.plot(v2 , 'ro')





#%%

dim = data.shape
tot = dim[0] * dim[1] * dim[2]

print "comparacion matrices" , np.sum(img2.get_data() == data2) ,  tot

print "comparacion matrices" , np.sum(img.get_data() == data2) ,  tot


np.mean(v2)

#%%

def recorre_(daton , n_reg_aumentada ,n_reg):
    daton[daton == 1] = 0
    start = 1
    end = 1
    while(end <= n_reg_aumentada +1):
        cuenta = np.count_nonzero(daton == end)
        
        if cuenta == 0:
            end += 1
        elif  cuenta != 0 and start < end:
            daton[ daton == end] = start
            start +=1
            end +=1
    print "termine en " ,  start
    for  i in range(start +1 ,  n_reg+1):
        daton[0,i%108,0] = i

recorre_(data2 , n_regions  , n_regions_old)

#%%

nib.save(img2 , 'interface_100_genial.nii')
