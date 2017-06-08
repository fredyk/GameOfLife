import os, sys, time, random, pygame, pygame.gfxdraw
from time import sleep, time as now

class Cell:

    'Algunas constantes...'
    KEEP_EQUAL = 0
    BE_BORN    = 1
    DEAD       = 2

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
        up_row   = max(self.y - 1, 0)
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

    def mustBeBorn(self):
        # self.must_be_born = not self.alive and self.getOthersAlive() in [3]
        self.must_be_born = not self.alive and self.getOthersAlive() in [3, 5, 6, 7, 8]
        return self.must_be_born

    def mustDead(self):
        # self.must_dead = self.alive and not self.getOthersAlive() in [2, 3]
        self.must_dead = self.alive and not self.getOthersAlive() in [5, 6, 7, 8]
        return self.must_dead

    def beBorn(self):
        self.alive = True
        return Cell.BE_BORN

    def dead(self):
        self.alive = False
        return Cell.DEAD

    def query(self):
        return self.mustDead()   and Cell.DEAD    or \
               self.mustBeBorn() and Cell.BE_BORN or Cell.KEEP_EQUAL

    def update(self):
        'Devuelve 0, 1 o 2'
        if self.must_dead:      return self.dead()
        elif self.must_be_born: return self.beBorn()
        return Cell.KEEP_EQUAL

    def __str__(self):
        query = self.query()
        return "%s |" % ( "*" if self.alive else " " )


class Game:

    def __init__(self, size=9, alive_random = True):

        'Tamano'
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
            raise ValueError("Invalid Coordinates %dx%y"%(x, y))

    def queryAllCells(self):
        return [ cell.query() for cell in self.cells ]

    def updateAllCells(self):
        opers = [ cell.update() for cell in self.cells ]
        result = 1 in opers or 2 in opers
        if not int(random.random()*100):
            self.generatePlane()
        self.queryAllCells()
        return result

    def generatePlane(self):
        combs = [
            [
                ( 0, 0 ),
                ( 1, 0 ),
                ( 2, 0 ),
                ( 0, 1 ),
                ( 1, 2 )
            ]
        ]
        ox = int( random.random() * ( self.size - 2 ) )
        oy = int( random.random() * ( self.size - 2 ) )
        while not self.isDeadZone(ox, oy, 3):
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

"""
    COMIENZA LA INTERFAZ GRAFICA
"""


BLACK       = (   0,   0,   0)
FPS         = 60.0
GAME_SIZE   = 2**6
SQUARE_SIZE = 32

x, y = (0, 0) if os.name == "posix" else (20, 20)

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)

pygame.init()


while GAME_SIZE*SQUARE_SIZE > 1080:
    SQUARE_SIZE /= 2

game = Game(GAME_SIZE, alive_random=True)


width, height = GAME_SIZE*SQUARE_SIZE, GAME_SIZE*SQUARE_SIZE
size = (width, height)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Game Of Life")
clock = pygame.time.Clock()
done         = False
game_changed = True
started      = False

while not done:

    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
            elif event.key == pygame.K_SPACE:
                started ^= True
            elif event.key == pygame.K_p:
                game.generatePlane()
                game.queryAllCells()
                game_changed = True

    if game_changed and started:
        game_changed = game.updateAllCells()

    screen.fill(BLACK)
    screen.lock()

    for y in xrange(game.size):
        for x in xrange(game.size):
            cell = game.getCell(x, y)
            if cell.isAlive():
                pygame.gfxdraw.filled_polygon(
                    screen,
                    (
                        ( SQUARE_SIZE*x, SQUARE_SIZE*y ),
                        ( SQUARE_SIZE*(x+1), SQUARE_SIZE*y ),
                        ( SQUARE_SIZE*(x+1), SQUARE_SIZE*(y+1) ),
                        ( SQUARE_SIZE*x, SQUARE_SIZE*(y+1) ),
                    ),
                    (255, 0, 0, 63) if cell.must_dead else (0, 0, 255, 63) if game_changed else ( 0, 255, 0, 63 )
                )
                pass
    screen.unlock()
    pygame.display.flip()

    clock.tick(FPS)