import pygame, support

from math import radians, ceil

from settings import *


class UI(pygame.sprite.Group):
	def __init__(self, hearts_group, monster_sprites):
		super().__init__()

		self.display_surface = pygame.display.get_surface()
		self.display_surface_center =\
			pygame.math.Vector2(self.display_surface.get_width()//2, self.display_surface.get_height()//2)

		self.hearts_group = hearts_group

		self.stamina_wheel = StaminaWheel()

		self.fps_display = FPSDisplay()

		self.monster_sprites = monster_sprites
		self.monsters_health_bars = []

		self.create_monsters_health_bar()

	def create_monsters_health_bar(self):
		for sprite in self.monster_sprites:
			self.monsters_health_bars.append(FluidBar((120,10),(114,6),
				('midbottom','rect','midtop',(0,100)),
				'#181a17','red','health',sprite.health,sprite.health,'dead',self.destroy_monsters_health_bar,sprite))

	def destroy_monsters_health_bar(self, bar):
		self.monsters_health_bars.remove(bar)

	def get_camera_offset(self, player):
		return player.rect.center - self.display_surface_center

	def custom_draw(self, player, dt):
		# general
		for sprite in self.sprites():
			self.display_surface.blit(sprite.image, sprite.rect)

		# hearts
		self.display_hearts(player)

		# stamina
		self.display_stamina(player)

		# fps
		self.display_fps(dt)

		# monster health bar
		self.display_monsters_health_bar(player)

	def display_monsters_health_bar(self, player):
		for bar in self.monsters_health_bars:
			bar.update()
			bar.draw(self.display_surface, self.get_camera_offset(player))	

	def display_hearts(self, player):
		full_hearts = player.hearts // 1
		fragmented_heart = player.hearts % 1
		for n, heart in enumerate(self.hearts_group):
			self.update_hearts(full_hearts, fragmented_heart, player, n, heart)
			self.display_surface.blit(heart.image, heart.rect)

	def display_stamina(self, player):
		self.stamina_wheel.update(player)
		self.stamina_wheel.draw(self.display_surface)

	def display_fps(self, dt):
		self.fps_display.update(dt)
		self.fps_display.display(self.display_surface)

	def update_hearts(self, full_hearts, fragmented_heart, player, n, heart):
		if player.hearts != player.last_hearts:
			if n < full_hearts:
				heart_fraction = 1
			elif n == full_hearts:
				heart_fraction = fragmented_heart
			else:
				heart_fraction = 0

			heart.update(int(heart_fraction*4))


class Heart(pygame.sprite.Sprite):
	def __init__(self, surfaces, pos, groups, fraction):
		super().__init__(groups)

		self.surfaces = support.invert(surfaces)
		self.surface_index = int(fraction*4)
		self.image = self.surfaces[self.surface_index]
		self.rect = self.image.get_rect(**pos)

	def update(self, new_index):
		self.surface_index = new_index
		self.image = self.surfaces[self.surface_index]


class StaminaWheel:
	def __init__(self):
		self.rect = pygame.Rect(STAMINA_WHEEL_POS,STAMINA_WHEEL_SIZE)

		self.last_stamina_degrees = 0

	def update(self, player):
		self.max_stamina_degrees = (player.max_stamina / FULL_STAMINA_WHEEL_UNITS * 360)

		if player.spending_stamina:
			self.last_stamina_degrees = (player.last_stamina / player.max_stamina * self.max_stamina_degrees)

		self.stamina_degrees = (player.stamina / player.max_stamina * self.max_stamina_degrees)

		self.full = self.stamina_degrees >= self.max_stamina_degrees

		self.exhausted = player.exhausted

	def draw(self, display_surface):
		if not self.full:
			stamina_wheels = ceil(self.max_stamina_degrees / 360)

			max_stamina_degrees = self.max_stamina_degrees
			last_stamina_degrees = self.last_stamina_degrees
			stamina_degrees = self.stamina_degrees

			for wheel in range(stamina_wheels):
				data = [
					(MAX_STAMINA_WHEEL_COLOR, min(max_stamina_degrees,360)),
					(LAST_STAMINA_WHEEL_COLOR, (min(last_stamina_degrees,360)*1.05)),
					(EXHAUSTED_STAMINA_WHEEL_COLOR if self.exhausted else STAMINA_WHEEL_COLOR, min(360,stamina_degrees))]

				for color, degrees in data:
					pygame.draw.arc(
						display_surface,
						color,
						self.rect.inflate(2*STAMINA_WHEEL_RADIUS_DISTANCE*wheel,2*STAMINA_WHEEL_RADIUS_DISTANCE*wheel),
						radians(STAMINA_WHEEL_START_DEGREE),
						radians(degrees+STAMINA_WHEEL_START_DEGREE),
						MAIN_STAMINA_WHEEL_THICKNESS if wheel == 0 else STAMINA_WHEEL_THICKNESS)

				max_stamina_degrees = max_stamina_degrees - 360 if max_stamina_degrees >= 360 else 0
				last_stamina_degrees = last_stamina_degrees - 360 if last_stamina_degrees >= 360 else 0
				stamina_degrees = stamina_degrees - 360 if stamina_degrees >= 360 else 0


class FPSDisplay:
    def __init__(self):
        self.fps = 0
        self.frame_count = 0
        self.fps_sum = 0

        self.counter = 0
        self.update_interval = 0.5 # seconds

        self.font = pygame.font.Font('../fonts/Montaga-Regular.ttf', 25)
        self.surface = self.font.render(str(self.fps), True, 'white')
        self.rect = pygame.Rect((WINDOW_WIDTH - 200, 0, 200, 40))

    def update(self, dt):
        self.counter += dt
        self.frame_count += 1
        self.fps_sum += 1 / dt

        if self.counter >= self.update_interval:
            self.fps = self.fps_sum / self.frame_count
            self.surface = self.font.render(f'fps: {int(self.fps)}', True, 'white')

            self.counter = 0
            self.frame_count = 0
            self.fps_sum = 0

    def display(self, display_surface):
        pygame.draw.rect(display_surface, 'black', self.rect)
        display_surface.blit(self.surface, self.rect)


class FluidBar:
	def __init__(self, bg_dimensions, fluid_dimensions, bg_pos_info, bg_color, fluid_color, fluid_source, start_fluid, max_fluid, destroy_source, destruction_function, sprite):
		self.set_pos_anchor = bg_pos_info[0]
		self.pos_obj = bg_pos_info[1]
		self.get_pos_anchor = bg_pos_info[2]
		self.pos_offset = bg_pos_info[3]

		self.padx = max(0,(bg_dimensions[0]-fluid_dimensions[0])//2)

		self.sprite = sprite

		self.bg_color = bg_color
		self.fluid_color = fluid_color

		self.bg_rect = pygame.Rect((0,0),bg_dimensions)
		self.fluid_rect = pygame.Rect((0,0),fluid_dimensions)

		self.max_fluid = max_fluid
		self.fluid_rect_max_width = fluid_dimensions[0]
		self.fluid_source = fluid_source
		self.current_fluid = start_fluid

		self.destroy_source = destroy_source
		self.destruction_function = destruction_function

	def get_current_fluid(self):
		self.current_fluid = getattr(self.sprite, self.fluid_source)

	def get_pos(self):
		pos_offset = self.pos_offset
		pos_obj = getattr(self.sprite, self.pos_obj)
		get_pos = getattr(pos_obj, self.get_pos_anchor)

		if isinstance(self.pos_offset, (tuple, list)):
			pos_offset = pygame.math.Vector2(pos_offset)
			get_pos = pygame.math.Vector2(get_pos)

		return pos_offset + get_pos

	def get_camera_offset_rect(self, source_rect, camera_offset):
		offset_rect = source_rect.copy()
		offset_rect.center = pygame.math.Vector2(offset_rect.center) - camera_offset

		return offset_rect

	def get_current_fluid_width(self):
		return self.current_fluid / self.max_fluid * self.fluid_rect_max_width

	def place_fluid_rect(self):
		self.fluid_rect.midleft = (self.bg_rect.left+self.padx,self.bg_rect.centery)

	def check_destruction(self):
		if getattr(self.sprite, self.destroy_source):
			self.destruction_function(self)

	def update(self):
		self.get_current_fluid()

		setattr(self.bg_rect, self.set_pos_anchor, self.get_pos())
		self.place_fluid_rect()

		self.fluid_rect.width = self.get_current_fluid_width()

		self.check_destruction()

	def draw(self, display_surface, camera_offset):
		pygame.draw.rect(display_surface,self.bg_color,self.get_camera_offset_rect(self.bg_rect, camera_offset))
		pygame.draw.rect(display_surface,self.fluid_color,self.get_camera_offset_rect(self.fluid_rect, camera_offset))
