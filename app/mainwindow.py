# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from map import *
from simulation import *

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

	def init_simulation(self):
		""" Обработка кнопки "Start". Начало нового эксперимента
		"""
		# Очищаем экран - удаляем все что нарисовано
		self.scene.clear()
		
		# Создаем карту из файла
		self.test_map = load_map_from_wkt('test_map.csv')		
		self.draw_map() #Рисуем карту
		self.view.fitInView(self.scene.sceneRect())

		#Создаем новый эксперимент
		number_of_particles = 1000
		self.simulation = Simulation(number_of_particles, self.test_map)
		self.draw_particles() #вызываем функицю которая рисует частицы
		
	def do_step(self):
		pass


	def draw_map(self):
		# Рисуем все объекты(полигоны) на карте		
		for poly in self.test_map.objects():
			self.scene.addPolygon(poly, QPen(Qt.NoPen), QBrush(QColor(179,112,123))) 
		
	def draw_particles(self):
		for (x, y, direction) in self.simulation.particles():
			self.scene.addEllipse(x - 2, y - 2, 4, 4) 
