from Database.ManageDB import update_employee


class Employee:
    def __init__(self, id, name, role, access_permission):
        self.id = id
        self.name = name
        self.role = role
        self.access_permission = access_permission
        self.friends = []
        self.schedule = {}
        self.location = None

    def entrance_room(self, room):
        self.location = room

    def exit_room(self):
        self.location = None

    def recommendation_by_friends(self):
        """"return sorted list of rooms 'sorted_room' sorted by friends location"""
        best_rooms = {}
        for friend in self.friends:
            if friend.get_location() is not None and friend.get_room_permission() < self.access_permission:
                count = best_rooms.get(friend.location, 0) + 1
                best_rooms += {friend.location, count}
        sorted_rooms = sorted(best_rooms.items(), key=lambda x: x[1])
        return sorted_rooms[::-1]  # reverse list

    def get_location(self):
        """return Room object or None"""
        return self.location

    def get_curr_room_permission(self):
        cur_room = self.get_location()
        if cur_room is None:
            raise "%d employee is not in a room right now".format(self.id)
        return cur_room.get_permission()

    def add_friends(self, friends):
        self.friends += friends
        update_employee(self.id, self.name, self.role, self.access_permission, self.friends, self.schedule)

    def remove_friends(self, friends):
        """
        update the list of friends of self and write it to DB
        :param friends: it is a list of id's of friends
        """
        for friend in friends:
            self.friends.remove(friend)
        update_employee(self.id, self.name, self.role, self.access_permission, self.friends, self.schedule)

    def add_schedules(self, schedules):
        """
        update the dictionary of schedules of self and write it to DB
        :param schedules: assume it is a dictionary {k: date_time v: (num_employee, room_id )}
        """
        self.schedule.update(schedules)
        update_employee(self.id, self.name, self.role, self.access_permission, self.friends, self.schedule)

    def change_permission(self, permission):
        self.access_permission = permission
        update_employee(self.id, self.name, self.role, self.access_permission, self.friends, self.schedule)

    def change_role(self, role):
        self.role = role
        update_employee(self.id, self.name, self.role, self.access_permission, self.friends, self.schedule)
