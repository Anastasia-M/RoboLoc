
class Simulation():
	def __init__(number_of_particles):
		# В этом списке мы будем хранить наши частицы
		self.particles = self.generate_random_particles(number_of_particles)
		# Реальные координаты робота
		self.robot_position = (0, 0)
	
	def generate_random_particles(self, N):
		""" Эта функция генерирует N случайных частиц, равномерно расположеных на карте
			Используеться равномерное распределение
			Каждая частицы это кортеж вида: (x, y, dir), где x, y это координаты и dir это направление(ориентация)			 
		"""
		#Задание!!!: написать эту функцию. Для этого нужно знать bounding-box карты, смотри задание map.py
		pass

	def particles(self):
		"""Итератор для частиц"""
		for p in self.particles:
			yield p		



