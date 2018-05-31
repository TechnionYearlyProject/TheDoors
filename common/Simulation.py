from datetime import datetime

from models.Room import Room
from models.Schedule import Schedule
from models.Order import Order
from flask import session
from models.User import User, Manager
from common.database import Database
from models.facilities import Facilities
from models.friends import Friends
import numpy as np
import random

NUM_EMPLOYEES = 0
NUM_ROOMS = 0
NUM_FACILITIES = 0
DURATION = 0
HOURS_PER_DAY = 10

def add_random_users_simulation(maxEmployees, manager):
    '''
    the function creates random users and adds them to the simulation engine
    :param maxEmployees: maximum of employees in the simulation can't be zero
    :param manager: the manager of the simulation
    '''
    global NUM_FACILITIES
    global NUM_EMPLOYEES
    NUM_EMPLOYEES = random.randint(maxEmployees / 2, maxEmployees)
    for i in range(NUM_EMPLOYEES):
        manager.user_register_simulation("simulationEmp" + str(i) +"@gmail.com", str(i), "simulationEmp" + str(i), '000000026', 'eng', 3, 'Simulation', "facility" + str(random.randint(1, NUM_FACILITIES)))

def add_random_rooms_simulation(maxRooms, manager):
    '''
    the function creates random rooms and adds them to the simulation engine
    :param maxRooms: maximum of rooms in the simulation can't be zero
    :param manager: the manager of the simulation
    '''
    global NUM_ROOMS
    global NUM_FACILITIES
    NUM_ROOMS = random.randint(1, maxRooms)
    for i in range():
        Manager.add_room_simulation(random.randint(1,3), random.randint(30,100), i, random.randint(1,3), "facility" + str(random.randint(1, NUM_FACILITIES)), True)

def add_random_facilities_simulation(maxFacilities, manager):
    '''
    the function creates random facilitiess and adds them to the simulation engine
    :param maxFacilities: maximum of facilities in the simulation can't be zero
    :param manager: the manager of the simulation
    '''
    global NUM_FACILITIES
    NUM_FACILITIES = random.randint(1, maxFacilities)
    for i in range(NUM_FACILITIES):
        manager.add_facility_simulation("facility" + str(i))

def order_rooms_simulation(duration):
    global DURATION
    global HOURS_PER_DAY
    DURATION = duration
    duration_hours = DURATION * HOURS_PER_DAY
    poisson_dest = np.random.poisson(2, duration_hours)
    #TODO: order rooms for employees according to the poisson




def simulation_engine():
    Database.initialize()
    Manager.manager_register_simulation("simulation@gmail.com", 'admin', 'simulation admin', '000000000', 'eng', 1, 'Simulation', 'sim')
