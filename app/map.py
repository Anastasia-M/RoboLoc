import re
import math

from shapely.wkt import loads
import shapely.geometry as gm

from PyQt5.QtGui import *
from PyQt5.QtCore import *

#----------------------------------------------------------

class Map:
	def __init__(self):
		# Карта это прото список полигонов
		self.polygons = []
		self.bbox = gm.box(0, 0, 0, 0)

	def add(self, poly):
		"""Добавляет полигон на карту"""
		self.polygons.append(poly)
		if self.bbox.area != 0:
			self.bbox = self.bbox.union(poly.envelope)
		else:
			self.bbox = poly.envelope

	def objects(self):
		"""Итератор для объектов карты"""
		for poly in self.polygons:
			# Преобразуем в qt тип
			yield QPolygonF([QPointF(x,y) for (x, y) in poly.exterior.coords])		

	def bounding_box(self):
		"""Возвращает прямоугольник который описывает границы карты
		   https://ru.wikipedia.org/wiki/AABB
		   Тип результата: QRectF
		"""		
		(xmin, ymin, xmax, ymax) = self.bbox.bounds
		# Преобразуем в qt тип 
		return QRectF(xmin, ymin, xmax - xmin, ymax - ymin)

	def is_occupied(self, x, y):
		"""Эта функция возвращает True если координаты (x,y) занаяты объктом карты, напривер стеной
		"""
		if self.bbox.contains(gm.Point(x,y)) == True:
			return True

		for poly in self.polygons:
			if poly.contains(gm.Point(x,y)):
				return True
		return False

	def min_distance_to(self, point, direction, max_range):
		"""Эта функция считает расстояние до ближайшего объекта карты в заданом направлении

		   Аргументы:
		   point -- точка от которой считаеться расстояние
		   direction -- направление заданное в радианаз(от 0 до 2*pi).
		   max_range -- максимальное растояние
		"""
		x, y = point
		end = (x + max_range * math.cos(direction), y + max_range * math.sin(direction))
		ray = gm.LineString([point, end])
		dist = max_range		
		start = gm.Point(point)
		for shape in self.polygons:
			z = shape.intersection(ray)
			if isinstance(z, gm.LineString):	
				for p in z.coords:
					d = start.distance(gm.Point(p))
					if d < dist:
						dist = d
						end = p
		return (dist, end)
		

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
				result_map.add(poly) # Добавляем полигон к карте

	return result_map # Возвращаем карту


#----------------------------------------------------------
# Тестовый код для карты
if __name__ == '__main__':
	import sys
	from PyQt5.QtCore import *
	from PyQt5.QtWidgets import *
	from PyQt5.QtGui import *

	class TestMap(QWidget):
		def __init__(self, parent=None):
			super(TestMap, self).__init__(parent)
			self.scene = QGraphicsScene()
			self.view = QGraphicsView()
			self.view.setScene(self.scene)
			self.view.setMinimumSize(800, 600)    
			mainLayout = QHBoxLayout()
			mainLayout.addWidget(self.view)
			self.setLayout(mainLayout)    	    
			self.setWindowTitle("Test map")

			# Создадим карту с парой тестовых объектов
			self.test_map = Map()
			self.test_map.add(gm.Polygon([(0,0), (0, 100), (10, 100), (10, 0)]))
			self.test_map.add(gm.Polygon([(90,0), (90, 100), (100, 100), (100, 0)]))				
			
			# Рисуем карту
			for poly in self.test_map.objects():
				self.scene.addPolygon(poly, QPen(Qt.NoPen), QBrush(QColor(179,112,123))) 
			self.view.fitInView(self.scene.sceneRect())

			# Тест нашего дальномера
			# Меряем растояние до стенок по 16 различным направления, и рисуем лучи дальномера
			for i in range(0, 16):
				direction = math.pi * 2 * i / 16.0
				res = self.test_map.min_distance_to((50, 50), direction, 60)
				if res != None:
					_, (x, y) = res
					line = QLineF(QPointF(50,50), QPointF(x,y))
					self.scene.addLine(line, QPen(QBrush(QColor(112,179,123)),0.5,Qt.DashLine)) 


	app = QApplication(sys.argv)

	screen = TestMap()
	screen.show()

	sys.exit(app.exec_())	