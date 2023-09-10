import pygame


class SimpleObject(pygame.sprite.Sprite):
	def __init__(self, groups, surface, pos):
		super().__init__(groups)
		self.image = surface
		self.rect = self.image.get_rect(topleft=pos)

		if self.rect.height < 70:
			Yinflate = -self.rect.height * 0.06
		else:
			Yinflate = -self.rect.height * 0.3

		self.hitbox = self.rect.inflate(0, Yinflate)
		self.hitbox.bottom = self.rect.bottom


class LongObject(pygame.sprite.Sprite):
	def __init__(self, groups, surface, pos):
		super().__init__(groups)
		self.image = surface
		self.rect = self.image.get_rect(topleft=pos)
		self.hitbox = self.rect.inflate(-self.rect.width/1.9, -self.rect.height/2.4)
		self.hitbox.bottom = self.rect.bottom
