import pygame
from settings import *

class Cartridge:
	def __init__(self, player):
		self.player = player
		self.padding = 10

		self.bullet_width = 16
		self.bullet_height = 32

	def get_surface(self):
		if not self.player.reloading:
			surface = pygame.Surface((self.bullet_width, self.bullet_height))
			surface.fill('yellow')
		else:
			current_time = pygame.time.get_ticks()
			full_pixel_width = (self.bullet_width+self.padding)*7

			width = int(full_pixel_width *\
				((current_time-self.player.start_reload_time)/
					self.player.reload_duration))
			
			surface = pygame.Surface((width,
				self.bullet_height))
			surface.fill('orange')

		return surface

	def get_pos(self, n=None):
		if not self.player.reloading:
			pos = (n*(self.bullet_width+self.padding)+CARTRIDGE_POS[0],
				CARTRIDGE_POS[1])
		else:
			pos = CARTRIDGE_POS 

		return pos

	def draw(self, display_surface):
		if not self.player.reloading:
			for n in range(self.player.bullets):
				display_surface.blit(self.get_surface(), self.get_pos(n))
		else:
			display_surface.blit(self.get_surface(), self.get_pos())

		
class HealthIndicator(pygame.sprite.Sprite):
	def __init__(self, image, player):

		self.image = image
		self.rect = self.image.get_rect(topleft=HEALTH_INDICATOR_POS)
		self.padding = 10

		self.player = player

	def draw(self, display_surface):
		for n in range(self.player.health):
			self.rect.x = n * (self.rect.width + self.padding) + HEALTH_INDICATOR_POS[0]
			display_surface.blit(self.image, self.rect)

		self.rect.topleft = HEALTH_INDICATOR_POS
