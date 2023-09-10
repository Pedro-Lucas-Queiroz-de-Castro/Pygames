import pygame
from sys import exit
from level import Level
from settings import *
from time import time


class Game:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		pygame.display.set_caption("Asteroid Shooter")
		self.level = Level()
		self.clock = pygame.time.Clock()
		self.prev_time = time()

	def run(self):
		while True:
			dt = time() - self.prev_time
			self.prev_time = time()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					exit()

			self.level.run(dt)
			pygame.display.update()
			self.clock.tick()


if __name__ == '__main__':
	game = Game()
	game.run()
