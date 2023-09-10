import pygame
from pygame.math import Vector2 as Vector
from settings import SPRITES_OVERLAP_POSITIONS
from math import sin

class Entity(pygame.sprite.Sprite):
	def __init__(self, name, pos, groups, animations, collision_objects):
		super().__init__(groups)

		# animation
		self.animations = animations
		self.state = 'down_idle'
		self.frame_index = 0
		self.animation_speed = 10 # surfs per second

		# general
		self.name = name
		self.image = self.animations[self.state][self.frame_index]
		self.rect = self.image.get_rect(center=pos)

		# float based movement
		self.pos = Vector(self.rect.midbottom)
		self.direction = Vector()
		self.speed = 300

		# collision
		self.hitbox = self.rect.inflate(-self.rect.width/2,-self.rect.height/2)
		self.hitbox.bottom = self.rect.bottom
		self.collision_objects = collision_objects
		self.mask = pygame.mask.from_surface(self.image)

		# attack
		self.attacking = False

		# drawing
		self.overlap_value = SPRITES_OVERLAP_POSITIONS[name]
		self.overlap_pos = self.rect.top + self.rect.height * self.overlap_value

		# health
		self.health = 100

		# vulnerability
		self.is_vulnerable = True
		self.vulnerability_duration = 400
		self.hit_time = None

		# sound
		self.hit_sound = pygame.mixer.Sound('../sound/hit.mp3')
		self.hit_sound.set_volume(0.6)

	def get_damage(self, amount):
		if self.is_vulnerable:
			self.health -= amount
			self.is_vulnerable = False
			self.hit_time = pygame.time.get_ticks()

			self.hit_sound.play()

		self.check_death()

	def check_death(self):
		if self.health <= 0:
			self.kill()

	def vulnerability_timer(self):
		if not self.is_vulnerable:
			current_time = pygame.time.get_ticks()
			if current_time - self.hit_time > self.vulnerability_duration:
				self.is_vulnerable = True

	def blink(self):
		if not self.is_vulnerable and self.wave_value():
			mask = pygame.mask.from_surface(self.image)
			mask_surface = mask.to_surface()
			mask_surface.set_colorkey((0,0,0)) # this gets rid of a specific color
			self.image = mask_surface

	def wave_value(self):
		return sin(pygame.time.get_ticks()) >= 0

	def move(self, dt, direction_factor=1):
		# normalize
		if self.direction.magnitude() != 0:
			self.direction.normalize_ip()

		# horizontal
		self.pos.x += self.direction.x * self.speed * dt * direction_factor
		self.hitbox.centerx = round(self.pos.x)
		self.rect.centerx = self.hitbox.centerx

		self.collision('horizontal')

		# vertical
		self.pos.y += self.direction.y * self.speed * dt * direction_factor
		self.hitbox.bottom = round(self.pos.y)
		self.rect.bottom = self.hitbox.bottom

		self.collision('vertical')

	def update_overlap(self, value=0.5):
		self.overlap_pos = self.rect.top + self.rect.height * value
		
	def collision(self, direction):
		for hitbox in self.collision_objects:
			if self.hitbox.colliderect(hitbox):
				match direction:
					case 'horizontal':
						if self.direction.x > 0:
							self.hitbox.right = hitbox.left
						elif self.direction.x < 0:
							self.hitbox.left = hitbox.right

					case 'vertical':
						if self.direction.y > 0:
							self.hitbox.bottom = hitbox.top
						elif self.direction.y < 0:
							self.hitbox.top = hitbox.bottom

				self.rect.midbottom = self.hitbox.midbottom
				self.pos.x, self.pos.y = self.rect.centerx, self.rect.bottom

	def animate(self, dt, finish_cooldowns=lambda: None):
		current_animation = self.animations[self.state] # current frames
		self.frame_index += self.animation_speed * dt # time passage

		if int(self.frame_index) >= len(current_animation):
			self.frame_index = 0 # restarts the animation, loops the frame
			self.attacking = False # finish attack animation and attack logic

			finish_cooldowns()

		self.image = current_animation[int(self.frame_index)] # current frame
		self.mask = pygame.mask.from_surface(self.image) # updates the mask
