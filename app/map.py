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
		self.bounds = self.bbox.bounds

	def add(self, poly):
		"""Добавляет полигон на карту"""
		self.polygons.append(poly)
		if self.bbox.area != 0:
			self.bbox = self.bbox.union(poly.envelope)
		else:
			self.bbox = poly.envelope
		self.bounds = self.bbox.bounds

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
		(xmin, ymin, xmax, ymax) = self.bounds
		# Преобразуем в qt тип 
		return QRectF(xmin, ymin, xmax - xmin, ymax - ymin)

	def contains(self, x, y):
		return self.bounding_box().contains(QPointF(x,y))


	def is_occupied(self, x, y):
		"""Эта функция возвращает True если координаты (x,y) занаяты объктом карты, напривер стеной
		"""
		#if self.contains(x, y) == True:
		#	return True

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


	def min_distance(self, point, max_range):
		"""Эта функция считает расстояние до ближайшего объекта карты во всех напрявлениях

		   Аргументы:
		   point -- точка от которой считаеться расстояние
		   max_range -- максимальное растояние
		"""
		start = gm.Point(point)
		dist = max_range		
		for shape in self.polygons:
			d = start.distance(shape)
			if d < dist:
				dist = d
		return dist		

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

def build_occupancy_map(envmap, cell_size, max_range):
	result = []
	(xmin, ymin, xmax, ymax) = envmap.bbox.bounds
	for iw in range(0, int((xmax-xmin)/cell_size)):
		x = xmin + (iw + 0.5)*cell_size
		col = []
		for ih in range(0, int((ymax - ymin)/cell_size)):
			y = ymin + (ih + 0.5)*cell_size
			col.append(envmap.min_distance((x,y), max_range))
		result.append(col)
	return result


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
			self.test_map.add(gm.Polygon([(45,20), (45, 30), (55, 30), (55, 20)]))				

			#Тестируем "карту заполнености
			occupancy_map = build_occupancy_map(self.test_map, 1, 100)

			image = QImage(100,100, QImage.Format_RGB32)
			for i in range(0,len(occupancy_map)):
				for j in range(0,len(occupancy_map[i])):
					image.setPixel(i, j, 255*occupancy_map[i][j] / 50)
			self.scene.addRect(self.test_map.bounding_box(), QPen(Qt.NoPen), QBrush(image))

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