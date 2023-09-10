import pygame

from settings import *

from enemies import Entity


class Camera(pygame.sprite.Group):
	def __init__(self):
		super().__init__()

		self.display_surface = pygame.display.get_surface()

		self.display_surface_center =\
			pygame.math.Vector2(self.display_surface.get_width()//2, self.display_surface.get_height()//2)

		self.offset = pygame.math.Vector2()

	def custom_draw(self, player, dt):
		self.offset = player.rect.center - self.display_surface_center

		for sprite in sorted(self.sprites(), key=lambda sprite: sprite.z):
			if sprite.z == 0:
				parallax = 0.7
				parallay = 1
			elif sprite.z == 1:
				parallax = 0.8
				parallay = 1
			elif sprite.z == 2:
				parallax = 0.9
				parallay = 1
			else:
				parallax = 1
				parallay = 1

			offset = self.offset.copy()
			offset.x *= parallax
			offset.y *= parallay

			offset_rect = sprite.rect.copy()
			offset_rect.center = pygame.math.Vector2(offset_rect.center) - offset

			self.display_surface.blit(sprite.image, offset_rect)

		# self.show_class_rects(Entity)
		# self.show_class_radius(Entity)
		
	def show_class_rects(self, Class):
		rects = ('rect', 'hitbox', 'floor_rect', 'left_wall_rect', 'right_wall_rect')
		colors = ('blue', 'red', 'green', 'orange', 'orange')
		widths = (1, 1, 0, 0, 0)

		for entity in [sprite for sprite in self.sprites() if isinstance(sprite, Class)]:
			for rect_name, color, width in zip(rects, colors, widths):

				rect = getattr(entity, rect_name).copy()
				rect.center = pygame.math.Vector2(rect.center) - self.offset

				pygame.draw.rect(self.display_surface, color, rect, width)

	def show_class_radius(self, Class):
		radius = ['attack_radius']
		colors = ['red']
		width = 1

		data = list(zip(radius, colors))

		for entity in [sprite for sprite in self.sprites() if isinstance(sprite, Class)]:
			for radius_name, color in data:
				if hasattr(entity, radius_name):
					center = pygame.math.Vector2(entity.hitbox.center) - self.offset
					radius = getattr(entity, radius_name)
					pygame.draw.circle(self.display_surface, color, center, radius, width)
