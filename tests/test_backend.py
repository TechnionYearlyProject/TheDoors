import pytest
import os
import subprocess

from datetime import datetime

from common.database import Database
from models.Room import Room
from models.Schedule import Schedule
from models.User import Manager, User
from models.facilities import Facilities
from models.friends import Friends
from models import Analytics


@pytest.fixture(autouse=True)
def p():
    p = subprocess.Popen('mongod', stdout=open(os.devnull, "w"))
    yield p
    p.terminate()


def test_user():
    Database.initialize()
    Database.dropAll()
    Manager.manager_register("admin@yahoo.com", 'admin', 'Admin admin', '000000000', 'eng', 1, 'YAHOO', 'matam')
    Manager.user_register("email@gmail.com", '123', 'ely', '000000026', 'eng', 3, 'YAHOO', 'matam')
    Manager.user_register("user@yahoo.com", '123', 'yosi', '023412349', 'eng', 1, 'YAHOO', 'matam')
    Manager.user_register("user2@yahoo.com", '123', 'dave', '123412348', 'eng', 1, 'YAHOO', 'matam')
    Manager.user_register("email_1@gmail.com", '123', 'foox', '000002600', 'eng', 3, 'YAHOO', 'matam')
    Manager.user_register("email_2@gmail.com", '123', 'avi', '000260000', 'eng', 3, 'YAHOO', 'matam')
    Manager.user_register("email_3@gmail.com", '123', 'yin', '000000026', 'eng', 3, 'YAHOO', 'matam')
    Manager.user_register("email_4@gmail.com", '123', 'yan', '026000000', 'eng', 3, 'YAHOO', 'matam')

    assert User.get_by_id("email@gmail.com") is None
    # assert User.get_by_id("000000000") is not None
    assert Manager.get_by_email("admin@yahoo.com").company == 'YAHOO'
    assert User.get_by_email('user@yahoo.com').company == 'YAHOO'
    assert User.get_by_email("user2@yahoo.com").company == 'YAHOO'

    assert User.login_valid('email_4@gmail.com', '123') is True
    assert User.login_valid('email_4@gmail.com', 'username__') is False

    manager = Manager.get_by_email('user@yahoo.com')
    assert manager is None
    manager = Manager.get_by_email('admin@yahoo.com')
    assert manager is not None
    assert manager.delete_user('user@yahoo.com') is True
    assert User.get_by_email('user@yahoo.com') is None
    assert manager.delete_user('email_3@gmail.com') is False

    assert manager.delete_user('aaaaaaaaaaaaa') is False
    assert User.min_permission(['email_4@gmail.com', "user2@yahoo.com", "admin@yahoo.com"]) == 1
    assert User.min_permission(['email_4@gmail.com', 'email_1@gmail.com']) == 3
    assert manager.update_user('manager') is True
    print(os.getcwd() + '/rooms.csv')
    try:
        manager.import_rooms(os.getcwd() + '\\rooms.csv')
        manager.import_employee(os.getcwd() + '\\employee.csv')
    # should'nt works on travis
    except Exception as e:
        pass


def test_rooms():
    Database.initialize()

    Database.remove('rooms', {})
    status, room_id = Room.add_room(2, 30, 1, 3, 'YAHOO', 'matam', True)
    assert status is True
    status, room_id = Room.add_room(2, 30, 3, 4, 'YAHOO', 'matam', False)
    assert status is True
    assert Room.remove_room(room_id) is True
    status, room_id = Room.add_room(2, 30, 3, 4, 'YAHOO', 'matam', True)
    assert status is True
    assert Room.get_by_id(room_id).company == 'YAHOO'
    assert len(Room.get_by_company('YAHOO')) > 0
    assert len(Room.get_by_facility('YAHOO', 'matam')) > 0
    assert len(Room.get_by_capacity(5, 'YAHOO', 'matam', 2)) > 0
    assert len(Room.get_by_capacity(50, 'YAHOO', 'matam', 2)) == 0
    assert len(Room.get_by_capacity(20, 'YAHOO', 'matam', 3)) > 0
    assert len(Room.get_by_capacity(20, 'YAHOO', 'matam', 1)) == 0

    # todo - Ilana should fix this
    # assert len(Room.available_rooms('11/11/11', 12, 1, 2, 2, 'YAHOO', 'matam')) > 0


# todo - Ilana should fix this
def test_schedules_orders():
    Database.initialize()
    Database.dropAll()
    Manager.manager_register("admin@yahoo.com", 'admin', 'Admin admin', '000000000', 'eng', 1, 'YAHOO', 'matam')

    status, room_id = Room.add_room(2, 30, 1, 3, 'YAHOO', 'matam', True)
    assert status is True
    status, room_id = Room.add_room(2, 30, 3, 4, 'YAHOO', 'matam', False)
    assert status is True
    assert Room.remove_room(room_id) is True
    status, room_id = Room.add_room(2, 30, 3, 4, 'YAHOO', 'matam', True)

    num1 = Database.count('orders')
    Database.remove('orders', {'_id': '23/05/18'})
    num2 = Database.count('orders')
    Database.remove('orders', {'date': '26/05/18'})
    num3 = Database.count('orders')
    num_users1 = Database.count('users')
    Manager.user_register("email_1@gmail.com", '123', 'foox', '000002600', 'eng', 3, 'YAHOO', 'matam')
    Manager.user_register("email_4@gmail.com", '123', 'yan', '026000000', 'eng', 3, 'YAHOO', 'matam')
    num_users2 = Database.count('users')

    manager = Manager.get_by_email('user@yahoo.com')
    assert manager is None
    manager = Manager.get_by_email('admin@yahoo.com')
    assert manager is not None
    try:
        manager.import_rooms(os.getcwd() + '\\rooms.csv')
        manager.import_employee(os.getcwd() + '\\employee.csv')
    # should'nt works on travis
    except Exception as e:
        pass
    num_users2 = Database.count('users')

    user = User.get_by_email('email_1@gmail.com')
    participants = ['email_1@gmail.com', 'email_2@gmail.com']
    date = datetime.utcnow().strftime('%d/%m/%y')
    date = '26/06/18'
    status, string = user.new_order(date, participants, 1, 2, "YAHOO", 'matam')
    print(string)
    orders = user.get_orders()
    num_orders = len(orders)
    assert len(user.get_orders()) > 0
    schedules = user.get_schedule()
    assert len(schedules) > 0
    schedules = Schedule.get_schedules('email_1@gmail.com')
    assert len(Schedule.get_by_room("YAHOO matam 1")) > 0
    assert len(Room.available_rooms('11/11/11', 2, 1, 2, 2, 'YAHOO', 'matam')) > 0


def test_schedules_orders2():
    User.print_values()
    Database.initialize()
    Database.dropAll()
    # Database.find_one('orders', {'_id' : '23/05/18' })
    # num1 = Database.count('orders')
    # Database.remove('orders', {'_id': '23/05/18'})
    # num2 = Database.count('orders')

    Manager.manager_register("admin@yahoo.com", 'admin', 'Admin admin', '000000000', 'eng', 1, 'YAHOO', 'matam')


    status, room_id = Room.add_room(2, 2, 1, 3, 'YAHOO', 'matam', True) ########################################changed capacity
    assert status is True
    status, room_id = Room.add_room(2, 1, 3, 4, 'YAHOO', 'matam', False)
    assert status is True
    assert Room.remove_room(room_id) is True
    status, room_id = Room.add_room(2, 1, 3, 4, 'YAHOO', 'matam', True)

    num1 = Database.count('orders')
    Database.remove('orders', {'_id': '23/05/18'})
    num2 = Database.count('orders')
    Database.remove('orders', {'date': '26/05/18'})
    num3 = Database.count('orders')
    num_users1 = Database.count('users')
    Manager.user_register("email_1@gmail.com", '123', 'foox', '000002600', 'eng', 3, 'YAHOO', 'matam')
    Manager.user_register("email_4@gmail.com", '123', 'yan', '026000000', 'eng', 3, 'YAHOO', 'matam')
    num_users2 = Database.count('users')

    manager = Manager.get_by_email('user@yahoo.com')
    assert manager is None
    manager = Manager.get_by_email('admin@yahoo.com')
    assert manager is not None
    try:
        manager.import_rooms(os.getcwd() + '\\rooms.csv')
        manager.import_employee(os.getcwd() + '\\employee.csv')
    # should'nt works on travis
    except Exception as e:
        pass
    num_users2 = Database.count('users')

    user1 = User.get_by_email('email_1@gmail.com')
    user2 = User.get_by_email('email_4@gmail.com')
    participants1 = ['email_1@gmail.com', 'email_2@gmail.com']
    participants2  =['email_4@gmail.com']
    #date = datetime.utcnow().strftime('%d/%m/%y')
    date = '26/06/18'
    status2, string2 = user2.new_order(date, participants2, 6, 7, "YAHOO", 'matam')
    schedules2 = user2.get_schedule()

    status1, string1 = user1.new_order(date, participants1, 6, 7, "YAHOO", 'matam')
    schedules1 = user1.get_schedule()
    schedules2 = user2.get_schedule()
    print(string1)

    orders = user1.get_orders()
    num_orders = len(orders)
    assert len(user1.get_orders()) > 0
    schedules1 = user1.get_schedule()
    assert len(schedules1) > 0
    schedules = Schedule.get_schedules('email_1@gmail.com')
    assert len(Schedule.get_by_room("YAHOO matam 1")) > 0
    schedules2 = user2.get_schedule()
    assert len(schedules2) > 0



def test_schedules_orders3():
    User.print_values()
    Database.initialize()
    Database.dropAll()
    # Database.find_one('orders', {'_id' : '23/05/18' })
    # num1 = Database.count('orders')
    # Database.remove('orders', {'_id': '23/05/18'})
    # num2 = Database.count('orders')

    Manager.manager_register("admin@yahoo.com", 'admin', 'Admin admin', '000000000', 'eng', 1, 'YAHOO', 'matam')


    status, room_id = Room.add_room(2, 2, 1, 3, 'YAHOO', 'matam', True) ########################################changed capacity
    assert status is True
    status, room_id = Room.add_room(2, 1, 3, 4, 'YAHOO', 'matam', False)
    assert status is True
    assert Room.remove_room(room_id) is True
    status, room_id = Room.add_room(2, 1, 3, 4, 'YAHOO', 'matam', True)
    status, room_id = Room.add_room(2, 2, 4, 4, 'YAHOO', 'matam', True)

    num1 = Database.count('orders')
    Database.remove('orders', {'_id': '23/05/18'})
    num2 = Database.count('orders')
    Database.remove('orders', {'date': '26/05/18'})
    num3 = Database.count('orders')
    num_users1 = Database.count('users')
    Manager.user_register("email_1@gmail.com", '123', 'foox', '000002600', 'eng', 3, 'YAHOO', 'matam')
    Manager.user_register("email_4@gmail.com", '123', 'yan', '026000000', 'eng', 3, 'YAHOO', 'matam')
    Manager.user_register("email_6@gmail.com", '456', 'bim', '313324360', 'eng', 3, 'YAHOO', 'matam')
    num_users2 = Database.count('users')
    user2 = User.get_by_email('email_4@gmail.com')
    user3 = User.get_by_email('email_6@gmail.com')

    manager = Manager.get_by_email('user@yahoo.com')
    assert manager is None
    manager = Manager.get_by_email('admin@yahoo.com')
    assert manager is not None
    try:
        manager.import_rooms(os.getcwd() + '\\rooms.csv')
        manager.import_employee(os.getcwd() + '\\employee.csv')
    # should'nt works on travis
    except Exception as e:
        pass
    num_users2 = Database.count('users')

    user1 = User.get_by_email('email_1@gmail.com')
    user2 = User.get_by_email('email_4@gmail.com')
    user3 = User.get_by_email('email_6@gmail.com')
    participants1 = ['email_1@gmail.com', 'email_2@gmail.com']
    participants2  =['email_4@gmail.com']
    participants3 = ['email_7@gmail.com' , 'email_8@gmail.com']
    date = datetime.utcnow().strftime('%d/%m/%y')
    #date ='12/06/18'
    status2, string2 = user2.new_order(date, participants2, 6, 7, "YAHOO", 'matam')
    schedules2 = user2.get_schedule()

    status1, string1 = user1.new_order(date, participants1, 6, 7, "YAHOO", 'matam')
    schedules1 = user1.get_schedule()
    schedules2 = user2.get_schedule()

    status1, string1 = user3.new_order(date, participants3, 7, 8, "YAHOO", 'matam')
    schedules1 = user1.get_schedule()
    schedules2 = user2.get_schedule()
    schedules3 = user3.get_schedule()
    assert  len(schedules1) > 0
    assert len(schedules2) > 0
    assert len(schedules3) == 0

    print(string1)

    orders = user1.get_orders()
    num_orders = len(orders)
    assert len(user1.get_orders()) > 0
    schedules1 = user1.get_schedule()
    assert len(schedules1) > 0
    schedules = Schedule.get_schedules('email_1@gmail.com')
    assert len(Schedule.get_by_room("YAHOO matam 1")) > 0
    schedules2 = user2.get_schedule()
    assert len(schedules2) > 0



def test_facilities():
    Database.initialize()
    # add company

    status = Facilities.is_company_exist('google')
    assert status != Facilities.add_company('google', 'matam')
    status = Facilities.is_company_exist('yahoo')
    assert status != Facilities.add_company('yahoo', 'matam')
    status = Facilities.is_company_exist('microsoft')
    assert status != Facilities.add_company('microsoft', 'matam')
    status = Facilities.is_company_exist('vmware')
    assert status != Facilities.add_company('vmware', 'matam')
    status = Facilities.is_company_exist('intel')
    assert status != Facilities.add_company('intel', 'matam')
    # add facilities to each company

    status = Facilities.is_facility_exist('google', 'carmel')
    assert status != Facilities.add_facility('google', 'carmel')
    status = Facilities.is_facility_exist('yahoo', 'carmel')
    assert status != Facilities.add_facility('yahoo', 'carmel')
    status = Facilities.is_facility_exist('microsoft', 'carmel')
    assert status != Facilities.add_facility('microsoft', 'carmel')
    status = Facilities.is_facility_exist('vmware', 'carmel')
    assert status != Facilities.add_facility('vmware', 'carmel')
    status = Facilities.is_facility_exist('intel', 'carmel')
    assert status != Facilities.add_facility('intel', 'carmel')

    assert 'carmel' in Facilities.get_facilities('intel')
    assert 'matam' in Facilities.get_facilities('intel')
    assert 'carmel' in Facilities.get_facilities('vmware')
    assert 'matam' in Facilities.get_facilities('vmware')

    Facilities.remove_facility('vmware', 'carmel')
    assert 'carmel' not in Facilities.get_facilities('vmware')


def test_friends():
    Database.initialize()
    # Database.dropAll()

    Manager.manager_register("admin@yahoo.com", 'admin', 'Admin admin', '000000000', 'eng', 1, 'YAHOO', 'matam')
    Manager.user_register("email@gmail.com", '123', 'ely', '000000026', 'eng', 3, 'YAHOO', 'matam')
    Manager.user_register("user@yahoo.com", '123', 'yosi', '023412349', 'eng', 1, 'YAHOO', 'matam')
    Manager.user_register("user2@yahoo.com", '123', 'dave', '123412348', 'eng', 1, 'YAHOO', 'matam')
    Manager.user_register("email_1@gmail.com", '123', 'foox', '000002600', 'eng', 3, 'YAHOO', 'matam')
    Manager.user_register("email_2@gmail.com", '123', 'avi', '000260000', 'eng', 3, 'YAHOO', 'matam')
    Manager.user_register("email_3@gmail.com", '123', 'yin', '000000026', 'eng', 3, 'YAHOO', 'matam')
    Manager.user_register("email_4@gmail.com", '123', 'yan', '026000000', 'eng', 3, 'YAHOO', 'matam')

    user1 = User.get_by_email("email_1@gmail.com")
    user2 = User.get_by_email('email_2@gmail.com')
    user3 = User.get_by_email('email_3@gmail.com')
    user4 = User.get_by_email('email_4@gmail.com')

    emails = ["email_1@gmail.com", 'email_2@gmail.com', 'email_3@gmail.com', 'email_4@gmail.com', "user2@yahoo.com"]
    permission = User.min_permission(emails)
    assert permission == 1

    user1.add_friend('email_2@gmail.com')
    status, string = user1.add_friend('email_3@gmail.com')
    assert status is False
    user1.add_friend('email_4@gmail.com')

    assert user2.email in user1.get_friends_emails()
    assert user3 not in user1.get_friends_emails()
    assert user4.email in user1.get_friends_emails()

    user1.remove_friend('email_4@gmail.com')
    assert 'email_4@gmail.com' not in user1.get_friends_emails()

    assert 'email_1@gmail.com' in user2.get_friends_emails()
    assert not Friends.is_friends('email_1@gmail.com', 'email_4@gmail.com')
    assert Friends.is_friends('email_1@gmail.com', 'email_2@gmail.com')

    manager = Manager.get_by_email('admin@yahoo.com')

    assert len(user1.get_friends()) > 0

    manager.add_friend('email_1@gmail.com')

    assert user2 is not None
    assert manager.delete_user('email_2@gmail.com') is True


    def test_analytics():
        Database.initialize()

        Manager.manager_register("admin@yahoo.com", 'admin', 'Admin admin', '000000000', 'eng', 1, 'YAHOO', 'matam')
        Manager.user_register("email@gmail.com", '123', 'ely', '000000026', 'eng', 3, 'YAHOO', 'matam')
        Manager.user_register("user@yahoo.com", '123', 'yosi', '023412349', 'eng', 1, 'YAHOO', 'matam')
        Manager.user_register("user2@yahoo.com", '123', 'dave', '123412348', 'eng', 1, 'YAHOO', 'matam')
        Manager.user_register("email_1@gmail.com", '123', 'foox', '000002600', 'eng', 3, 'YAHOO', 'matam')
        Manager.user_register("email_2@gmail.com", '123', 'avi', '000260000', 'eng', 3, 'YAHOO', 'matam')
        Manager.user_register("email_3@gmail.com", '123', 'yin', '000000026', 'eng', 3, 'YAHOO', 'matam')
        Manager.user_register("email_4@gmail.com", '123', 'yan', '026000000', 'eng', 3, 'YAHOO', 'matam')

        assert Analytics.get_num_employees_company('YAHOO') == 8

        Manager.user_register("email_5@gmail.com", '123', 'yani', '026000001', 'eng', 3, 'YAHOO', 'matam')

        assert Analytics.get_num_employees_company('YAHOO') == 9

        Manager.manager_register("admin_herz@yahoo.com", 'admin_herz', 'Admin admin herz', '000000001', 'eng', 1, 'YAHOO', 'Herzeliya')
        Manager.user_register("email_herz1@gmail.com", '123', 'ely', '000000326', 'eng', 3, 'YAHOO', 'Herzeliya')
        Manager.user_register("user_herz2@yahoo.com", '123', 'yosi', '023414349', 'eng', 1, 'YAHOO', 'Herzeliya')

        assert Analytics.get_num_employees_company('YAHOO') == 12

        assert Analytics.get_num_employees_facility('YAHOO', 'Herzeliya') == 3

        Room.add_room(2, 2, 1, 3, 'YAHOO', 'matam', True)
        Room.add_room(2, 1, 3, 4, 'YAHOO', 'matam', False)

        assert Analytics.get_num_rooms_facility_simulation('YAHOO') == 2

        Room.add_room(2, 2, 1, 3, 'YAHOO', 'Herzeliya', True)
        Room.add_room(2, 1, 3, 4, 'YAHOO', 'Herzeliya', False)

        assert Analytics.get_num_rooms_facility('YAHOO') == 4
        assert Analytics.get_num_rooms_facility('YAHOO',  'Herzeliya') == 2


        user1 = User.get_by_email("email_1@gmail.com")
        user2 = User.get_by_email('email_2@gmail.com')
        user3 = User.get_by_email('email_3@gmail.com')
        user4 = User.get_by_email('email_4@gmail.com')