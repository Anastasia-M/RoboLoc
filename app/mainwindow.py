# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from map import *
from simulation import *
import math

#------------------------------------------------------------------------------
#
class SceneObjects:
	def __init__(self, graphics_scene):
		self.scene = graphics_scene		
		self.particles = None
		self.cursor = None
		self.sensor_beams = None

	def draw_robot(self, pose):
		x, y, direction = pose
		sx, sy = math.cos(direction), math.sin(direction)
		sx1, sy1 = -math.sin(direction), math.cos(direction)

		poly = QPolygonF()
		poly.append(QPointF(x + 20*sx, y + 20*sy))
		poly.append(QPointF(x + 8*sx1, y + 8*sy1))
		poly.append(QPointF(x - 8*sx1, y - 8*sy1))

		if self.cursor == None:
			self.cursor = self.scene.addPolygon(poly, QPen(QColor(0,0,0)), QBrush(QColor(255,0,0)))
		else:
			self.cursor.setPolygon(poly)	


	def draw_particles(self, plist):		
		if self.particles == None:
			self.particles = [self.scene.addEllipse(x - 2, y - 2, 4, 4) for (x, y, _) in plist] 			
		else:
			i = 0
			for (x,y,direction) in plist:
				self.particles[i].sceneRect(x - 2, y - 2, 4, 4)		
				i+=1

	def draw_sensor(self, pose, sensor):
		robot_x, robor_y, _ = pose
		lines = [QLineF(QPointF(robot_x, robor_y), QPointF(x,y)) for _,(x,y) in sensor]
		if self.sensor_beams == None:
			self.sensor_beams = [self.scene.addLine(l, QPen(QBrush(QColor(112,179,123)), 2, Qt.DashLine)) for l in lines]
		else:
			i = 0
			for l in lines:
				self.sensor_beams[i].setLine(l)		
				i+=1

	def draw_map(self, envmap):
		# Рисуем все объекты(полигоны) на карте	
		for poly in envmap.objects():
			self.scene.addPolygon(poly, QPen(Qt.NoPen), QBrush(QColor(179,112,123))) 
	
	def clear(self):
		self.scene.clear()
		self.cursor = None
		self.particles = None
		self.sensor_beams = None


#------------------------------------------------------------------------------
#
class MainWindow(QWidget):
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)

		self.startButton = QPushButton("&Start")
		self.nextButton = QPushButton("&Next")
		self.scene = QGraphicsScene()
		self.view = QGraphicsView()
		self.view.setScene(self.scene)
		self.view.setMinimumSize(800, 600)    

		sidePanel = QWidget()
		sideLayout = QVBoxLayout()
		sideLayout.addWidget(self.startButton)
		sideLayout.addWidget(self.nextButton)
		sidePanel.setLayout(sideLayout)

		mainLayout = QHBoxLayout()
		mainLayout.addWidget(sidePanel, 0, Qt.AlignTop)
		mainLayout.addWidget(self.view)
		self.setLayout(mainLayout)    
    
		self.startButton.clicked.connect(self.init_simulation)
		self.nextButton.clicked.connect(self.do_step)
	
		self.setWindowTitle("Robot localization demo")

		self.test_map = None # Переменная класса которая хранит карту
		self.simulation = None # Переменная класса которая хранит текущий эксперимент
		self.scene_objects = SceneObjects(self.scene) # Будет хранить все текущие объкты сцены		

	def init_simulation(self):
		""" Обработка кнопки "Start". Начало нового эксперимента
		"""
		# Очищаем экран - удаляем все что нарисовано
		self.scene_objects.clear()
		
		# Создаем карту из файла
		self.test_map = load_map_from_wkt('test_map.csv')		
		self.scene_objects.draw_map(self.test_map) #Рисуем карту
		self.view.fitInView(self.scene.sceneRect())

		#Создаем новый эксперимент
		number_of_particles = 1000
		self.simulation = Simulation(number_of_particles, self.test_map)
		self.scene_objects.draw_robot(self.simulation.robot_position)
		self.scene_objects.draw_particles(self.simulation.particles())		

	def do_step(self):
		x, y, direction = self.simulation.robot_position		
		sensor = self.simulation.move((x, y - 20, direction))		
		self.scene_objects.draw_sensor(self.simulation.robot_position, sensor)
		self.scene_objects.draw_robot(self.simulation.robot_position)
					