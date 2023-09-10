import pygame

from joystick_constants import *
from settings import *
from support import *

from entity import Entity
from time_handling import *
from random import choice


class MeleeUser(Entity):
	def __init__(self, groups, animations, pos, collision_sprites, melee_hit_animations):
		super().__init__(groups, animations, pos, collision_sprites)

		self.melee_hit_animations = melee_hit_animations

	def create_melee_attack_mask(self):
		if self.animation_state in self.melee_hit_animations[self.animation_direction].keys():
			self.melee_attack_mask = pygame.mask.from_surface(self.melee_hit_animations[self.animation_direction][self.animation_state][int(self.frame_index)])
		else:
			self.melee_attack_mask = None


class Player(MeleeUser):
	def __init__(self, groups, animations, melee_hit_animations, pos, window_dimensions, collision_sprites, damage_sprites, attackable_sprites, add_heart):
		self.z = 6

		super().__init__(groups, animations, pos, collision_sprites, melee_hit_animations)

		# window
		self.window_width, self.window_height = window_dimensions

		# joystick
		self.joystick = None

		# animation
		self.animation_speed_var = 1
		self.frame_index_direction = 1

		# horizontal movement
		self.horizontal_speed = 600
		self.exhausted_direction = 0.25

		self.running = False
		self.direction_min_running_value = 0.7

		# vertical movement
		self.gravity = 3000
		self.pressing_down = False
		self.fall_acceleration_speed_coefficient = 1.5

		# jump
		self.jump_speed = 1200
		self.jump_increment_speed = 1600
		self.jump_increment_activated = False
		self.preparing_to_jump = False

		# somersault
		self.somersaulting = False
		self.somersaulted = False
		self.somersault_horizontal_speed = 500
		self.somersault_up_direction_speed = 600
		self.somersault_falling_speed = 650

		# crouch
		self.crouching = False
		self.crouching_speed = 100

		# slide
		self.sliding = False
		self.slide_initial_speed = 1000
		self.slide_speed = self.slide_initial_speed
		self.slide_deseleration = 2700
		self.slide_speed_min = 50

		self.slide_cooldown = Cooldown(900)

		# climb
		self.climbing = False
		self.climbing_speed = 300

		self.toggle_climb_cooldown = Cooldown(250)

		# sword
		 # draw/sheathe
		self.has_sword = True
		self.sword_drawed = False
		self.drawing_sword = False
		self.sheathing_sword = False

		self.sword_toggle_cooldown = Cooldown(250)

		 # attack
		self.attack_power = 0
		self.sword_attacking = False
		self.sword_attack_combo = []
		self.max_sword_attack_combo = 3
		self.sword_attack_index = 0

		self.sword_attack_combo_cooldown = Cooldown(100)
		self.sword_attack_cooldown = Cooldown(0)
		self.sword_attack_cooldown_milliseconds = (0,0,0)#(150,270,390)

		# attack hitboxes
		self.attackable_sprites = attackable_sprites

		# damage
		self.damage_sprites = damage_sprites
		self.invulnerability_cooldown = Cooldown(800)
		self.blink_wave = TimeWave(800//16) # cooldown // 16

		# heart
		self.min_hearts = 0
		self.max_hearts = HEARTS_START_NUMBER

		self.hearts = self.max_hearts
		self.last_hearts = self.hearts

		self.recover_hearts_cooldown = Cooldown(100)
		self.add_heart_cooldown = Cooldown(300)

		self.add_heart = add_heart

		# death
		self.deathing = False
		self.died_in_the_air = False
		self.falling_dead_hit_floor = False
		self.falling_dead_hitted_floor = False
		self.dead_floor_hit_bounce_falling_speed_percent = 0.4

		# stamina
		self.max_stamina = STAMINA_START_AMOUNT
		self.stamina = self.max_stamina
		self.last_stamina = self.stamina

		self.stamina_recovering_speed = 30

		self.spending_stamina = False
		self.exhausted = False

		self.get_more_stamina_cooldown = Cooldown(300)

		# noise
		self.noise_degree = 0


	# input
	def get_joydata(self):
		if self.joystick:
			joydata = {}

			# axis
			joydata['axis'] = [self.joystick.get_axis(a) for a in range(self.joystick.get_numaxes())]

			# d-pad/hat
			joydata['hats'] = [self.joystick.get_hat(h) for h in range(self.joystick.get_numhats())]

			# buttons
			joydata['buttons'] = [bool(self.joystick.get_button(b)) for b in range(self.joystick.get_numbuttons())]

		else:
			joydata = None

		return joydata

	def get_controls(self, joydata, keys):
		controls = {}

		if self.joystick:
			controls['horizontal movement'] = truncade(joydata['axis'][H_LEFT_AXIS], 2)
		else:
			if keys[pygame.K_RIGHT]:
				controls['horizontal movement'] = 1
			elif keys[pygame.K_LEFT]:
				controls['horizontal movement'] = -1
			else:
				controls['horizontal movement'] = 0

		if self.joystick:
			controls['vertical movement'] = truncade(joydata['axis'][V_LEFT_AXIS], 2)
		else:
			if keys[pygame.K_UP]:
				controls['vertical movement'] = -1
			elif keys[pygame.K_DOWN]:
				controls['vertical movement'] = 1
			else:
				controls['vertical movement'] = 0

		controls['pressing up'] = truncade(joydata['axis'][V_LEFT_AXIS], 2) < 0 if self.joystick else keys[pygame.K_UP]
		controls['pressing down'] = truncade(joydata['axis'][V_LEFT_AXIS], 2) > 0 if self.joystick else keys[pygame.K_DOWN]

		controls['jump'] = joydata['buttons'][CROSS] if self.joystick else keys[pygame.K_x]
		controls['somersault'] = joydata['buttons'][R1] if self.joystick else keys[pygame.K_c]
		controls['sword draw'] = joydata['buttons'][SQUARE] if self.joystick else keys[pygame.K_z]
		controls['sword sheathe'] = joydata['buttons'][CIRCLE] if self.joystick else keys[pygame.K_a]
		controls['attack'] = joydata['buttons'][SQUARE] if self.joystick else keys[pygame.K_z]
		controls['toggle climb'] = joydata['buttons'][TRIANGLE] if self.joystick else keys[pygame.K_s]

		# controls['get damage'] = joydata['buttons'][R2] if self.joystick else keys[pygame.K_e]
		# controls['recover hearts'] = joydata['buttons'][L2] if self.joystick else keys[pygame.K_q]
		controls['add heart'] = joydata['buttons'][L1] if self.joystick else keys[pygame.K_p]

		controls['add stamina'] = joydata['buttons'][10] if self.joystick else keys[pygame.K_w]

		controls['sword toggle'] = joydata['buttons'][R2] if self.joystick else keys[pygame.K_e]

		return controls

	def input(self, controls, dt):
		if not self.deathing:
			# horizontal movement
			self.direction.x = controls['horizontal movement']

			# vertical movement
			if controls['jump']:
				self.jump(preparing=True)

			self.pressing_up = controls['pressing up']
			self.pressing_down = controls['pressing down']

			# somersault
			if controls['somersault'] and not self.somersaulted:
				self.somersaulting = True
				self.somersaulted = True

			# crouch
			if self.pressing_down and self.on_floor:
				self.crouching = True
			else:
				self.crouching = False

			# slide
			if not self.slide_cooldown.on:
				if controls['attack'] and self.on_floor and self.pressing_down:
					self.sliding = True

			# climb
			if not self.toggle_climb_cooldown.on:
				if controls['toggle climb'] and (self.wall_colliding or self.climbing):
					self.climbing = not self.climbing
					self.toggle_climb_cooldown.start()

			# sword draw/sheathe
			if controls['sword draw'] and not self.pressing_down:
				self.draw_sword()

			if controls['sword sheathe']:
				self.sheathe_sword()

			# sword attack
			if controls['attack'] and not self.pressing_down:
				self.sword_attack()

			# heart system
			# if controls['get damage']:
			# 	self.take_damage(choice([0.25,0.5,0.75,1]))

			# if controls['recover hearts']:
			# 	self.recover_hearts(choice([0.25,0.5,0.75,1]))

			if controls['add heart']:
				self.get_new_heart()

			# stamina
			if controls['add stamina']:
				self.get_more_stamina(choice(list(range(10,101,10))))

			# sword toggle
			if controls['sword toggle'] and not self.sword_toggle_cooldown.on:
				self.has_sword = not self.has_sword
				if not self.has_sword:
					self.sword_drawed = False
				self.sword_toggle_cooldown.start()


	# damage
	def check_damage(self):
		if not self.deathing:
			if not self.invulnerability_cooldown.on:
				for sprite in self.damage_sprites:
					if sprite.hitbox.colliderect(self.hitbox):

						offset = (sprite.rect.left - self.rect.left, sprite.rect.top - self.rect.top)

						take_hit = (not self.sword_attacking) and not self.melee_attack_mask.overlap(sprite.mask,offset) and self.mask.overlap(sprite.mask,offset)\
						if self.melee_attack_mask else self.mask.overlap(sprite.mask,offset)

						if take_hit:
							self.take_damage(sprite.attack_power)
							self.take_knockback(sprite.knockback_power)

							self.invulnerability_cooldown.start()

	def take_damage(self, amount):
		if not self.deathing:			
			self.hearts = max(self.min_hearts, self.hearts-amount)

	def take_knockback(self, knockback_power):
		self.direction.y = -knockback_power

	def check_death(self):
		if not self.deathing:
			if self.hearts <= 0:
				self.deathing = True
				self.died_in_the_air = not self.on_floor
		elif self.died_in_the_air:
			self.falling_dead_hit_floor = self.on_floor


	# heart
	def recover_hearts(self, amount):
		if not self.recover_hearts_cooldown.on:

			self.hearts = min(self.hearts+amount, self.max_hearts)

			self.recover_hearts_cooldown.start()

	def get_new_heart(self):
		if self.max_hearts < MAX_HEARTS_NUMBER:
			if not self.add_heart_cooldown.on:
				self.max_hearts += 1
				self.add_heart()
				
				self.add_heart_cooldown.start()


	# stamina
	def recover_stamina(self, dt):
		if self.stamina < self.max_stamina and not self.spending_stamina:

			if self.climbing and self.direction.y == 0:
				pass
			else:
				self.stamina = min(self.max_stamina, self.stamina + self.stamina_recovering_speed * dt)

			if self.stamina >= self.max_stamina:
				self.exhausted = False

	def stamina_spending(self, dt):
		if not self.exhausted:
			if self.running:
				self.spending_stamina = True
				self.stamina -= STAMINA_COSTS['running'] * dt

			elif self.climbing and self.direction.y != 0:
				self.spending_stamina = True
				self.stamina -= STAMINA_COSTS['climbing'] * dt

			else:
				self.spending_stamina = False

			self.stamina = max(0.5, self.stamina)

			if self.stamina == 0.5:
				self.stamina = 0
				self.spending_stamina = False
				self.exhausted = True

	def has_enough_stamina(self, key, dt):
		return self.stamina > STAMINA_COSTS[key] * dt and not self.exhausted

	def get_more_stamina(self, amount):
		if self.max_stamina / FULL_STAMINA_WHEEL_UNITS < MAX_STAMINA_WHEELS:
			if not self.get_more_stamina_cooldown.on:
				self.max_stamina = min(FULL_STAMINA_WHEEL_UNITS*MAX_STAMINA_WHEELS,self.max_stamina+amount)
				self.get_more_stamina_cooldown.start()


	# sword
	def draw_sword(self):
		if self.has_sword:
			if not self.sword_drawed:
				self.drawing_sword = True

	def sheathe_sword(self):
		if self.sword_drawed:
			self.sheathing_sword = True

	def sword_attack(self):
		if not self.sword_attack_combo_cooldown.on and not self.sword_attack_cooldown.on:
			if self.sword_drawed:
				self.sword_attacking = True

				if self.sword_attack_combo:
					if self.sword_attack_combo[-1] == self.sword_attack_index:
						self.sword_attack_combo.append(self.sword_attack_combo[-1]+1)
				else:
					self.sword_attack_combo.append(0)

				if self.sword_attack_combo[-1] == self.max_sword_attack_combo:
					self.sword_attack_combo.pop()

				self.sword_attack_combo_cooldown.start()


	# movement
	def jump(self, preparing=False):
		if self.on_floor:
			if preparing:
				self.preparing_to_jump = True
			else:
				self.direction.y = -self.jump_speed
				self.jump_increment_activated = True

	def somersault(self):
		self.direction.x = 1 if self.animation_direction == 'right' else -1
		self.direction.y = -self.somersault_up_direction_speed
		return self.somersault_horizontal_speed

	def somersault_ending(self):
		if self.direction.x == 0:
			self.direction.x = 1 if self.animation_direction == 'right' else -1
		return self.somersault_falling_speed

	def slide(self, dt):
		self.direction.x = 1 if self.animation_direction == 'right' else -1
		self.slide_speed -= self.slide_deseleration * dt
		self.slide_speed = max(self.slide_speed_min, self.slide_speed)

	def horizontal_movement(self, dt):
		if self.somersaulting:
			speed = self.somersault()

		elif self.somersaulted and not self.on_floor:
			speed = self.somersault_ending()
			
		elif self.crouching:
			speed = self.crouching_speed

		elif self.sliding:
			speed = self.slide_speed
			self.slide(dt)

		else:
			speed = self.horizontal_speed

			if self.exhausted:
				if self.direction.x != 0:
					sign = self.direction.x/abs(self.direction.x)
				else:
					sign = 0

				self.direction.x = sign * min(abs(self.direction.x),abs(self.exhausted_direction*sign))


		self.pos.x += speed * dt * self.direction.x
		self.rect.left = round(self.pos.x)
		self.hitbox.left = self.get_hitbox_topleft()[0]


	def climb(self, dt, controls):
		self.direction.y = controls['vertical movement']

		self.pos.y += self.direction.y * dt * self.climbing_speed
		self.rect.top = round(self.pos.y)
		self.hitbox.top = self.get_hitbox_topleft()[1]

	def apply_gravity(self, dt):
		self.direction.y += self.gravity * dt

	def apply_jump_increment(self, dt, controls):
		if not controls['jump'] or self.direction.y > 0:
			self.jump_increment_activated = False

		if self.jump_increment_activated:
			self.direction.y -= self.jump_increment_speed * dt

	def vertical_movement(self, dt, controls):
		if not self.falling_dead_hitted_floor and self.falling_dead_hit_floor:
			self.direction.y = -self.dead_floor_hit_bounce_falling_speed_percent * self.last_direction_y_no_floor

		elif self.climbing:
			self.climb(dt, controls)

		else:
			if self.was_climbing:
				self.direction.y = 0

			self.apply_gravity(dt)

			self.apply_jump_increment(dt, controls)

			if self.pressing_down and self.direction.y > 0:
				fall_speed = self.fall_acceleration_speed_coefficient
			else:
				fall_speed = 1

			self.pos.y += self.direction.y * dt * fall_speed
			self.rect.top = round(self.pos.y)
			self.hitbox.top = self.get_hitbox_topleft()[1]


	# noise
	def get_noise_degree(self):
		self.noise_degree = 50 if self.crouching else 100


	# hitting attackables
	def get_attack_power(self):
		if self.sword_attacking:
			self.attack_power = 7 + (3 * self.sword_attack_index)
		elif self.sliding:
			self.attack_power = 10

	def hit_attackables(self):
		if self.melee_attack_mask:
			
			for sprite in self.attackable_sprites:
				if sprite.hitbox.colliderect(self.hitbox):

					offset = (sprite.rect.left - self.rect.left, sprite.rect.top - self.rect.top)

					if self.melee_attack_mask.overlap(sprite.mask,offset):
						sprite.take_damage(self.attack_power)


	# ...
	def filter_gerunds(self, dt):
		if self.deathing:
			self.sliding = False
			self.climbing = False
			self.direction.x = max(0, self.direction.x - 0.1 * dt) if not self.on_floor else 0

		self.running = abs(self.direction.x) >= self.direction_min_running_value and self.has_enough_stamina('running', dt)

		if self.preparing_to_jump:
			self.direction.x = 0
			self.crouching = False
			self.sliding = False
			self.climbing = False
			self.running = False

		if self.sliding:
			self.preparing_to_jump = False
			self.climbing = False
			self.crouching = False
			self.drawing_sword = False
			self.sword_attacking = False
			self.running = False

		if self.on_floor:
			self.somersaulting = False
			self.somersaulted = False
		else:
			self.drawing_sword = False
			self.sheathing_sword = False
			self.running = False

		if self.wall_colliding:
			pass
		else:
			self.climbing = False

		self.climbing = self.climbing and self.has_enough_stamina('climbing', dt)

		if self.climbing:
			self.direction.x = 0
			self.crouching = False
			self.sliding = False
			self.somersaulting = False
			self.drawing_sword = False
			self.sheathing_sword = False
			self.sword_attacking = False
			self.running = False

		if self.drawing_sword:
			self.direction.x = 0
			self.crouching = False
			self.sliding = False
			self.somersaulting = False
			self.climbing = False
			self.sheathing_sword = False
			self.preparing_to_jump = False
			self.running = False

		if self.sheathing_sword:
			self.direction.x = 0
			self.crouching = False
			self.sliding = False
			self.somersaulting = False
			self.climbing = False
			self.drawing_sword = False
			self.preparing_to_jump = False
			self.running = False

		if self.sword_attacking:
			self.direction.x = 0
			self.crouching = False
			self.sliding = False
			self.somersaulting = False
			self.climbing = False
			self.sheathing_sword = False
			self.drawing_sword = False
			self.preparing_to_jump = False
			self.running = False


	# animation
	def animation_update(self):
		# DIRECTION
		if self.direction.x > 0:
			self.animation_direction = 'right'
		elif self.direction.x < 0:
			self.animation_direction = 'left'

		# STATE
		if self.on_floor:
			if self.deathing:
				if self.died_in_the_air:
					if self.falling_dead_hit_floor and not self.falling_dead_hitted_floor:
						if self.direction.y <= 0:
							self.animation_state = 'death fall floor hit up'
					else:
						self.animation_state = 'death fall floor hit'
				else:
					self.animation_state = 'death'
			elif self.preparing_to_jump:
				self.animation_state = 'jump prepare'
			elif self.direction.x != 0:
				if self.running:
					self.animation_state = 'run'
				else:
					self.animation_state = 'walk'
			else:
				self.animation_state = 'idle sword' if self.sword_drawed else 'idle'

			if self.crouching:
				self.animation_state = self.animation_state.split(' ')[0] + ' crouch'
			elif self.sliding:
				self.animation_state = 'slide'

			if self.drawing_sword:
				self.animation_state = 'sword draw'
			elif self.sheathing_sword:
				self.animation_state = 'sword sheathe'
			elif self.sword_attacking:
				self.animation_state = 'sword attack ' +\
				 str(self.sword_attack_combo[self.sword_attack_index])

		else:
			if self.deathing:
				if not self.falling_dead_hit_floor:
					self.animation_state = 'death fall'
				elif self.direction.y > 0:
					self.animation_state = 'death fall floor hit down'
			elif self.somersaulting:
				self.animation_state = 'somersault'
			elif self.direction.y <= 0:
				self.animation_state = 'jump'
			else:
				self.animation_state = 'fall'

		if self.climbing:
			self.animation_state = 'climb'

		# SPEED
		if self.animation_state == 'run':
			self.animation_speed_var = abs(self.direction.x)

		elif self.animation_state == 'walk':
			self.animation_speed_var = abs(self.direction.x)*1.43 # max: 1 = 0.7 * 1.43
			self.animation_speed_var = max(0.6, self.animation_speed_var)

		elif self.animation_state == 'climb':
			self.animation_state_var = abs(self.direction.y)

		else:
			self.animation_speed_var = 1

		# SWORD
		if self.animation_state in WITH_OR_NOT_SWORD_ANIMAION_STATES:
			if self.has_sword:
				self.animation_state += ' sword'

		if self.animation_state in SWORD_ON_OR_OFF_ANIMAION_STATES:
			if self.sword_drawed:
				self.animation_state += ' drawed'
			else:
				self.animation_state += ' sheathed'

	def process_frame_index(self, current_animation, dt):
		# reseting when animation change
		if self.last_animation_state != self.animation_state:
			self.frame_index = 0

		# frame index direction
		self.frame_index_direction = 1

		if self.deathing:
			if int(self.frame_index) == len(current_animation)-1:
				self.frame_index_direction = 0

		elif self.climbing:
			if self.direction.y > 0:
				self.frame_index_direction = 1
			elif self.direction.y < 0:
				self.frame_index_direction = -1
			else:
				self.frame_index_direction = 0

		# increasing
		self.frame_index += ANIMATION_SPEEDS['player'][self.animation_state] *\
		 self.animation_speed_var * dt * self.frame_index_direction

		# loop below zero
		if self.frame_index < 0:
			self.frame_index = len(current_animation)-0.01

		# limiting/reseting when loops
		if self.frame_index >= len(current_animation):
			self.frame_index = 0

			if self.preparing_to_jump:
				self.preparing_to_jump = False
				self.jump()

			elif self.somersaulting:
				self.somersaulting = False

			elif self.sliding:
				self.sliding = False
				self.slide_speed = self.slide_initial_speed

				self.slide_cooldown.start()

			elif self.drawing_sword:
				self.drawing_sword = False
				self.sword_drawed = True

			elif self.sheathing_sword:
				self.sheathing_sword = False
				self.sword_drawed = False

			elif self.sword_attacking:
				self.sword_attack_index += 1
				if self.sword_attack_index == len(self.sword_attack_combo):

					self.sword_attack_cooldown.milliseconds =\
					 self.sword_attack_cooldown_milliseconds[len(self.sword_attack_combo)-1]
					self.sword_attack_cooldown.start()

					self.sword_attack_combo = []
					self.sword_attack_index = 0
					self.sword_attacking = False

	def animate(self, dt):
		current_animation = self.animations[self.animation_direction][self.animation_state]

		self.process_frame_index(current_animation, dt)

		self.image = current_animation[int(self.frame_index)]


	# update
	def last_variables(self):
		# was, last, before
		self.old_rect = self.rect.copy()
		self.old_hitbox = self.hitbox.copy()

		self.last_animation_state = self.animation_state
		self.was_climbing = self.climbing
		self.last_image = self.image

		self.last_hearts = self.hearts
		self.last_stamina = self.stamina

		self.falling_dead_hitted_floor = self.falling_dead_hit_floor

		if not self.on_floor:
			self.last_direction_y_no_floor = self.direction.y

	def update_timers(self):
		self.slide_cooldown.update()

		self.toggle_climb_cooldown.update()

		self.sword_attack_combo_cooldown.update()
		self.sword_attack_cooldown.update()

		self.invulnerability_cooldown.update()
		self.recover_hearts_cooldown.update()
		self.add_heart_cooldown.update()

		self.get_more_stamina_cooldown.update()

		self.sword_toggle_cooldown.update()

		self.blink_wave.run()

	def update(self, dt):
		self.update_timers()
		self.last_variables()

		joydata = self.get_joydata()
		keys = pygame.key.get_pressed()
		controls = self.get_controls(joydata, keys)

		self.input(controls, dt)

		self.recover_stamina(dt)

		self.create_melee_attack_mask()

		self.filter_gerunds(dt)

		self.get_noise_degree()

		self.stamina_spending(dt)

		self.horizontal_movement(dt)
		self.horizontal_collision()
		self.vertical_movement(dt, controls)
		self.vertical_collision()

		self.check_wall_floor()

		self.animation_update()
		self.animate(dt)
		self.blink()

		if self.update_mask_hitbox():
			self.create_melee_attack_mask()

			self.horizontal_collision()
			self.vertical_collision()

			self.check_wall_floor()

		self.get_attack_power()
		self.hit_attackables()

		self.check_damage()
		self.check_death()
