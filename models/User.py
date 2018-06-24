from datetime import datetime

from models.Room import Room
from models.Schedule import Schedule
from models.Order import Order
from flask import session
import smtplib
import sched

import time

from common.database import Database
from models.facilities import Facilities
from models.friends import Friends


class User(object):
    def __init__(self, email, username, password, _id, role, permission, company, facility,
                 added_date=datetime.utcnow().strftime('%d/%m/%y'), manager=False, roles=[]):
        self.email = email
        self.password = password
        self.username = username
        self._id = _id
        self.role = role
        self.permission = permission
        self.company = company
        self.facility = facility
        self.added_date = added_date
        self.manager = manager
        self.roles = roles

    def save_to_mongodb(self):
        # print "need to fixed. save to mongo"
        Database.insert(collection='users', data=self.json())

    def save_to_mongodb_simulation(self):
        # print "need to fixed. save to mongo"
        Database.insertSimulation(collection='users', data=self.json())

    def json(self):
        return {
            'email': self.email,
            'username': self.username,
            'password': self.password,
            '_id': self._id,
            'role': self.role,
            'permission': self.permission,
            'company': self.company,
            'facility': self.facility,
            'added_date': self.added_date,
            'manager': self.manager,
            'roles': self.roles
        }

    def update_user(self, username=None, password=None, role=None, permission=None, facility=None):
        self.username = username if username is not None else self.username
        self.password = password if password is not None else self.password
        self.role = role if role is not None else self.role
        self.permission = permission if permission is not None else self.permission
        self.facility = facility if facility is not None else self.facility
        try:
            Database.update('users', {'email': self.email}, self.json())
            return True
        except Exception as e:
            return False

    @classmethod
    def get_by_email(cls, email):
        data = Database.find_one('users', {'email': email})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_email_simulation(cls, email):
        data = Database.find_oneSimulation('users', {'email': email})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_company(cls, company):
        users = []
        data = Database.find('users', {'company': company})
        if data is not None:
            for user in data:
                users.append(cls(**user))
        # print(len(users))
        # print(users)
        return set(users)

    @classmethod
    def get_by_company_simulation(cls, company):
        users = []
        data = Database.findSimulation('users', {'company': company})
        if data is not None:
            for user in data:
                users.append(cls(**user))
        # print(len(users))
        # print(users)
        return set(users)

    @classmethod
    def get_by_id(cls, _id):
        data = Database.find_one('users', {'_id': _id})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_id_simulation(cls, _id):
        data = Database.find_oneSimulation('users', {'_id': _id})
        if data is not None:
            return cls(**data)

    @staticmethod
    def login_valid(email, password):
        # Check whether a user's email matches the password they sent us
        user = User.get_by_email(email)
        if user is not None:
            # Check the password
            return user.password == password
        return False

    @staticmethod
    def login(user_email):
        # login_valid has already been called
        session['email'] = user_email

    @staticmethod
    def logout():
        session['email'] = None

    def get_friends(self):
        friends = Friends.get_friends(self.email)
        res = []
        for friend_email in friends:
            res.append(User.get_by_email(friend_email))
        return res

    def get_friends_emails(self):
        friends = Friends.get_friends(self.email)
        res = []
        for friend_email in friends:
            res.append(friend_email)
        return res

    def add_friend(self, friend_email):
        friend = User.get_by_email(friend_email)
        if friend is not None:
            if friend.company == self.company:
                return Friends.add_friend(self.email, friend_email)
            return False, "not in the same company, sorry"
        return False, "email dose'nt exist"

    def create_meeting(self, start_time, end_time, order_id, room_id, date=datetime.utcnow().strftime('%d/%m/%y'),
                       participants=[]):
        if self.email not in participants:
            participants.append(self.email)
        Schedule.assign_all(date, participants, start_time, end_time, order_id, room_id)

    def remove_friend(self, friend_email):
        return Friends.remove_friend(self.email, friend_email)

    def get_orders(self, start=None, end=None):
        return Order.find_by_user_email(self.email)

    def get_schedule(self, date=None, start_time=None, end_time=None, room_id=None):
        return Schedule.get_schedules(self.email, date, start_time, end_time, room_id)

    def new_order(self, date, participants, start_time, end_time, company, facility):


        if self.email not in participants:
            participants.append(self.email)
        problematic_participants = Schedule.all_participants_are_free(date, participants, start_time,
                                                                      end_time)

        if len(problematic_participants) > 0:
            return False, problematic_participants
        min_permission = User.min_permission(participants)
        _id = self.email + ' ' + date + ' ' + str(start_time) + ' ' + str(end_time)
        status, order_id, room_id = Order.new_order(_id, self.email, date, participants, start_time, end_time, company,
                                                    facility, min_permission)

        if status:
            # not finish yet
            Schedule.assign_all(date, participants, start_time, end_time, order_id, room_id)
            # self.create_meeting(start_time, end_time, order_id, room_id, date, participants)
        return status, order_id

    def new_order_simulation(self, date, participants, start_time, end_time, company, facility):
        if self.email not in participants:
            participants.append(self.email)
        problematic_participants = Schedule.all_participants_are_free_simulation(date, participants, start_time,
                                                                                 end_time)

        if len(problematic_participants) > 0:
            return False, problematic_participants
        min_permission = User.min_permission_simulation(participants)
        _id = self.email + ' ' + date + ' ' + str(start_time) + ' ' + str(end_time)
        status, order_id, room_id = Order.new_order_simulation(_id, self.email, date, participants, start_time,
                                                               end_time, company,
                                                               facility, min_permission)

        if status:
            # not finish yet
            Schedule.assign_all_simulation(date, participants, start_time, end_time, order_id, room_id)
            # self.create_meeting(start_time, end_time, order_id, room_id, date, participants)
        return status, order_id

    def cancel_meeting(self, meeting_id):
        """
        this user won't come to this meeting so the user decide to cancel it
        :param meeting_id:
        """

        order_id = Schedule.cancel_meeting(meeting_id)
        if Order.who_create_order(order_id) == self.email:
            return self.cancel_order(order_id)
        if order_id is not None:
            Order.participant_cancel(self.email, order_id)
            meetings = Schedule.get_by_order(order_id)
            for m in meetings:
                m.remove_participants(self.email)


    def cancel_order(self, order_id):
        """
        this method delete the order that match this order_id from the 'orders' table in db
        and delete the meeting from the schedule of each participant that invited to this meeting.
        only the user taht create this order can cancel it
        :param order_id:
        """
        if Order.who_create_order(order_id) == self.email:
            Order.delete_order(order_id)
            Schedule.delete_order(order_id)

    @classmethod
    def min_permission(cls, participants):
        permission = 1000000000
        for user in participants:
            user = User.get_by_email(user)
            if user is not None:
                permission = int(user.permission) if int(user.permission) < permission else permission
        return permission

    @classmethod
    def min_permission_simulation(cls, participants):
        permission = 1000000000
        for user in participants:
            user = User.get_by_email_simulation(user)
            if user is not None:
                permission = int(user.permission) if int(user.permission) < permission else permission
        return permission

    @classmethod
    def print_time(cls):
        print("************************************************From print_time", time.time())

    @classmethod
    def print_values(cls):
        print("")
        # sched.every(1).seconds.do(cls.print_time)


class Manager(User):

    def __init__(self, email, username, password, _id, role, permission, company, facility,
                 added_date=datetime.utcnow().strftime('%d/%m/%y'), manager=True,
                 roles=['Software Engineer', 'Architect Engineer', 'Electrical Engineer', 'Programmer']):
        self.email = email
        self.password = password
        self.username = username
        self._id = _id
        self.role = role
        self.permission = permission
        self.company = company
        self.facility = facility
        self.added_date = added_date
        self.manager = manager
        self.roles = roles

    @classmethod
    def get_by_email(cls, email):
        data = Database.find_one('users', {'$and': [{'manager': True}, {'email': email}]})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_email_simulation(cls, email):
        data = Database.find_oneSimulation('users', {'$and': [{'manager': True}, {'email': email}]})
        if data is not None:
            return cls(**data)

    def get_employees(self):
        return User.get_by_company(self.company)

    def get_employees_simulation(self):
        return User.get_by_company_simulation(self.company)

    @classmethod
    def manager_register(cls, email, password, username, _id, role, permission, company, facility):
        data = Database.find_one('facilities', {'company': company})
        role = 'Manager'
        permission = 100
        if data is not None:
            return False, "company already exist"
        else:
            user = cls.get_by_email(email)
            if not cls.check_id(_id):
                return False, "bad number ID"
            if user is None:
                # User dose'nt exist, create new user
                Facilities.add_company(company, facility)
                new_user = cls(email, username, password, _id, role, permission, company, facility)
                try:
                    new_user.save_to_mongodb()
                    session['email'] = email
                    return True, "SUCCESS"
                except Exception as e:
                    return False, str(e)
            else:
                # User already exist
                return False, "user email already exist"

    def manager_register_simulation(cls, email, password, username, _id, role, permission, company, facility):
        data = Database.find_oneSimulation('facilities', {'company': company})
        role = 'Manager'
        if data is not None:
            return False, "company already exist"
        else:
            Facilities.add_company_simulation(company, facility)
            user = cls.get_by_email_simulation(email)
            if user is None:
                # User dose'nt exist, create new user
                new_user = cls(email, username, password, _id, role, permission, company, facility)
                try:
                    new_user.save_to_mongodb_simulation()
                    session['email'] = email
                    return True, "SUCCESS"
                except Exception as e:
                    return False, str(e)
            else:
                # User already exist
                return False, "user email already exist"

    @classmethod
    def check_id(cls, _id):
        """check if the given _id is legal id"""
        if len(str(_id)) != 9:
            return False
        sum = 0
        factor = 0
        for i in _id:
            tmp = int(i) * (factor + 1)
            factor = (factor + 1) % 2
            dig = 1 if tmp > 9 else 0
            sum += tmp % 10 + dig
        return False if sum % 10 != 0 else True

    @classmethod
    def user_register(cls, email, password, username, _id, role, permission, company, facility):
        if not Facilities.is_company_exist(company):
            return False, "company dose'nt exist"
        user = User.get_by_email(email)
        print(email)
        if not cls.check_id(_id):
            return False, "bad number ID"
        if user is None:
            # User dose'nt exist, create new user
            new_user = User(email, username, password, _id, role, permission, company, facility)
            try:
                new_user.save_to_mongodb()
            except Exception as e:
                return False, str(e)
            return True, ''
        else:
            # User already exist
            return False, "user email already exist"

    @classmethod
    def user_register_simulation(cls, email, password, username, _id, role, permission, company, facility):
        if not Facilities.is_company_exist_simulation(company):
            return False, "company dose'nt exist"
        user = User.get_by_email_simulation(email)
        print(email)
        if user is None:
            # User dose'nt exist, create new user
            new_user = User(email, username, password, _id, role, permission, company, facility)
            try:
                new_user.save_to_mongodb_simulation()
            except Exception as e:
                return False, str(e)
            return True, ''
        else:
            # User already exist
            return False, "user email already exist"

    def delete_user(self, user_email):
        user = User.get_by_email(user_email)
        if user is not None and user.company == self.company:
            if Order.remove_user(user_email):
                Friends.remove_user(user_email)
                Schedule.remove_user(user_email)
                Database.remove('users', {'email': user_email})
                return True
        return False

    def get_facilities(self):
        return Facilities.get_facilities(self.company)

    def get_facilities_simulation(self):
        return Facilities.get_facilities_simulation(self.company)

    def get_roles(self):
        return self.roles

    def add_roles(self, new_role):
        self.roles.append(new_role)
        self.roles = list(set(self.roles))
        Database.update('users', {'email': self.email}, self.json())

    def add_facility(self, facility):
        Facilities.add_facility(self.company, facility)

    def add_facility_simulation(self, facility):
        Facilities.add_facility_simulation(self.company, facility)

    def import_employee(self, file):
        """
        :param file:the format is like this:
        Email,	Name,	Role,	Permission level,	Facility,	ID
        """

        with open(file) as details:  # open the file
            for line in filter(lambda x: x.strip(), details.readlines()):
                if line.find('@') == -1:
                    continue
                line = line.replace('"', "")
                print(line)
                email, name, role, permission, facility, id = line[:-1].split(
                    ",")  # get the parameters we need from the line
                self.add_facility(facility)
                self.add_roles(role)
                self.user_register(email, 'password', name, id, role, permission, self.company, facility)

    def add_room(self, permission, capacity, room_num, floor, facility, disabled_access):
        return Room.add_room(permission, capacity, room_num, floor, self.company, facility, disabled_access)

    # def add_room_simulation(self, permission, capacity, room_num, floor, facility, disabled_access):
    #     return Room.add_room(permission, capacity, room_num, floor, self.company, facility, disabled_access)

    def import_rooms(self, file):
        """
        :param file:the format is like this:
        "Room ID","Floor","Facility","Permission level","Capacity","Disabled access"

        """

        with open(file) as details:  # open the file
            for line in filter(lambda x: x.strip(), details.readlines()):
                if line.find('Permission level') != -1:
                    continue
                line = line.replace('"', "")
                print(line)
                room_id, floor, facility, permission, capacity, dsiabled_access = line[:-1].split(
                    ",")  # get the parameters we need from the line
                self.add_facility(facility)
                self.add_room(permission, capacity, room_id, floor, facility, dsiabled_access)

    def get_rooms(self):
        return Room.get_by_company(self.company)
