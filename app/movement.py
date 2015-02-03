""" Модель движения

Этот молуль содердит определение вероятностной модели движения робота в 2D пространсве
"""

import math
import random

#----------------------------------------------------------
#
#
def normal_angle(angle):
    while angle < 0:
        angle += 2 * math.pi;
    while angle > 2 * math.pi:
        angle -= 2 * math.pi;
    return angle;

#----------------------------------------------------------

def get_control(old_position, new_position):
	x_s, y_s, dir_s = old_position
	x_e, y_e, dir_e = new_position
	dx = x_e - x_s
	dy = y_e - y_s

	start_rotation = normal_angle(math.atan2(dy, dx) - dir_s)
	transition = math.sqrt(dx * dx + dy * dy)
	end_rotation = normal_angle(dir_e - dir_s - start_rotation)
	
	return (start_rotation, transition, end_rotation)

#----------------------------------------------------------

def sample_odometry(np, start, control):
	""" 
	"""
	x_s, y_s, dir_s = start
	start_rotation, transition, end_rotation = control

    # параметры шума 
	params = [np[0] * start_rotation + np[1] * transition, np[2] * transition + np[3] * (start_rotation + end_rotation), np[0] * end_rotation + np[1] * transition]
    
    # применяем шум
	start_rotation -= random.gauss(0, params[0])
	transition -= random.gauss(0, params[1])
	end_rotation -= random.gauss(0, params[2])

	return (x_s + transition * math.cos(dir_s + start_rotation),
            y_s + transition * math.sin(dir_s + start_rotation),
            normal_angle(dir_s + start_rotation + end_rotation))


#----------------------------------------------------------
# Тестируем модель движения
if __name__ == '__main__':
	import numpy as np
	import matplotlib.pyplot as plt

	def add_subplot(noise, start, end):
		# Построим 100 зашумленных результатов 
		samples = [sample_odometry(noise, start, end) for i in range(0, 600)]		
		x = [x for (x, _, _) in samples]
		y = [y for (_, y, _) in samples]
		plt.scatter(x, y, alpha = 0.2)
		plt.scatter([start[0]], start[1], s = 100, c='r', marker='^')
		plt.scatter([end[0]], end[1], s = 100, c='r', marker='>')
		plt.text(start[0], start[1], '  start')
		plt.text(end[0], end[1], '  end')

	#Без шума
	plt.subplot(221)
	plt.title('Без шума')
	add_subplot(noise=[0,0,0,0], start =(10, 10, math.radians(0)), end = (40, 40, math.radians(90)))

	#Шум только поворота
	plt.subplot(222)
	plt.title('Шум только поворота')
	add_subplot(noise=[0.1,0.001,0,0], start =(10, 10, math.radians(0)), end = (30, 30, math.radians(90)))

	#Шум только поступательного движения
	plt.subplot(223)
	plt.title('Шум поступательного движения')
	add_subplot(noise=[0,0,0.1,0.1], start =(10, 10, math.radians(0)), end = (30, 30, math.radians(90)))

	#Шум
	plt.subplot(224)
	plt.title('Шум и повотора и поступательного движения')
	add_subplot(noise=[0.1,0.001, 0.05, 0.1], start =(10, 10, math.radians(0)), end = (30, 30, math.radians(90)))
	
	plt.show()