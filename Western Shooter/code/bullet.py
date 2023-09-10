import pygame

class Bullet(pygame.sprite.Sprite):
	def __init__(self, pos, direction, image, groups, collision_objects, shooter, speed):
		super().__init__(groups)

		self.image = image
		self.rect = self.image.get_rect(center=pos)
		self.shooter = shooter

		# float based movement
		self.pos = pygame.math.Vector2(pos)
		self.direction = direction
		self.speed = speed

		self.overlap_pos = self.rect.centery

		# collision
		self.collision_objects = collision_objects
		self.mask = pygame.mask.from_surface(self.image)

		# rotation
		self.to_rotate_image = image
		self.angle = 0
		self.rotation_speed = 200

	def move(self, dt):
		self.pos += self.direction * self.speed * dt
		self.rect.center = round(self.pos.x), round(self.pos.y)

	def rotate(self, dt):
		self.angle += self.rotation_speed * dt
		self.image = pygame.transform.rotozoom(self.to_rotate_image, self.angle, 1)
		self.mask = pygame.mask.from_surface(self.image)

	def update(self, dt):
		self.move(dt)
		self.rotate(dt)