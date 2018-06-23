import errno

from datetime import datetime, timedelta

from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
import sys

from common.Simulation import simulation_engine
from common.database import Database
import os
import subprocess

from models.Analytics import Analytics
from models.Room import Room
from models.Schedule import Schedule
from models.User import User, Manager

app = Flask(__name__)
app.secret_key = 'super secret key'
"""Here we write the routes function.
    which it mean that when we try to go to some url (/index)
    the function under that run"""
UPLOAD_FOLDER = sys.argv[0].replace('main.py', "uploads")

ALLOWED_EXTENSIONS = set(['csv'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

MAX_PERMISSION = 100

one_day = timedelta(days=1)


def get_week(date):
    """Return the full week (Sunday first) of the week containing the given date.

    'date' may be a datetime or date instance (the same type is returned).
    """
    day_idx = (date.weekday() + 1) % 7  # turn sunday into 0, monday into 1, etc.
    sunday = date - timedelta(days=day_idx)
    date = sunday
    for n in range(0, 7):
        yield date
        date += one_day


def add_user(req, manager):
    email = req.form['email']
    password = req.form['password']
    username = req.form['username']
    _id = req.form['id']
    permission = req.form['permission']
    facility = req.form['facility']
    role = req.form['role']
    if facility not in manager.get_facilities():
        manager.add_facility(facility)
    if role not in manager.get_roles():
        manager.add_roles(role)
    return manager.user_register(email, password, username, _id, role, permission, manager.company, facility)


def remove_user(req, manager):
    email = req.form['email']
    return manager.delete_user(email)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def import_users(request, manager):
    try:
        file = request.files['file']
        filename = secure_filename(file.filename)
        mkdir_p(UPLOAD_FOLDER)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        manager.import_employee(filename)
        flash('Import successfully')
    except Exception as e:
        flash('Import fail:\n' + str(e))


def p():
    p = subprocess.Popen('mongod', stdout=open(os.devnull, "w"))
    yield p
    p.terminate()


@app.route('/logout')
def logout():
    User.logout()
    return redirect(url_for('home'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    user = User.get_by_email(session['email'])
    if request.method == 'GET':
        return render_template('settings.html', manager=user.manager)
    else:
        if user.password != request.form['old_password']:
            flash("Wrong Password!")
        elif request.form['new_password'] != request.form['again']:
            flash("New Password Not Match!")
        else:
            user.update_user(user.username, request.form['again'], user.role, user.permission, user.facility)
            flash("Password Changed Successfully!")
        return redirect(url_for('settings'))


@app.route('/')
def home():
    # Todo
    # return render_template('friends_page.html')
    try:
        if session['email'] is not None:
            user = User.get_by_email(session['email'])
            if user.manager:
                return redirect(url_for('route_analytics'))
            else:
                return redirect(url_for('route_edit_friends'))
    except Exception as e:
        return render_template('page-login.html', wrong_password=False)
    return render_template('page-login.html', wrong_password=False)


@app.route('/login', methods=['POST', 'GET'])
def login_user():
    email = request.form['email']
    password = request.form['password']
    if User.login_valid(email, password):
        User.login(email)
        if Manager.get_by_email(email) is not None:
            return redirect(url_for('route_analytics'))
        elif User.get_by_email(email) is not None:
            return redirect(url_for('route_reservations'))
    else:
        User.logout()
        return render_template('page-login.html', wrong_password=True, email=email)
    return 'hello' + email


@app.route('/register', methods=['GET', 'POST'])
def manager_register():
    if request.method == 'GET':
        return render_template('page-register.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        company = request.form['company']
        facility = request.form['facility']
        username = request.form['username']
        _id = request.form['_id']
        status, info = Manager.manager_register(email, password, username, _id, 'Manager', MAX_PERMISSION,
                                                company,
                                                facility)
        if status:
            User.login(email)
            return redirect(url_for('route_analytics'))
        else:
            flash(info)
            return redirect(url_for('manager_register'))


@app.route('/simulation', methods=['GET', 'POST'])
def route_simulation():
    if request.method == 'GET':
        Database.dropAllSimulation()
        return render_template('Simulation.html', employees_no=0, rooms_no=0, facility_no=0,
                               meetings_no=0, facility_visits_meetings=[("None", 0, 0)],
                               occupancies=[("None", 0)])
    if request.method == 'POST':
        if session['email'] is not None:
            Database.dropAllSimulation()
            duration = int(request.form['duration'])
            max_rooms = int(request.form['room'])
            max_employees = int(request.form['employee'])
            max_facilities = int(request.form['facility'])
            a=simulation_engine(max_rooms, max_employees, max_facilities, duration)
            flash(a)
            manager = Manager.get_by_email_simulation("simulation@gmail.com")
            flash(manager)
            return render_template('Simulation.html', employees_no=0, rooms_no=0, facility_no=0,
                                   meetings_no=0, facility_visits_meetings=[("None", 0, 0)],
                                   occupancies=[("None", 0)])
            employees_no = len(manager.get_employees_simulation())
            facility_no = len(manager.get_facilities_simulation())
            facility_visits_meetings = []
            facilities = manager.get_facilities_simulation()
            for facility in facilities:
                visits = Analytics.get_all_participants_in_facility_simulation(manager, facility, duration)
                meetings = Analytics.get_meetings_number_in_facility_simulation(manager, facility, duration)
                facility_visits_meetings.append((facility, visits, meetings))
            rooms_no = len(Room.get_by_company_simulation(manager.company))
            occupancies = Analytics.get_all_rooms_occupancy_simulation(manager, duration)
            meetings_no = Analytics.get_meeting_number_simulation(manager, duration)
            return render_template('Simulation.html', employees_no=employees_no, rooms_no=rooms_no,
                                   facility_no=facility_no,
                                   meetings_no=meetings_no, facility_visits_meetings=facility_visits_meetings,
                                   occupancies=occupancies)


@app.route('/analytics', methods=['GET'])
def route_analytics():
    manager = Manager.get_by_email(session['email'])
    if session['email'] is not None and manager is not None:
        employees_no = len(manager.get_employees())
        facility_no = len(manager.get_facilities())
        facility_visits_meetings = []
        facilities = manager.get_facilities()
        for facility in facilities:
            visits = Analytics.get_all_participants_in_facility(manager, facility)
            meetings = Analytics.get_meetings_number_in_facility(manager, facility)
            facility_visits_meetings.append((facility, visits, meetings))
        rooms_no = len(Room.get_by_company(manager.company))
        occupancies = Analytics.get_all_rooms_occupancy(manager)
        meetings_no = Analytics.get_meeting_number(manager)
        return render_template('Analytics.html', employees_no=employees_no, rooms_no=rooms_no, facility_no=facility_no,
                               meetings_no=meetings_no, facility_visits_meetings=facility_visits_meetings,
                               occupancies=occupancies)


def get_user_roles_facilities(manager):
    roles = manager.get_roles()
    facilities = manager.get_facilities()
    users = manager.get_employees()
    return users, roles, facilities


@app.route('/employee_datatable', methods=['GET', 'POST'])
def route_employee_datatable():
    manager = Manager.get_by_email(session['email'])
    if session['email'] is not None and manager is not None:
        if request.method == 'GET':
            users, roles, facilities = get_user_roles_facilities(manager)
            return render_template('Employee-datatable.html', users=users, roles=roles, facilities=facilities)
        elif request.method == 'POST':
            if request.form['type'] == 'add_user':
                status, info = add_user(request, manager)
                if status:
                    flash('Added successfully')
                else:
                    flash('Failed:\n' + info)
            elif request.form['type'] == 'remove_user':
                if remove_user(request, manager):
                    flash("Deleted Successfully")
                else:
                    flash("Delete Failed")
            elif request.form['type'] == 'import_users':
                import_users(request, manager)
            return redirect(url_for('route_employee_datatable'))


def get_rooms_facilities(manager):
    rooms = manager.get_rooms()
    facilities = manager.get_facilities()
    return rooms, facilities


def add_room(request, manager):
    permission = request.form['permission']
    floor = request.form['floor']
    facility = request.form['facility']
    disabled_access = request.form['disabled_access']
    capacity = request.form['capacity']
    room_num = request.form['room_name']
    if facility not in manager.get_facilities():
        manager.add_facility(facility)
    return manager.add_room(permission, capacity, room_num, floor, facility, disabled_access)


def remove_room():
    room_to_remove = request.form['room_id']
    Room.remove_room(room_to_remove)


def import_rooms(request, manager):
    try:
        file = request.files['file']
        filename = secure_filename(file.filename)
        mkdir_p(UPLOAD_FOLDER)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        manager.import_rooms(filename)
        flash('Import successfully')
    except Exception as e:
        flash('Import fail:\n' + str(e))


@app.route('/rooms_datatable', methods=['GET', 'POST'])
def route_rooms_datatable():
    manager = Manager.get_by_email(session['email'])
    if session['email'] is not None and manager is not None:

        if request.method == 'GET':
            rooms, facilities = get_rooms_facilities(manager)
            return render_template('Rooms-datatable.html', rooms=rooms, facilities=facilities)
        elif request.method == 'POST':
            if request.form['type'] == 'add_room':
                status, info = add_room(request, manager)
                if status:
                    flash("Added Successfully")
                else:
                    flash('Fail:\n' + info)
            elif request.form['type'] == 'remove_room':
                if remove_room():
                    flash("Deleted Successfully")
                else:
                    flash("Delete Failed")
            elif request.form['type'] == 'import_rooms':
                import_rooms(request, manager)
            # rooms, facilities = get_rooms_facilities(manager)
            return redirect(url_for('route_rooms_datatable'))
            # return render_template('Rooms-datatable.html', rooms=rooms, facilities=facilities)


@app.route('/edit_friends', methods=['GET', 'POST'])
def route_edit_friends():
    if session['email'] is not None:
        email = session['email']
        user = User.get_by_email(email)
        if request.method == 'GET':
            friends = user.get_friends_emails()
            possible_friends = [friend.email for friend in User.get_by_company(user.company) if
                                friend.email not in friends and friend.email != email]
            friends = user.get_friends()
            print(str(user.manager) + '   ' + user.email)
            return render_template('friends_page.html', manager=user.manager, friends=friends,
                                   possible_friends=possible_friends)
        elif request.method == 'POST':
            if request.form['type'] == 'add_friend':
                user.add_friend(request.form['email'])
            if request.form['type'] == 'remove_friend':
                user.remove_friend(request.form['email'])
        return redirect(url_for('route_edit_friends'))


def convert_date():
    date = datetime.strptime(request.form['date'], '%Y-%m-%d')
    day = str(date.day) if date.day > 9 else '0' + str(date.day)
    month = str(date.month) if date.month > 9 else '0' + str(date.month)
    year = str(date.year)[2:]
    date = day + '/' + month + '/' + year
    return date


def reserve_room():
    participants = list(request.form.getlist('participants', None))
    date = convert_date()

    start_time = request.form['start']
    meeting_duration = request.form['duration']
    user = User.get_by_email(session['email'])
    end_time = str(int(start_time) + int(meeting_duration))
    status, info = user.new_order(date, participants, start_time, end_time, user.company,
                                  user.facility)
    if not status:
        if isinstance(info, str):
            flash('Fail!\n' + info)
        else:
            str1 = ' '.join(info)
            flash('Fail!\n Those participants already have meeting on this time ' + str1)
    elif status:
        flash('Meeting create successfully')


@app.route('/reserve_room', methods=['GET', 'POST'])
def route_reserve_room():
    if session['email'] is not None:
        email = session['email']
        user = User.get_by_email(email)
        friends = user.get_friends_emails()
        if request.method == 'GET':
            return render_template('order.html', manager=user.manager, friends=friends)
        elif request.method == 'POST':
            if get_day(convert_date()) == 'Saturday' or get_day(convert_date()) == 'Friday':
                flash('This day is not working day.')
            else:
                reserve_room()
    return redirect(url_for('route_reserve_room'))


@app.route('/my_reservations', methods=['POST'])
def route_cancel_reserve_room():
    return
    # if session['email'] is not None:
    #     email = session['email']
    #     user = User.get_by_email(email)
    #     friends = user.get_friends_emails()
    #     if request.method == 'GET':
    #         return render_template('order.html', manager=user.manager, friends=friends)
    #     elif request.method == 'POST':
    #         reserve_room()
    # return redirect(url_for('route_reserve_room'))


@app.route('/my_reservations', methods=['GET'])
def route_reservations():
    if session['email'] is not None:
        email = session['email']
        user = User.get_by_email(email)
        meetings = []
        for day in get_week(datetime.today().date()):
            d = str(day.day) if day.day > 9 else '0' + str(day.day)
            month = str(day.month) if day.month > 9 else '0' + str(day.month)
            year = str(day.year)[2:]
            date = '{}/{}/{}'.format(d, month, year)
            scheds = user.get_schedule(date)
            if len(scheds) > 0:
                meetings = meetings + scheds
        return render_template('reservation.html', manager=user.manager, meetings=meetings)


@app.before_first_request
def initialize_database():
    # p()
    Database.initialize()


@app.route('/event_abs_circuit.html', methods=['GET'])
def event_abs_circuit():
    return render_template('event-abs-circuit.html')


@app.route('/meeting_info', methods=['GET', 'POST'])
def meeting_info():
    email = session['email']
    user = User.get_by_email(email)
    meeting = Schedule.get_by_id(request.form.get('meeting_id'))
    return render_template('meeting.html', manager=user.manager, meeting=meeting)


@app.route('/meeting_cancel', methods=['GET', 'POST'])
def meeting_cancel():
    if session['email'] is not None:
        email = session['email']
        user = User.get_by_email(email)
        user.cancel_meeting(request.form.get('meeting_id'))
    return redirect(url_for('route_reservations'))


def get_day(date):
    date = datetime.strptime(date, '%d/%m/%y')
    return str(date.strftime("%A"))


if __name__ == '__main__':
    app.debug = True
    # for day in get_week(datetime.today().date()):
    #     date = '{}/{}/{}'.format(day.day, day.month, str(day.year)[2:4])
    #     print(date)
    app.run()
