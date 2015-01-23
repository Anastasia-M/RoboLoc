""" Модель сенсора

"""
import math

def range_probibility(z, ze):
	sigma2 = 6000
	sqrt2sigma = math.sqrt(2 * sigma2)
	return 0.001 + math.exp(-0.5 * (z - ze) * (z - ze) / sigma2) / sqrt2sigma


def calculate_signal_probibility(measured, expected):
	total_probibility = 1.0
	for (m,_),(e,_) in zip(measured, expected):
		total_probibility *= range_probibility(m, e)
	return total_probibility

 
#----------------------------------------------------------
# Тестируем сенсор
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
	y = [range_probibility(x, 250) for x in range(0, 500)]
	plt.plot(y)
	plt.show()
