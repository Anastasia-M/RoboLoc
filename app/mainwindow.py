# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from map import *

class MainWindow(QWidget):
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)

		self.startButton = QPushButton("&Start")
		self.nextButton = QPushButton("&Next")
		self.scene = QGraphicsScene()
		self.view = QGraphicsView()
		self.view.setScene(self.scene)
		self.view.setMinimumSize(400, 400)    

		sidePanel = QWidget()
		sideLayout = QVBoxLayout()
		sideLayout.addWidget(self.startButton)
		sideLayout.addWidget(self.nextButton)
		sidePanel.setLayout(sideLayout)

		mainLayout = QHBoxLayout()
		mainLayout.addWidget(sidePanel, 0, Qt.AlignTop)
		mainLayout.addWidget(self.view)
		self.setLayout(mainLayout)    
    
		self.startButton.clicked.connect(self.initSimulation)
		self.nextButton.clicked.connect(self.doStep)
	
		self.setWindowTitle("Robot localization demo")

		self.test_map = None # Переменная класса которая хранит карту
		self.simulation = None # Переменная класса которая хранит текущий эксперимент

	def init_simulation(self):
		""" Обработка кнопки "Start". Начало нового эксперимента
		"""
		# Создаем карту из файла
		self.test_map = load_map_from_wkt('test_map.csv')		
		self.draw_map() #Рисуем карту

		#Создаем новый эксперимент
		number_of_particles = 100
		self.simulation = Simulation(number_of_particles)
		self.draw_particles() #вызываем функицю которая рисует частицы
		self.view.fitInView(self.scene.sceneRect())

	def do_step(self):
		pass


	def draw_map(self, test_map):
		# Рисуем все объекты(полигоны) на карте		
		for poly in self.test_map.objects():
			self.scene.addPolygon(poly, QPen(Qt.NoPen), QBrush(QColor(179,112,123))) 
		
	def draw_particles(self):
		# Задание!!!: Нарисовать частицы 
		pass
