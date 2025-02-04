from math import *

def Distance_sphere(long1,lat1,long2,lat2,R): # formule de haversine
    return 2*R*asin(sqrt(sin(lat1-lat2)**2+cos(lat1)*cos(lat2)*sin(long1-long2)**2))