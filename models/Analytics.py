from common.database import Database

"""
    in this class we implement tools for the analytics
    
"""


class Analytics(object):
    @staticmethod
    def get_room_occupancy(room_id, facility_id, time):
        query = {'$and': [{'facility': facility_id}, {'room': room_id}]}
        room = Database.find_one('rooms', query)
        if room is None:
            return
        # TODO: implement get_occupancy (will be after room ordering is done)
        occupancy = room.get_occupancy(time)
        return occupancy/room.capacity

    @staticmethod
    def get_num_employees_facility(company_id, facility_id):

