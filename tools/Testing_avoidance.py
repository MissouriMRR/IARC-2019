from math import cos, pi, sin, asin, acos, degrees, radians
from numpy import array, append, dot
from matplotlib import pyplot as plt

SECTOR_ANGLE = 10#degrees
NUMBER_OF_SECTORS = 360/SECTOR_ANGLE
AVOID_SPEED = 2 #m/s
array_type = array([])
Z_SPEED = 0

#Simulated Values
s_angle = array([44,89,134,180,269,314,359])

    
obstacle_sector_history = []
    
def convert_to_cartessian(angle):
    angle_temp = []
    if (type(angle) != list) and (type(angle) != type(array_type)):
        angle_temp.append(angle)
        print('The given angle is type = ' + str(type(angle)))
        angle = []
        angle.append(angle_temp)
    if len(angle) == 1:
        angle = list(angle)
        angle.append(angle[0])
    unit_vector = ([])
    vector_angle = []
    i = 0
    for a in array(angle):        
        unit_vector.append([cos(radians(a)),sin(radians(a))])
    unit_vector = array(unit_vector)
    return unit_vector


sector_value = ((s_angle/SECTOR_ANGLE) + 1)
sector_value = (list(map(int,sector_value))) #round obstacle angle down a sector by using "int"
sector_value.sort() #sort vector numerically
sector_value = (list(dict.fromkeys(sector_value))) #remove duplicate sectors
print(sector_value)
obstacle_sector_history.append(sector_value)
    
unit_vector = convert_to_cartessian(SECTOR_ANGLE*array(sector_value))

for angle in s_angle:
    sector_difference = []
    count = 1;
    for sectors in sector_value:
        if (count) == len(sector_value):
            sector_difference.append(sector_value[0]-sectors+NUMBER_OF_SECTORS)
        else:
            sector_difference.append(sector_value[count]-sectors)
        count = count + 1
    
    avoid_angle = SECTOR_ANGLE*(max(sector_difference)/2+sector_value[sector_difference.index(max(sector_difference))])
           
    if avoid_angle > 360:
        avoid_angle = avoid_angle - 360
    avoid_sector = int(avoid_angle/SECTOR_ANGLE)
    avoid_unit_vector_temp = convert_to_cartessian((avoid_sector)*SECTOR_ANGLE)
    avoid_unit_vector = avoid_unit_vector_temp[0]
    [n,e,d] = [AVOID_SPEED*avoid_unit_vector[0],AVOID_SPEED*avoid_unit_vector[1],Z_SPEED]


    #This plots the dashed sector lines
    sector_line = 1
    while sector_line <= NUMBER_OF_SECTORS:
        plt.figure(1)
        current_angle = radians(sector_line*SECTOR_ANGLE)
        plt.plot([0,10*sin(current_angle)],[0,10*cos(current_angle)],'g--')
        sector_line = sector_line+1

    #This graphs the real position of the obstacles
    real_obstacle_position = convert_to_cartessian(s_angle)
    for vector in real_obstacle_position:
        plt.figure(1)    
        plt.plot(vector[1],vector[0],'ro')
        plt.axis([-2,2,-2,2])

    #This graphs the desired direction of the drone
    plt.figure(1)
    plt.plot([0,10*avoid_unit_vector[1]],[0,10*avoid_unit_vector[0]],'b')
plt.show()
    
    



