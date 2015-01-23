from random import uniform
import math
import movement
from sensor import calculate_signal_probibility
import random
from bisect import bisect_left

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

def get_control(old_position, new_position):
	x_s, y_s, dir_s = old_position
	x_e, y_e, dir_e = new_position
	return (x_e - x_s, y_e - y_s, dir_e - dir_s)
	
#----------------------------------------------------------

class Simulation():
	""" Класс отвечает за симуляцию локализации робота
	"""
	def __init__(self, 	number_of_particles, envmap):
		# Ссылка на карту
		self.envmap = envmap
		# Сразу генерируем заданное число частиц
		self.particles_list = generate_random_particles(self.envmap, number_of_particles)
		# Реальные координаты робота
		self.robot_position = (430, 600, -math.pi/2)
		self.number_of_sensors = 8
		self.sensor_range = 500 
		self.movement_params = [0.1,0.001, 0.05, 0.1]
		self.directions = [i * 2 * math.pi / self.number_of_sensors for i in range(0, self.number_of_sensors)]
		

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
			if self.envmap.is_occupied(x, y):
				weights[i] = 0

		norm = sum(weights)
		weights[0] /= norm
		for i in range(1, len(weights)):
			weights[i] = weights[i] / norm + weights[i-1]

		indices = [bisect_left(weights, random.uniform(0, 1)) for i in range(1, len(weights))]
		return [particles[i] for i in indices]			


	def move(self, new_position):
		#Применяем модель движения ко всем частицам
		control = get_control(self.robot_position, new_position)
		new_particles = [movement.sample_odometry(self.movement_params, p, control) for p in self.particles_list]
		self.robot_position = new_position	
		actual_sensor = self.read_sensors(self.robot_position)

		weights = [ calculate_signal_probibility(actual_sensor, self.read_sensors(p)) for p in self.particles()]

		self.particles_list = self.resample(weights, new_particles)

		return actual_sensor
