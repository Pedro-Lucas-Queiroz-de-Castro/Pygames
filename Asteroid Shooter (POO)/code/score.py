import pygame
from settings import *


class Score:
	def __init__(self):
		self.screen = pygame.display.get_surface()
		self.score = 0
		self.font = pygame.font.Font('../images/subatomic.ttf', SCORE_FONT_SIZE)


	def update(self):
		self.score = int(pygame.time.get_ticks() // 1000)
		text = f"Score: {self.score}"
		self.surface = self.font.render(text, True, SCORE_COLOR)
		self.rect = self.surface.get_rect(center=SCORE_POS)


	def draw(self):
		self.screen.blit(self.surface, self.rect)
		pygame.draw.rect(self.screen, SCORE_BORDER_COLOR,
			self.rect.inflate(SCORE_BORDER_INFLATE[0], SCORE_BORDER_INFLATE[1]), 
			SCORE_BORDER_WIDTH, border_radius=SCORE_BORDER_RADIUS)
