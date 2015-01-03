from shapely.wkt import loads
import re
from PyQt5.QtGui import *
from PyQt5.QtCore import *

#----------------------------------------------------------

class Map:
	def __init__(self):
		# Карта это прото список полигонов
		self.polygons = []

	def add(self, poly):
		"""Добавляет полигон на карту"""
		self.polygons.append(poly)

	def objects(self):
		"""Итератор для объектов карты"""
		for p in self.polygons:
			yield p		

	def bounding_box(self):
		"""Возвращает прямоугольник который описывает границы карты
		   https://ru.wikipedia.org/wiki/AABB

		   Тип результата: QRectF
		""" 
		#Задание!!!: реализовать эту функцию. Результат будет нужен для генерации случайных частиц		
		pass

	def min_distance_to(self, point, direction):
		"""Эта функция считает расстояние до ближайшего объекта карты в заданом направлении

		   Аргументы:
		   point -- точка от которой считаеться расстояние
		   direction -- направление заданное в градусах(от 0 до 359).
		"""
		pass


#----------------------------------------------------------

def load_map_from_wkt(filename):
	"""Эта фунция создает карту из текстового файла

	Фаил должен содержать полигоны в формате WKT(http://en.wikipedia.org/wiki/Well-known_text)
	"""
	pattern = 'POLYGON.?\(\([0-9,\. \-]+\)\)'
	result_map = Map() # Новая карта
	with open(filename) as f:
		content = f.readlines()
		for line in content:
			m = re.search(pattern, line)
			if m:
				poly = loads(m.group(0))				
				qpoly = QPolygonF() # Преобразуем в полигон из Qt
				for x, y in poly.exterior.coords:						
					qpoly.append(QPointF(x,y))
				result_map.add(qpoly) # Добавляем полигон к карте
	return result_map # Возвращаем карту