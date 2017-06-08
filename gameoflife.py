import math
import os
import pygame, pygame.gfxdraw
import threading
from time import sleep

from app.game import Game

BLACK = (0, 0, 0)
FPS = 30.0
GAME_SIZE = 2 ** 6 - (0 if os.name == "posix" else 2)
SQUARE_SIZE = 32

x, y = (0, 0) if os.name == "posix" else (20, 20)

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)

pygame.init()

while GAME_SIZE * SQUARE_SIZE > 1080:
    SQUARE_SIZE /= 2

game = Game(GAME_SIZE, alive_random=True)

width, height = GAME_SIZE * SQUARE_SIZE, GAME_SIZE * SQUARE_SIZE
size = (width, height)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Game Of Life")
clock = pygame.time.Clock()
done = False
game_changed = True
started = False
ths = []


def setGameChanged(changed):
    global game_changed
    game_changed = changed


class BomberThread(threading.Thread):
    def __init__(self, game, *args, **kargs):
        threading.Thread.__init__(self)
        self.stopped = False
        self.game = game

    def run(self):
        while not self.stopped:
            self.game.generatePlane(GAME_SIZE - 3, GAME_SIZE - 3)
            self.game.queryAllCells()
            setGameChanged(True)
            sleep(0.9 ** 3.0)
            pass

    def stop(self):
        self.stopped = True


def switch_bombs(game):
    if len(ths) > 0:

        'Stop threads'
        for th in ths:
            th.stop()

        'Empty threads'
        [ths.pop() for t in ths]

    else:

        'New bomber'
        th = BomberThread(game)
        ths.append(th)
        th.start()


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
            elif event.key == pygame.K_b:
                switch_bombs(game)
        # handle MOUSEBUTTONUP
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            # get a list of all sprites that are under the mouse cursor
            # clicked_sprites = [s for s in sprites if s.rect.collidepoint(pos)]
            # do something with the clicked sprites...
            px, py = pos
            bx, by = math.floor(px / float(width) * GAME_SIZE), math.floor(py / float(height) * GAME_SIZE)
            while bx >= GAME_SIZE - 2:
                print "slower than", bx
                bx -= 1
            while by >= GAME_SIZE - 2:
                by -= 1

            print "born at", (bx, by), GAME_SIZE

            game.generatePlane(bx, by)
            game.queryAllCells()
            game_changed = True

            # print (px, py), ()

    if game_changed and started:
        game_changed = game.updateAllCells(add_random=False)

    screen.fill(BLACK)
    screen.lock()

    for y in xrange(game.size):
        for x in xrange(game.size):
            cell = game.getCell(x, y)
            if cell.isAlive():
                pygame.gfxdraw.filled_polygon(
                    screen,
                    (
                        (SQUARE_SIZE * x, SQUARE_SIZE * y),
                        (SQUARE_SIZE * (x + 1), SQUARE_SIZE * y),
                        (SQUARE_SIZE * (x + 1), SQUARE_SIZE * (y + 1)),
                        (SQUARE_SIZE * x, SQUARE_SIZE * (y + 1)),
                    ),
                    (255, 0, 0, 63) if cell.must_dead else (0, 127, 255, 63) if game_changed else (0, 255, 0, 63)
                )
                pass
    screen.unlock()
    pygame.display.flip()

    clock.tick(FPS)

for th in ths:
    th.stop()
