from classes.gridElements import *
from classes.controller import *
from utils.apply_profile_bat import *

def main():
    #Time series initialization for simulation. In a real situation, we'd get values from sensors
    ts_pv_system = [0, 0, 0, 0, 0, 0, 0.1, 0.1, 0.25, .5, .7, .9, 1, 1, .95, .7, .3, .15, 0, 0, 0, 0, 0, 0]
    ts_load = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ts_battery = []

    '''
    CASE 1
    '''
    #Initialization of elements
    ctrl1 = Controller("Main Controller")
    pv1 = Pv_system("PV1",ctrl1,1000,ts_pv_system)
    pv2 = Pv_system("PV2", ctrl1, 500, ts_pv_system)
    load1 = Load("LOAD1",ctrl1,700,ts_load)
    p_max_grid1 = 200


    for t in range(24):
        ctrl1.step(p_max_grid1,t)


    '''
    CASE 2
    ctrl1 = Controller("Main Controller")
    pv1 = Pv_system("PV1",ctrl1,1000,ts_pv_system)
    load1 = Load("LOAD1",ctrl1,700,ts_load)
    
    bat1 = Battery("BATTERY1", ctrl1, 100)
    #bat2 = Battery("BATTERY2", ctrl1, 300)
    
    battery_optimization = ctrl1.optimization_battery(24, p_max_grid1)
    print(battery_optimization)

    apply_profile_battery(battery_optimization,ctrl1)


    for t in range(24):
        ctrl1.step(p_max_grid1,t)
    '''



if __name__ == "__main__":
    main()




