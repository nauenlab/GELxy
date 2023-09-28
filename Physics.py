# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 12:51:21 2023

@author: Saturn
"""


from math import pow, sqrt
from Coordinate import Coordinate


def get_velocity(initial_coordinate, final_coordinate):
    xi, yi = initial_coordinate.x, initial_coordinate.y
    xf, yf = final_coordinate.x, final_coordinate.y
    v2(xi, xf)
    

def v2(i, f):
    d = f - i
    a = 4.0
    t = 1 # make this a variable value
    
    pvf1 = 8*t - 4*(sqrt((4*pow(t, 2))-d))
    pvf2 = 8*t + 4*(sqrt((4*pow(t, 2))-d))
    print(pvf1, pvf2)
    
    if check_vf_correctness(pvf1, d, t):
        print("YAY")
    
    if check_vf_correctness2(pvf1, d, t):
        print("YAY")
    
    
#    print(vf)
    
def check_vf_correctness(v, d, t):
    arc_distance = 2*pow(v/2, 3/2)/3
    half_linear_distance = (v*pow(t,2))/2 - pow(v, 2)/4
    f_h_integral = (v*(sqrt(d/2)+1)*t)
    l_h_integral = (v*(sqrt(d/2)+1)*sqrt(v/2))
    last_linear_distance = f_h_integral - l_h_integral
    rect_distance = half_linear_distance + last_linear_distance
    
    print(arc_distance, rect_distance, d)
    print(arc_distance + rect_distance)
    return arc_distance + rect_distance == d


def check_vf_correctness2(v, d, t):
    tri_distance = pow(v, 3)/96
    half_linear_distance = (v*pow(t,2))/2 - pow(v, 2)/32
    f_h_integral = v*(sqrt(d/2)+1)*(t-(v/4))
    rect_distance = half_linear_distance + f_h_integral
    
    print(tri_distance, rect_distance, d)
    print(tri_distance + rect_distance)
    return tri_distance + rect_distance == d
   
   
    

c1 = Coordinate(0,0)
c2 = Coordinate(1, 0.08)

print(get_velocity(c1, c2))
#print(quad(integrand, 0, 2))