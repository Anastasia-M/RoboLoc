from random import uniform
import math

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
	def __init__(self, 	number_of_particles, envmap):
		# Ссылка на карту
		self.envmap = envmap
		# Сразу генерируем заданное число частиц
		self.particles_list = generate_random_particles(self.envmap, number_of_particles)
		# Реальные координаты робота
		self.robot_position = (400, 400, -math.pi/2)

	def particles(self):
		"""Итератор для частиц"""
		for p in self.particles_list:
			yield p		

	def move(self, new_position):
		sensor = [self.envmap.min_distance_to(new_position, 2 * i * math.pi / N) for i in range(1, N)]	

