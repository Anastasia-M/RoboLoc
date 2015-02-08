# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from map import *
from simulation import *
from simulationscene import *
import robotpath
import math
import cProfile, pstats

#------------------------------------------------------------------------------
#
class MainWindow(QWidget):
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)

		self.setWindowTitle("Robot localization demo")

		init_button = QPushButton("Загрузить")
		play_button = QPushButton(self.style().standardIcon(QStyle.SP_MediaPlay), "Начать")
		next_button = QPushButton(self.style().standardIcon(QStyle.SP_MediaSeekForward), "Шаг")	
		stop_button = QPushButton(self.style().standardIcon(QStyle.SP_MediaStop), "Стоп")
		graphics_scene = QGraphicsScene()
		self.graphics_view = QGraphicsView()
		self.graphics_view.setScene(graphics_scene)
		self.graphics_view.setMinimumSize(800, 600)    

		self.particles_spinbox = QSpinBox(self)
		self.particles_spinbox.setRange(100, 10000)
		self.particles_spinbox.setSingleStep(100)
		self.particles_spinbox.setValue(2000)
		self.particles_spinbox.setSuffix(" частиц")

		self.beams_spinbox = QSpinBox(self)
		self.beams_spinbox.setRange(6, 64)
		self.beams_spinbox.setSingleStep(1)
		self.beams_spinbox.setValue(14)
		self.beams_spinbox.setSuffix(" лучей")

		self.show_beams_cbox = QCheckBox("Сенсор")
		self.show_beams_cbox.setChecked(True)
		self.show_robot_cbox = QCheckBox("Робот")
		self.show_robot_cbox.setChecked(True)
		self.show_map_cbox = QCheckBox("Карта")
		self.show_map_cbox.setChecked(True)
		self.show_particles_cbox= QCheckBox("Частицы")
		self.show_particles_cbox.setChecked(True)
		self.show_belief_map_cbox = QCheckBox("Likelihood maps")

		self.show_belief_map_cbox.stateChanged.connect(self.view_options_changed)
		self.show_robot_cbox.stateChanged.connect(self.view_options_changed)
		self.show_beams_cbox.stateChanged.connect(self.view_options_changed)
		self.show_particles_cbox.stateChanged.connect(self.view_options_changed)
		self.show_map_cbox.stateChanged.connect(self.view_options_changed)

		view_group = QGroupBox("Вид");
		view_group_layout = QVBoxLayout()
		view_group_layout.addWidget(self.show_beams_cbox)
		view_group_layout.addWidget(self.show_robot_cbox)
		view_group_layout.addWidget(self.show_map_cbox)
		view_group_layout.addWidget(self.show_particles_cbox)		
		view_group_layout.addWidget(self.show_belief_map_cbox)
		view_group.setLayout(view_group_layout)

		sidePanel = QWidget()
		sideLayout = QVBoxLayout()
		sideLayout.addWidget(self.particles_spinbox)
		sideLayout.addWidget(self.beams_spinbox)

		sideLayout.addWidget(init_button)

		controlButtons = QWidget()
		controlButtonsLayout = QHBoxLayout()
		controlButtonsLayout.addWidget(play_button)
		controlButtonsLayout.addWidget(stop_button)
		controlButtonsLayout.addWidget(next_button)
		controlButtons.setLayout(controlButtonsLayout)

		sideLayout.addWidget(controlButtons)
		sideLayout.addWidget(view_group)
		sidePanel.setLayout(sideLayout)

		mainLayout = QHBoxLayout()
		mainLayout.addWidget(sidePanel, 0, Qt.AlignTop)
		mainLayout.addWidget(self.graphics_view)
		self.setLayout(mainLayout)    
    
		init_button.clicked.connect(self.init_simulation)
		next_button.clicked.connect(self.do_step)
		play_button.clicked.connect(self.play)
		stop_button.clicked.connect(self.stop)

			
		self.test_map = None # Переменная класса которая хранит карту
		self.simulation = None # Переменная класса которая хранит текущий эксперимент
		self.scene = SimulationScene(graphics_scene, self.graphics_view) # Будет хранить все текущие объкты сцены	
		self.step = 0		
		self.path = robotpath.path
		self.stop_flag = False

	def init_simulation(self):
		""" Обработка кнопки "Загрузить". Начало нового эксперимента
		"""
		# Очищаем экран - удаляем все что нарисовано
		self.scene.clear()
		
		# Создаем карту из файла
		self.test_map = load_map_from_wkt('test_map.csv')

		#Создаем новый эксперимент
		number_of_particles = self.particles_spinbox.value()
		number_of_sensors = self.beams_spinbox.value()	
		self.simulation = Simulation(number_of_particles, number_of_sensors, self.test_map)	

		if self.show_belief_map_cbox.isChecked():		
			self.scene.draw_occupancy(self.test_map, self.simulation.occupancy_map_cell, self.simulation.occupancy_map, 500)
		
		if self.show_map_cbox.isChecked():
			self.scene.draw_map(self.test_map)
		
		if self.show_particles_cbox.isChecked():
			self.scene.draw_particles(self.simulation.particles())		
		
		if self.show_robot_cbox.isChecked():
			self.scene.draw_robot(self.path[0])

		self.step = 0	


	def play(self):
		""" Обработка кнопки "Начать". Робот двигаеться атоматически
		"""		
		self.do_step()
		if not self.stop_flag and self.step < len(self.path):
			QTimer.singleShot(10, self.play)
		self.stop_flag = False
	

	def stop(self):
		""" Обработка кнопки "Стоп". Приостановать эксперимент
		"""		
		self.stop_flag = True


	def do_step(self):
		""" Обработка кнопки "Шаг". Делаем один шаг
		"""	
		x, y, direction = self.simulation.robot_position		
		self.step = self.step + 1
		if self.step >= len(self.path):
			return

		sensor = self.simulation.move(self.path[self.step])		

		self.scene.draw_particles(self.simulation.particles())		
		
		if self.show_beams_cbox.isChecked():	
			self.scene.draw_sensor(self.simulation.robot_position, sensor)

		if self.show_robot_cbox.isChecked():
			self.scene.draw_robot(self.simulation.robot_position)
		
	def view_options_changed(self):
		if self.show_belief_map_cbox.isChecked():		
			self.scene.draw_occupancy(self.test_map, self.simulation.occupancy_map_cell, self.simulation.occupancy_map, 500)		
		else:
			self.scene.hide_occupancy()

		if not self.show_robot_cbox.isChecked():
			self.scene.hide_robot()

		if self.show_map_cbox.isChecked():
			self.scene.draw_map(self.test_map)
		else:
			self.scene.hide_map()

		if self.show_particles_cbox.isChecked():
			self.scene.draw_particles(self.simulation.particles())		
		else:
			self.scene.hide_particles()
		

		if not self.show_beams_cbox.isChecked():
			self.scene.hide_sensor()


	# def mousePressEventV(self, event):
	# 	pos=event.pos()
	# 	pos=self.graphics_view.mapToScene(pos)
		
	# 	if self.last_pos != None:
	# 		#self.angle = normal_angle(self.angle + math.atan2(pos.y() - self.last_pos.y(), pos.x() - self.last_pos.x()))
	# 		self.angle = math.atan2(pos.y() - self.last_pos.y(), pos.x() - self.last_pos.x())
		
	# 	print(int(pos.x()), ",", int(pos.y()), ",", self.angle)

	# 	self.last_pos = pos;
    			