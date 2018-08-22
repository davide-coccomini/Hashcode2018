#!/usr/bin/python

import sys
from tqdm import tqdm

class Car(object):
	def __init__(self, id, row, col):
		self.id = id
		self.row = row
		self.col = col
		self.dest = (-1, -1)
		self.taken = False
		self.empty = True
		self.rides = []

		self.best_rides = []

	def at_destination(self):
		return (self.row, self.col) == self.dest

	def move(self):
		if self.row != self.dest[0]:
			inc = 1 if self.dest[0] > self.row else -1
			self.row += inc
		else:
			inc = 1 if self.dest[1] > self.col else -1
			self.col += inc

class Map(object):
	def __init__(self, rows, cols, ncars, nrides, bonus, turns, rides):
		self.rows = rows
		self.cols = cols
		self.ncars = ncars
		self.nrides = nrides
		self.bonus = bonus
		self.turns = turns

		self.cars = []
		for i in range(1, self.ncars+1):
			self.cars.append(Car(i, 0, 0))

		self.rides = rides

class Ride(object):
	def __init__(self, id, r_start, c_start, r_end, c_end, t_start, t_end):
		self.id = id
		self.r_start = r_start
		self.c_start = c_start
		self.r_end = r_end
		self.c_end = c_end
		self.turn_start = t_start
		self.turn_end = t_end
		self.car = None
		self.arrived = False
		self.instant = False

	def __repr__(self):
		return "Ride {} ({},{}) => ({},{}) [{},{}]".format( \
				self.id, self.r_start, self.c_start, self.r_end, self.c_end, \
				self.turn_start, self.turn_end)

def read_from_file(input_file):
	rides = []
	id = 0
	with open(input_file, "r") as f:
		rows, cols, ncars, nrides, bonus, turns = [int(v) for v in (f.readline()[:-1]).split(" ")]

		for line in f:
			r_start, c_start, r_end, c_end, t_start, t_end = [int(x) for x in (line[:-1]).split(" ")]
			rides.append(Ride(id, r_start, c_start, r_end, c_end, t_start, t_end))
			id += 1

	my_map = Map(rows, cols, ncars, nrides, bonus, turns, rides)
	return my_map

def distance(car, ride):
	return abs(car.row - ride.r_start) + abs(car.col-ride.c_start) + \
		abs(ride.r_start - ride.r_end) + abs(ride.c_start - ride.c_end)

def distance_to_point(start, end):
	return abs(start[0]-end[0])+abs(start[1]-end[1])

def find_best_rides(car, rides, current_turn):
	# Sort rides with preference
	for r in rides:
		if distance(car, r) + current_turn >= r.turn_end:
			rides.remove(r)

	if not len(rides): return []

	rides.sort(key=lambda r: (\
		r.turn_start - current_turn if r.turn_start>=current_turn else 999999, \
		distance(car, r)
	))
	
	ride_short_distance = rides[0]
	
	rides.sort(key=lambda r: (
		r.turn_start - current_turn if r.turn_start>=current_turn else 999999,
		distance(car, r), \
		(distance_to_point(
			(ride_short_distance.r_end, ride_short_distance.c_end),
			(r.r_start, r.c_start)
		) + \
		distance_to_point((r.r_start, r.c_start), (r.r_end, r.c_end))
		) if r.id != ride_short_distance.id else 0
	))
	return rides


def run(my_map):
	
	for current_turn in tqdm(range(my_map.turns)):
		empty_car = list(filter(lambda c: not c.taken, my_map.cars))
		waiting_ride = list(filter(lambda r: r.car is None, my_map.rides))

		for car in empty_car:
			car.best_rides = find_best_rides(car, waiting_ride, current_turn)

		#empty_car.sort(key=lambda c: len(c.best_rides))

		for index, car in enumerate(empty_car):
			ride = car.best_rides[0] if len(car.best_rides) else None

			if ride:
				for j in range(index+1, len(empty_car)):
					if ride in empty_car[j].best_rides:
						empty_car[j].best_rides.remove(ride)
				
				car.taken = True
				car.dest = (ride.r_start, ride.c_start)
				car.rides.append(ride)
				my_map.rides.remove(ride)

		taken_cars = list(filter(lambda c: c.taken, my_map.cars))
		for car in taken_cars:
			current_ride = car.rides[-1]
			
			if car.taken and car.empty and car.at_destination():
				car.empty=False
				current_ride.car = car
				car.dest = (current_ride.r_end, current_ride.c_end)

			if car.taken and not car.at_destination() or \
			car.taken and not car.empty and current_ride.t_start>=current_turn:
				car.move()

			if car.taken and not car.empty and car.at_destination():
				car.empty = True
				car.taken= False
				current_ride.arrived=True
				current_ride.instant = current_turn <= current_ride.turn_end

def write_output(my_map, output_file):
	with open(output_file, "w+") as f:
		for car in my_map.cars:
			f.write(' '.join([str(len(car.rides))] + [str(r.id) for r in car.rides]) +'\n')

	if len(list(filter(lambda r: r.car is None, my_map.rides))):
		print("Some ride wasn't served")
		return

	for car in my_map.cars:
		my_map.nrides -= len(car.rides)
		for ride in car.rides:
			if not ride.arrived:
				print("Some ride wasn't arrived")
				return
			elif not ride.instant:
				print("turn_arrive > turn_end")
				return

	if my_map.nrides != 0:
		print("Not all ride was served")
	return

def main():
	my_map = read_from_file(sys.argv[1])

	run(my_map)

	write_output(my_map, sys.argv[2])

if __name__=="__main__":
	main()
