# -*- coding: utf8 -*-
import os, sys, random
from cell import Cell
from time import sleep, time as now

class Game:

	def __init__(self, size=9, alive_random = True):

		'Tamaño'
		self.size = size

		'Creamos un array unidimensional de size^2 elementos'
		self.cells = [ Cell(self, x) for x in xrange( self.size ** 2 ) ]

		'Si deseamos vidas aleatorias.. hacemos nacer algunas celdas'
		if alive_random:
			for cell in self.cells:
				if not int(random.random()*2):
					cell.beBorn()
		else:
			'y si no las hacemos nacer todas, ya se mataran entre ellas!!'
			for cell in self.cells:
				cell.beBorn()

		'Obligamos a todas las celdas a comprobar su proximo estado'
		self.queryAllCells()

	def getCell(self, x, y):
		"""		
			Recibe coordenadas de una celda y devuelve el objeto celda
			sito en esas coordenadas
		"""
		offset = y * self.size + x

		'Comprobamos que las coordenadas apunten a una celda existente'
		if offset >= 0 and offset < len(self.cells):
			return self.cells[ offset ]
		else:
			raise ValueError("Invalid Coordinates %dx%d"%(x, y))

	def queryAllCells(self):
		return [ cell.query() for cell in self.cells ]

	def updateAllCells(self, add_random=True):
		opers = [ cell.update() for cell in self.cells ]
		result = 1 in opers or 2 in opers
		if add_random and not int(random.random()*100):
			self.generatePlane()
		self.queryAllCells()
		return result

	def generatePlane(self, x=-1, y=-1):
		combs = [
			[
				( 0, 0 ),
				( 1, 0 ),
				( 2, 0 ),
				( 0, 1 ),
				( 1, 2 )
			]
		]
		check_is_dead_zone = True
		if x == -1 or y == -1:
			ox = int( random.random() * ( self.size - 2 ) )
			oy = int( random.random() * ( self.size - 2 ) )
		else:
			ox = int(x)
			oy = int(y)
			check_is_dead_zone = False
		while check_is_dead_zone and not self.isDeadZone(ox, oy, 3):
			ox = int( random.random() * ( self.size - 2 ) )
			oy = int( random.random() * ( self.size - 2 ) )
		comb = combs[ int( random.random() * len(combs) ) ]
		for c in comb:
			x, y = c
			self.getCell(ox + x, oy + y ).beBorn()

	def isDeadZone(self, x, y, size):
		ox = x
		oy = y
		for y in xrange(oy, min(oy + size, self.size ) ):
			for x in xrange(ox, min(ox + size, self.size) ):
				if self.getCell(x, y).isAlive(): return False
		return True

if __name__ == "__main__":
	game = Game(10, True)
	while game.updateAllCells():
		for y in xrange(game.size):
			for x in xrange(game.size):
				print game.getCell(x, y),
			print
		print
		sleep(2e-1)