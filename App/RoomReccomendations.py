class Recommendation:
	def __init__(self, room_table, employee_table):
		self.Rooms = room_table
		self.Employees = employee_table

	def recommend_by_friends(self, employee):
		"""return list of rooms 'res' that highly recommended for employee """
		rec_room = employee.recommendation_by_friends()
		res = []
		for room in rec_room:
			room_tmp = self.Rooms.find({"id": room[0]})
			if room.current_occupancy <= room_tmp.capcity:
				res.append(room[0])
		return res

	def reccomendationToEmployeeByRoom(self, date_time, occupancy):
		reccomendedList = []
		for room in self.Rooms.find():
			if occupancy <= room.maxCapacity - room.schedule[date_time].occupancy:
				reccomendedList.append(room)
		return reccomendedList

	# input: time requested to check num of empty places in each room.
	# output: a dictionary that for each room include the number of empty seats in that room in the given time.
	def emptyRooms(self, time):
		emptyPlaceInRooms = {}
		for room in self.Rooms.find():
			emptyPlaceInRooms.update(room.id, room.maxCapacity - room.schedule[time].occupancy)
		return emptyPlaceInRooms

	def room_with_my_friends(self, friends):
		"""this fun get list of friends which the user want to be with (in the same room) and return the room that
		the biggest sub group in it"""
		rooms = {}
		for friend in friends:
			location = friend.get_location()
			if location is not None:
				count = rooms.get(location, default=0) + 1
				rooms += (location, count)
		sorted_rooms = sorted(rooms, key=lambda x: x[1])
		return sorted_rooms[-1]
