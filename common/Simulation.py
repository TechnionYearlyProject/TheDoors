from datetime import datetime,timedelta

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
DATE = datetime.now()

def add_random_users_simulation(maxEmployees, manager):
    '''
    the function creates random users and adds them to the simulation engine
    :param maxEmployees: maximum of employees in the simulation can't be zero
    :param manager: the manager of the simulation
    '''
    global NUM_FACILITIES
    global NUM_EMPLOYEES
    if maxEmployees is 0:
        return
    NUM_EMPLOYEES = random.randint(maxEmployees / 2, maxEmployees)
    for i in range(NUM_EMPLOYEES):
        status, info = manager.user_register_simulation("simulationEmp" + str(i) +"@gmail.com",
                                         str(i), "simulationEmp" + str(i), str(i), 'Software Engineer',
                                         3, 'Simulation', "facility" + str(random.randint(1, NUM_FACILITIES)))
        if status:
            return info

def add_random_rooms_simulation(maxRooms, manager):
    '''
    the function creates random rooms and adds them to the simulation engine
    :param maxRooms: maximum of rooms in the simulation can't be zero
    :param manager: the manager of the simulation
    '''
    global NUM_ROOMS
    global NUM_FACILITIES
    if maxRooms is 0:
        return
    NUM_ROOMS = random.randint(1, maxRooms)
    for i in range(NUM_ROOMS):
        Room.add_room_simulation(Room, random.randint(3,6), random.randint(30,100), i, str(manager.company), "facility" + str(random.randint(1, NUM_FACILITIES)))

def add_random_facilities_simulation(maxFacilities, manager):
    '''
    the function creates random facilitiess and adds them to the simulation engine
    :param maxFacilities: maximum of facilities in the simulation can't be zero
    :param manager: the manager of the simulation
    '''
    global NUM_FACILITIES
    if maxFacilities is 0:
        return
    NUM_FACILITIES = random.randint(1, maxFacilities)
    for i in range(NUM_FACILITIES):
        facility = "facility" + str(i)
        manager.add_facility_simulation(facility)

def order_rooms_simulation(duration):
    global DURATION
    global HOURS_PER_DAY
    global NUM_EMPLOYEES
    global DATE
    DURATION = duration
    duration_hours = DURATION * HOURS_PER_DAY
    poisson_dest = np.random.poisson((NUM_EMPLOYEES/20 +1), duration_hours)
    day_need_to_add = 0
    for hour in range(duration_hours-1):
        time = 8 + (hour % 10)
        DATE += timedelta(days = day_need_to_add)
        for i in range(poisson_dest[hour]-1):
            user_index = random.randint(0, NUM_EMPLOYEES-1)
            user = User.get_by_email_simulation("simulationEmp" + str(user_index) +"@gmail.com")
            return user
            participants_id = [user_index]
            num_of_participants = random.randint(0,4)
            for i in range(num_of_participants):
                participant = random.randint(1, NUM_EMPLOYEES-1)
                while participant in participants_id:
                    participant = random.randint(1, NUM_EMPLOYEES-1)
                participants_id.append(participant)
            participants = []
            for id in participants_id:
                participants.append("simulationEmp" + str(id) +"@gmail.com")
            # participants = map(lambda id: "simulationEmp" + str(id) +"@gmail.com", participants_id)
            user.new_order_simulation(DATE.strftime('%d/%m/%Y'),participants,time, time+1, 'Simulation', user.facility)
        if hour%10 == 0:
            day_need_to_add += 1


def simulation_engine(max_rooms, max_employees, max_facilities, duration):
    global DATE
    Database.initialize()
    status, info = Manager.manager_register_simulation(Manager, "simulation@gmail.com", 'admin', 'simulation admin', '000000000', 'Manager', 100, 'Simulation', 'sim')
    if not status:
        return (info)
    manager = Manager.get_by_email_simulation("simulation@gmail.com")
    DATE = datetime.now()
    add_random_facilities_simulation(max_facilities,manager)
    add_random_rooms_simulation(max_rooms, manager)
    info = add_random_users_simulation(max_employees, manager)
    # return info
    user = order_rooms_simulation(duration)
    # return user
    return (NUM_EMPLOYEES, NUM_ROOMS, NUM_FACILITIES)




