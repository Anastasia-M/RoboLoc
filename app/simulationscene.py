# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from map import *
import math

#------------------------------------------------------------------------------
#
class SimulationScene:
	def __init__(self, graphics_scene, graphics_view):
		self.scene = graphics_scene		
		self.view = graphics_view
		self.particles = None
		self.cursor = None
		self.sensor_beams = None
		self.belief_map = None

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
			self.cursor.setZValue(5)
		else:
			self.cursor.setVisible(True)
			self.cursor.setPolygon(poly)	


	def draw_particles(self, plist):		
		if self.particles == None:
			self.particles = [self.scene.addEllipse(x - 2, y - 2, 4, 4) for (x, y, _) in plist]
			[item.setZValue(3) for item in self.particles]
		else:
			i = 0
			for (x,y,direction) in plist:
				self.particles[i].setRect(x - 2, y - 2, 4, 4)
				self.particles[i].setVisible(True)		
				i+=1

	def draw_sensor(self, pose, sensor):
		robot_x, robor_y, _ = pose
		lines = [QLineF(QPointF(robot_x, robor_y), QPointF(x,y)) for _,(x,y) in sensor]
		if self.sensor_beams == None:
			self.sensor_beams = [self.scene.addLine(l, QPen(QBrush(QColor(112,179,123)), 2, Qt.DashLine)) for l in lines]
			[item.setZValue(2) for item in self.sensor_beams]
		else:
			i = 0
			for l in lines:
				self.sensor_beams[i].setVisible(True)
				self.sensor_beams[i].setLine(l)		
				i+=1

	def draw_map(self, envmap):
		if self.map_object != None:
			for item in self.map_object:
				item.setVisible(True)
			return

		self.map_object = []
		# Рисуем все объекты(полигоны) на карте	
		for poly in envmap.objects():
			item = self.scene.addPolygon(poly, QPen(Qt.NoPen), QBrush(QColor(179,112,123))) 
			item.setZValue(1)
			self.map_object.append(item)
		self.view.fitInView(self.scene.sceneRect())
		
	def draw_occupancy(self, envmap, cellsize, values, max_range):
		if self.belief_map != None:
			for item in self.belief_map:
				item.setVisible(True)
			return

		self.belief_map = []
		w = len(values)
		h = len(values[0])
		bbox = envmap.bounding_box()
		for i in range(0, w):
			for j in range(0, h):
				c = int(255.0 * values[i][j] / max_range)
				rect_item = self.scene.addRect(bbox.x() + i*cellsize, bbox.y() + j*cellsize, cellsize, cellsize, QPen(Qt.NoPen), QBrush(QColor(c,c,c)))
				rect_item.setZValue(0)
				self.belief_map.append(rect_item)
	
	def hide_occupancy(self):
		if self.belief_map != None:
			for item in self.belief_map:
				item.setVisible(False)

	def hide_particles(self):
		if self.particles != None:
			for item in self.particles:
				item.setVisible(False)

	def hide_map(self):
		if self.map_object != None:
			for item in self.map_object:
				item.setVisible(False)


	def hide_sensor(self):
		if self.sensor_beams != None:
			[item.setVisible(False) for item in self.sensor_beams]

	def hide_robot(self):
		if self.cursor != None:
			self.cursor.setVisible(False)


	def clear(self):
		self.scene.clear()
		self.cursor = None
		self.particles = None
		self.sensor_beams = None
		self.map_object = None
