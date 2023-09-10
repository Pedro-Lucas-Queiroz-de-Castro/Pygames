import pygame
from settings import *


class Bullet(pygame.sprite.Sprite):
	def __init__(self, pos, direction, groups, shooter):
		super().__init__(groups)

		self.shooter = shooter

		if direction.x < 0:
			surface = pygame.transform.flip(
				Bullet.surface, True, False).convert_alpha()
		else:
			surface = Bullet.surface

		# sprite
		self.image = surface
		self.rect = self.image.get_rect(center=pos)
		self.mask = pygame.mask.from_surface(self.image)
		self.z = LAYERS_Z_INDEXES['level']

		# float based movement
		self.direction = direction
		self.pos = pygame.math.Vector2(self.rect.center)
		self.speed = 1600

		# boundaries
		self.map_boundaries = Bullet.map_boundaries

		# collisions
		self.collision_sprites = Bullet.collision_sprites
		self.vulnerable_sprites = Bullet.vulnerable_sprites

		# audio
		self.sounds = Bullet.sounds

	def move(self, dt):
		self.pos += self.direction * self.speed * dt
		self.rect.center = round(self.pos.x), round(self.pos.y)

	def collision(self):
		if pygame.sprite.spritecollide(self,self.collision_sprites,False):
			# self.sounds['hit'].play()
			self.kill()

		for sprite in pygame.sprite.spritecollide(
			self,self.vulnerable_sprites,False,pygame.sprite.collide_mask):
				if sprite != self.shooter:
					sprite.get_damage(1)
					self.kill()

	def autodestroy(self):
		if self.rect.right < 0 or self.rect.bottom < 0:
			self.kill()
		elif self.rect.left > self.map_boundaries[0] or\
		 self.rect.top > self.map_boundaries[1]:
		 	self.kill()

	def update(self, dt):
		self.move(dt)
		self.collision()
		self.autodestroy()

class Shooter:
	def __init__(self, bullet_groups, *args):
		super().__init__(*args)

		self.bullet_groups = bullet_groups

		self.can_shoot = True
		self.shot_time = 0
		self.shot_cooldown = 400
		self.full_bullets_num = 0
		self.bullets = self.full_bullets_num

		self.reloading = False
		self.start_reload_time = 0
		self.reload_duration = 2000

		# audio
		if hasattr(self, 'sounds'):
			for key, value in Shooter.sounds.items():
				self.sounds[key] = value
		else:
			self.sounds = Shooter.sounds

	def get_bullet_direction(self):
		match self.state.split('_')[0]:
			case 'right':
				direction = pygame.math.Vector2(1,0)
			case 'left':
				direction = pygame.math.Vector2(-1,0)

		return direction

	def get_bullet_position(self, direction):
		x = self.rect.centerx + 50 * direction.x

		if self.duck:
			y = self.rect.centery + 8 
		elif 'jump' in self.state:
			y = self.rect.centery - 20
		else:
			y = self.rect.centery - 16

		return (x, y)

	def shot_cooldown_manager(self, current_time):
		self.can_shoot = current_time - self.shot_time > self.shot_cooldown

		if current_time - self.start_reload_time > self.reload_duration:
			self.reloading = False

	def reload(self):
		if not self.reloading and self.bullets <= 0:
			self.bullets = self.full_bullets_num

	def shoot(self):
		if self.can_shoot and self.bullets > 0:
			self.sounds['bullet'].play()

			self.bullets -= 1
			if self.bullets == 0:
				self.start_reload_time = pygame.time.get_ticks()
				self.reloading = True

			self.can_shoot = False
			self.shot_time = pygame.time.get_ticks()

			direction = self.get_bullet_direction()
			position = self.get_bullet_position(direction)

			Bullet(position, direction, self.bullet_groups, self)

			fire_position = (position[0]+16*direction.x,position[1])
			FireAnimation(fire_position,direction, self.bullet_groups, self)
			

class FireAnimation(pygame.sprite.Sprite):
	def __init__(self, pos, direction, groups, shooter):
		super().__init__(groups)

		self.shooter = shooter

		# animation
		self.animations = FireAnimation.animations
		self.get_left_animation()
		self.animation_speed = 10
		self.side = 'right' if direction.x > 0 else 'left'
		self.frame_index = 0

		# sprite
		self.image = self.animations[self.side][self.frame_index]
		self.rect = self.image.get_rect(center=pos)
		self.z = LAYERS_Z_INDEXES['level']

	def get_left_animation(self):
		self.animations['left'] = [
		pygame.transform.flip(frame,True,False).convert_alpha()
		for frame in self.animations['right']]	

	def animate(self, dt):
		# frame progress
		self.frame_index += self.animation_speed * dt
		if int(self.frame_index) >= len(self.animations[self.side]):
			self.kill()
		else:
			self.image = self.animations[self.side][int(self.frame_index)]

	def move(self, dt):
		direction = self.shooter.get_bullet_direction()
		self.rect.center = self.shooter.get_bullet_position(direction)
		self.rect.centerx += 12*direction.x
		self.side = 'right' if direction.x > 0 else 'left'

	def update(self, dt):
		self.move(dt)
		self.animate(dt)