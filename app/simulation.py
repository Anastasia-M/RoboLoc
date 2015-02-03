from random import uniform
import math
import movement
from sensor import calculate_signal_probibility
import random
import map
from bisect import bisect_left
import pickle, os

#----------------------------------------------------------

def generate_random_particles(envmap, N):
	""" Эта функция генерирует N случайных частиц, равномерно расположеных на карте
		Используеться равномерное распределение
		Каждая частицы это кортеж вида: (x, y, dir), где x, y это координаты и dir это направление(ориентация)			 
	"""
	bbox = envmap.bounding_box()
	result = []
	while len(result) < N:		
		x = uniform(bbox.bottomLeft().x(), bbox.bottomRight().x())
		y = uniform(bbox.bottomLeft().y(), bbox.topLeft().y())
		# Сначала проверим что эти коондинаты свободны
		if envmap.is_occupied(x, y):
			continue
		# Добавляем новую частицу
		direction = uniform(0, 360) # Случайное направление в градусах
		result.append( (x, y, direction) )
	return result

#----------------------------------------------------------

class Simulation():
	""" Класс отвечает за симуляцию локализации робота
	"""
	def __init__(self, 	number_of_particles, number_of_sensors, envmap):
		# Ссылка на карту
		self.envmap = envmap
		# Сразу генерируем заданное число частиц
		self.particles_list = generate_random_particles(self.envmap, number_of_particles)
		# Реальные координаты робота
		self.robot_position = (430, 600, -math.pi/2)

		self.sensor_range = 500 
		self.movement_params = [0.1, 0.003, 0.08, 0.1]
		self.directions = [i * 2 * math.pi / number_of_sensors for i in range(0, number_of_sensors)]		
		self.occupancy_map_cell = 5
		filename = "belief_map_"+str(self.occupancy_map_cell)+".data"
		if os.path.exists(filename):
			self.occupancy_map = pickle.load(open(filename, 'rb'))
		else:
			self.occupancy_map = map.build_occupancy_map(self.envmap, self.occupancy_map_cell, self.sensor_range)
			pickle.dump(self.occupancy_map, open(filename, 'wb'))

	def particles(self):
		"""Итератор для частиц"""
		for p in self.particles_list:
			yield p		

	def read_sensors(self, pose):
		x, y, direction = pose				
		return [self.envmap.min_distance_to((x,y), direction + d, self.sensor_range) for d in self.directions]	

	def resample(self, weights, particles):
		for i in range(0, len(weights)):
			x, y, _ = self.particles_list[i]			
			if not self.envmap.contains(x,y) or self.min_distance(x, y) == 0:
				weights[i] = 0

		norm = sum(weights)
		weights[0] /= norm
		for i in range(1, len(weights)):
			weights[i] = weights[i] / norm + weights[i-1]

		indices = [bisect_left(weights, random.uniform(0, 1)) for i in range(0, len(weights))]
		return [particles[i] for i in indices]			

	def min_distance(self, x, y):
		if not self.envmap.contains(x,y):
			xmin, ymin, xmax, ymax = self.envmap.bbox.bounds
			return min([abs(e) for e in [ xmin - x, y - ymin, xmax - x, ymax -y ]])

		i = int(( x - self.envmap.bounding_box().x() ) / self.occupancy_map_cell)
		j = int(( y - self.envmap.bounding_box().y() ) / self.occupancy_map_cell)
		if i < 0 or i >= len(self.occupancy_map):
			return self.sensor_range
		if j < 0 or j >= len(self.occupancy_map[0]):
			return self.sensor_range
		return self.occupancy_map[i][j]	

	def move(self, new_position):
		return self.move_occupancy(new_position)

	def move_rays(self, new_position):
		#Применяем модель движения ко всем частицам
		control = movement.get_control(self.robot_position, new_position)
		new_particles = [movement.sample_odometry(self.movement_params, p, control) for p in self.particles_list]
		self.robot_position = new_position	
		actual_sensor = self.read_sensors(self.robot_position)

		weights = [ calculate_signal_probibility(actual_sensor, self.read_sensors(p)) for p in self.particles()]

		self.particles_list = self.resample(weights, new_particles)

		return actual_sensor


	def move_occupancy(self, new_position):
		#Применяем модель движения ко всем частицам
		control = movement.get_control(self.robot_position, new_position)
		new_particles = [movement.sample_odometry(self.movement_params, p, control) for p in self.particles_list]
		self.robot_position = new_position	
		actual_sensor = self.read_sensors(self.robot_position)

		weights = []


		for x, y, direction in new_particles:
			w = 1
			for d, (s,_) in zip(self.directions, actual_sensor):
				if s == self.sensor_range:
					w = w * (0.001 + 0.1)
				else:						
					xp = x + math.cos(d + direction) * s
					yp = y + math.sin(d + direction) * s
					dist = self.min_distance(xp, yp)
					w = w * (0.001 + 0.899*math.exp(-0.5 * dist * dist / 6400))
			weights.append(w)
		
		self.particles_list = self.resample(weights, new_particles)

		return actual_sensor