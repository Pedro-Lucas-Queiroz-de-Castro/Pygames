import pygame
from settings import SPRITES_OVERLAP_POSITIONS

class Sprite(pygame.sprite.Sprite):
	def __init__(self, name, surface, pos, groups):
		super().__init__(groups)

		self.name = name.lower() if name else name
		self.pos = pos
		self.image = surface.convert_alpha()
		self.rect = self.image.get_rect(topleft=pos)
		# self.hitbox = self.rect.inflate(0, -self.rect.height * 0.34)
		# self.hitbox.bottom = self.rect.bottom

		# overlap fake 3d effect
		self.overlap_pos = self.rect.top +\
			self.rect.height * SPRITES_OVERLAP_POSITIONS[self.name]