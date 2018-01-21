import os
import subprocess

from Employee import Employee
from Room import Room
from Database.ManageDB import *
from SimulationEngine import *


def enter_rooms_csv(filename):
    import_room_details_from_file(filename)


def enter_employees_csv(filename):
    import_employees_from_file(filename)


def add_employee_aux(employee_str):
    id, name, role, access_permission, password = employee_str.split()
    add_employee(Employee(int(id), name, role, int(access_permission), password))


def add_room_aux(room_str):
    id, floor, max_capacity, access_permission = room_str.split()
    add_room(Room(id, int(floor), int(max_capacity), int(access_permission)))


def remove_employee_aux(id):
    remove_employee(int(id))


def update_employee_aux(employee_str):
    id, name, role, access_permission, password = employee_str.split()
    update_employee(int(id), name, role, int(access_permission), password)


def update_room_aux(room_str):
    id, floor, max_capacity, access_permission = room_str.split()
    update_room(id, int(floor), int(max_capacity), int(access_permission))

def add_friend_aux(cmd_str):
    emp_id, friend_id = cmd_str.split()
    add_a_friend_for_employee(emp_id,friend_id)

def remove_friend_aux(cmd_str):
    emp_id, friend_id = cmd_str.split()
    delete_a_friend_from_employee(emp_id,friend_id)

def get_friends_list_aux(user_id):
    for id in get_friends_list(user_id):
        name = Employee.find_one({"id" : str(id)})
    print id + " " + name + "\n"

def enter_week_sched_cvs(filename):
    pass  # waiting for fundction to be written


def get_room_recommendation(cmd_str):
    """
    id, date_time = cmd_str.split(' ', 1)
    RoomReccomendations(Rooms, Employees).reccomendationToEmployeeByRoom(int(id), date_time)
    """
    pass


def help():
    print '\n'.join(['Currently, available commands are: ', 'enter_rooms_csv filename', 'enter_employees_csv filename',
                     'add_employee id name role access_permission password', 'add_room id floor max_capacity access_permission',
                     'add_friend your_id friend_id', 'remove_friend your_id friend_id', 'remove_employee id', 'display_friends',
                     'remove_room id','update_employee id name role access_permission',
                     'update_room id floor max_capacity access_permission','simulation', 'help', 'quit'])
    # 'enter_week_sched_cvs id filename',
    # 'get_room_recommendation id DD/MM/YY HH',


if __name__ == "__main__":
    p = subprocess.Popen('mongod', stdout=open(os.devnull, "w"))
    print 'Welcome to TheDoors, The Program for Solving the Door Permissions Problem!'
    help()

    cmd_dict = {'enter_rooms_csv': enter_rooms_csv, 'enter_employees_csv': enter_employees_csv,
                'add_employee': add_employee_aux, 'add_room': add_room_aux, 'remove_employee': remove_employee_aux,
                'remove_room': remove_room, 'update_employee': update_employee_aux, 'update_room': update_room_aux,
                'enter_week_sched_cvs': enter_week_sched_cvs, 'get_room_recommendation': get_room_recommendation,
                'add_friend': add_friend_aux, 'remove_friend': remove_friend_aux, 'display_friends': get_friends_list_aux}
    while True:
        cmd_args = raw_input('>>> ').split(' ', 1)
        if cmd_args == ['help']:
            help()
        elif cmd_args == ['quit']:
            print 'Shutting down Program'
            p.terminate()
            break
        elif cmd_args == ['simulation']:
            print 'RUNNING SIMULATION'
            simulation_day_in_factory(new_rooms_details='rooms_demo.csv')
        elif len(cmd_args) > 1 and cmd_args[0] in cmd_dict.keys():
            cmd, args = cmd_args
            try:
                cmd_dict[cmd](args)
            except (ValueError, TypeError) as e:
                print 'Error! Invalid input, try again'
        else:
            print 'Command does not exist, please try again.'
