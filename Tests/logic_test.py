def test_logic():
	best_rooms = {1: 4, 3: 5, 2: 4}
	sorted_rooms = sorted(best_rooms.items(), key=lambda y: y[1])
	print(sorted_rooms[::-1])
	for x in sorted_rooms:
		print(x[1])