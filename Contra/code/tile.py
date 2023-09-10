import pygame
from settings import *

class Tile(pygame.sprite.Sprite):
	def __init__(self, pos, surf, groups, z):
		super().__init__(groups)

		self.image = surf
		self.rect = self.image.get_rect(topleft=pos)

		self.z = z

class CollisionTile(Tile):
	def __init__(self, pos, surf, groups, z):
		super().__init__(pos, surf, groups, z)

		self.old_rect = self.rect.copy()

class MovingPlatform(CollisionTile):
	def __init__(self, pos, surf, groups, z, name):
		super().__init__(pos, surf, groups, z)

		self.name = name

		# float based movement
		self.direction = pygame.math.Vector2(0,-1)
		self.pos = pygame.math.Vector2(self.rect.topleft)
		self.speed = 200
		
	def get_borders(self, borders):
		self.borders = [border for border in borders\
		if border.name.split('_')[1] == self.name.split('_')[1]]

	def move(self, dt):
		self.pos += self.direction * self.speed * dt
		self.rect.topleft = round(self.pos.x), round(self.pos.y)

	def collision(self):
		# border
		for border in self.borders:
			if self.rect.colliderect(border.rect):
				if self.old_rect.top >= border.old_rect.bottom:
					self.rect.top = border.rect.bottom
				elif self.old_rect.bottom <= border.old_rect.top:
					self.rect.bottom = border.rect.top

				self.direction *= -1

		# player
		if self.rect.colliderect(self.player.rect) and\
		self.rect.centery < self.player.rect.centery and self.player.on_floor:
			self.rect.bottom = self.player.rect.top
			self.direction *= -1

		self.pos.x, self.pos.y = self.rect.left, self.rect.top
						
	def update(self, dt):
		self.old_rect = self.rect.copy()
		self.move(dt)
		self.collision()

class PlatformBorder(pygame.sprite.Sprite):
	def __init__(self, l, t, w, h, name, groups):
		super().__init__(groups)

		self.name = name
		self.rect = pygame.Rect(l, t, w, h)
		self.old_rect = self.rect.copy()

