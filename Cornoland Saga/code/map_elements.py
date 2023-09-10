import pygame


class Tile(pygame.sprite.Sprite):
	def __init__(self, surface, pos, groups, z=3):
		super().__init__(groups)

		self.image = surface
		self.rect = self.image.get_rect(topleft=pos)
		self.old_rect = self.rect.copy()
		self.hitbox = self.rect.copy()
		self.old_hitbox = self.hitbox.copy()

		self.z = z

class Decoration(Tile):
	def __init__(self, surface, pos, groups):
		super().__init__(surface, pos, groups)

class Background(Tile):
	def __init__(self, surface, pos, groups, z):
		super().__init__(surface, pos, groups, z)
