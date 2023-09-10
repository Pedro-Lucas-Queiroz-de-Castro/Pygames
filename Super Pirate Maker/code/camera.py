import pygame

from pygame.math import Vector2 as vector

from settings import *
from sprites import Cloud


class CameraGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()

		self.display_surface = pygame.display.get_surface()

	def custom_draw(self, player):
		self.offset = vector(player.rect.center) - vector(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)

		cloud_sprites = []
		other_sprites = []

		for sprite in self.sprites():
			if isinstance(sprite, Cloud):
				cloud_sprites.append(sprite)
			else:
				other_sprites.append(sprite)

		self.draw_horizon()
		self.draw_clouds(cloud_sprites)
		self.draw_sea()

		for sprite in sorted(other_sprites, key=lambda sprite: sprite.z):
			
			offset_rect = sprite.rect.copy()
			offset_rect.center = vector(offset_rect.center) - self.offset

			self.display_surface.blit(sprite.image, offset_rect)

		# self.debug(player)

	def debug(self, player):
		head_rect = player.head_rect.copy()
		head_rect.center = vector(head_rect.center) - self.offset

		hat_rect = player.hat_rect.copy()
		hat_rect.center = vector(hat_rect.center) - self.offset

		pygame.draw.rect(self.display_surface,'red', head_rect)
		pygame.draw.rect(self.display_surface,'green', hat_rect)

	def draw_horizon(self):
		y = self.horizon_y - self.offset.y

		# horizon lines
		if y > 0:	
			horizon_rect1 = pygame.Rect(0,y - 10,WINDOW_WIDTH,10)
			horizon_rect2 = pygame.Rect(0,y - 16,WINDOW_WIDTH,4)
			horizon_rect3 = pygame.Rect(0,y - 20,WINDOW_WIDTH,2)
			pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect1)
			pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect2)
			pygame.draw.rect(self.display_surface, HORIZON_TOP_COLOR, horizon_rect3)

			# self.display_clouds(dt, y)

	def draw_clouds(self, cloud_sprites):
		for sprite in cloud_sprites:
	
			offset_rect = sprite.rect.copy()
			offset_rect.center = vector(offset_rect.center) - self.offset

			self.display_surface.blit(sprite.image, offset_rect)

	def draw_sea(self):
		y = self.horizon_y - self.offset.y

		# sea 
		if 0 < y < WINDOW_HEIGHT:
			sea_rect = pygame.Rect(0,y,WINDOW_WIDTH,WINDOW_HEIGHT-y)
			pygame.draw.rect(self.display_surface, SEA_COLOR, sea_rect)
			pygame.draw.line(self.display_surface, HORIZON_COLOR, (0,y), (WINDOW_WIDTH,y),3)
		if y < 0:
			self.display_surface.fill(SEA_COLOR)
