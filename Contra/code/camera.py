import pygame
from settings import LAYERS_Z_INDEXES, WINDOW_WIDTH

class AllSprites(pygame.sprite.Group):
	def __init__(self, tmx_map):
		super().__init__()

		self.offset = pygame.math.Vector2()

		# Sky
		# import
		self.fg_sky = pygame.image.load('../graphics/sky/fg_sky.png').convert_alpha()
		self.bg_sky = pygame.image.load('../graphics/sky/bg_sky.png').convert_alpha()

		# dimensions
		self.padding = WINDOW_WIDTH / 2

		self.map_width = tmx_map.tilewidth * tmx_map.width
		self.map_height = tmx_map.height*tmx_map.tileheight

		self.sky_width = self.bg_sky.get_width()
		self.sky_num = int((self.map_width+2*self.padding) // self.sky_width)

	def custom_draw(self, display_surface, player):
		self.offset.x = player.rect.centerx - display_surface.get_width()/2
		self.offset.y = player.rect.centery - display_surface.get_height()/2

		for n in range(self.sky_num):
			for surface, parallax_value in ((self.bg_sky,5), (self.fg_sky,4)):
				x = self.sky_width*n - self.padding - (self.offset.x // parallax_value)
				y = 300 - (self.offset.y // parallax_value)
				
				sky_rect = self.bg_sky.get_rect(topleft=(x,y))
				display_surface.blit(surface, sky_rect)
		

		for sprite in sorted(self.sprites(), key=lambda sprite: sprite.z):
			offset_rect = sprite.rect.copy()
			offset_rect.topleft -= self.offset
			display_surface.blit(sprite.image, offset_rect)
