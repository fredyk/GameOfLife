# -*- coding: iso-8859-1 -*-
import os, sys

class Cell:

	'Algunas constantes...'
	KEEP_EQUAL = 0
	BE_BORN = 1
	DEAD = 2

	def __init__(self, game, pos):
		"""
			El constructor recibe como parametro la posicion absoluta de la
			celda dentro de la matriz de celdas. Calculamos las
			coordenadas a partir de la posicion absoluta y el tamano de la tabla
		"""
		self.game = game
		self.x = pos % game.size
		self.y = pos / game.size
		self.alive = False
		
		'Estos 2 booleanos sirven para recordar de un turno al siguiente'
		'el nuevo estado de la celda'
		self.must_be_born = False
		self.must_dead = False

	def getOthersAlive(self):
		"""
			Con este metodo contamos cuantas otras celdas (vivas) afectan
			a la actual
		"""

		'Columnas y filas izquierda/derecha, superior/inferior'
		up_row 	 = max(self.y - 1, 0)
		down_row = min(self.y + 1, self.game.size-1)
		left_col = max(self.x - 1, 0)
		right_col= min(self.x + 1, self.game.size-1)
		
		'Contador de celdas vivas'
		cnt_alive = 0

		for y in xrange(up_row, down_row + 1):
			for x in xrange(left_col, right_col + 1):
				if (x, y) != (self.x, self.y):
					cell = self.game.getCell(x, y)
					if cell.isAlive():
						cnt_alive += 1

		return cnt_alive

	def isAlive(self): return self.alive

	def mustDead(self):
		self.must_dead = self.alive and not self.getOthersAlive() in [2, 3]
		# self.must_dead = self.alive and not self.getOthersAlive() in [2, 3]
		# self.must_dead = self.alive and not self.getOthersAlive() in [5, 6, 7, 8]
		# self.must_dead = self.alive and not self.getOthersAlive() in [1, 3, 5, 8]
		return self.must_dead

	def mustBeBorn(self):
		self.must_be_born = not self.alive and self.getOthersAlive() in [3, 6]
		# self.must_be_born = not self.alive and self.getOthersAlive() in [3]
		# self.must_be_born = not self.alive and self.getOthersAlive() in [3, 5, 6, 7, 8]
		# self.must_dead = self.alive and not self.getOthersAlive() in [3, 5, 7]
		return self.must_be_born


	def beBorn(self):
		self.alive = True
		return Cell.BE_BORN

	def dead(self):
		self.alive = False
		return Cell.DEAD

	def query(self):
		return self.mustDead() 	 and Cell.DEAD 	  or \
			   self.mustBeBorn() and Cell.BE_BORN or Cell.KEEP_EQUAL

	def update(self):
		'Devuelve 0, 1 o 2'
		if self.must_dead: 		return self.dead()
		elif self.must_be_born: return self.beBorn()
		return Cell.KEEP_EQUAL

	def __str__(self):
		query = self.query()
		return "%s |" % ( "*" if self.alive else " " )