import pygame, sys

from settings import *
from support import *

from math import sin


class VictoryScreen:
	def __init__(self, transition):
		self.transition = transition

		self.display_surface = pygame.display.get_surface()

		self.font = pygame.font.Font(GAME_OVER_FONT_PATH, GAME_OVER_FONT_SIZE)
		self.text_sprites = []

		self.fill_sprites('VICTORY', (WINDOW_CENTER[0], WINDOW_HEIGHT))

		self.text_rect_speed = 40
		self.centered = False

		# sounds
		self.music = pygame.mixer.Sound('../audio/Victory.mp3')
		self.music_played = False
	
	def fill_sprites(self, text, center):
		positions = self.get_positions(text, center)

		for char, pos in zip(text, positions):
			surf = self.font.render(char,False,VICTORY_TEXT_COLOR)
			rect = surf.get_rect(topleft=pos)

			self.text_sprites.append((surf, rect))

	def get_positions(self, text, center):
		positions = []

		full_rect = self.font.render(text, False, 'black').get_rect(center=center)
		start_x, start_y = (full_rect.x, full_rect.y)
		x = start_x

		for char in text:
			width = self.font.render(char, False, 'black').get_width()
			pos = (x, start_y)
			x += width

			positions.append(pos)

		return positions

	def event_loop(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.transition.active = True

	def update(self, dt):
		if not self.centered:
			for _, rect in self.text_sprites:
				rect.centery -= self.text_rect_speed * dt
				if rect.centery <= WINDOW_CENTER[1]:
					self.centered = True
		else:
			pass

	def display(self):
		self.display_surface.fill(GAME_OVER_BG_COLOR)

		for surf, rect in self.text_sprites:
			self.display_surface.blit(surf, rect)

	def play_sounds(self):
		if not self.music_played:
			self.music.play()
			self.music_played = True	

	def run(self, dt):
		self.play_sounds()

		self.event_loop()

		self.update(dt)
		self.display()


class GameDefeatScreen:
	def __init__(self, transition, start_color, text='GAME OVER', animation_speed=1.0015):
		self.transition = transition

		self.display_surface = pygame.display.get_surface()
		self.font = pygame.font.Font(GAME_OVER_FONT_PATH, GAME_OVER_FONT_SIZE)

		self.text = text

		self.start_color = start_color

		self.RGB = hex_color_to_decimal(start_color)
		self.text_color = decimal_color_to_hex(self.RGB)
		self.text_surf = self.font.render(self.text, False, self.text_color)
		self.text_rect = self.text_surf.get_rect(center=WINDOW_CENTER)

		self.animation_speed = animation_speed

		# sounds
		self.music = pygame.mixer.Sound('../audio/Death.mp3')
		self.music_played = False

	def reset_RGB(self):
		self.RGB = hex_color_to_decimal(self.start_color)

	def event_loop(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.transition.active = True

	def get_color(self, dt):
		self.RGB[0] *= self.animation_speed
		self.RGB[1] *= self.animation_speed
		self.RGB[2] *= self.animation_speed

		for i, channel in enumerate(self.RGB):
			if channel >= 255:
				self.RGB[i] = 255
				return self.text_color

		red = hex(int(self.RGB[0])).split('x')[1].zfill(2)
		green = hex(int(self.RGB[1])).split('x')[1].zfill(2)
		blue = hex(int(self.RGB[2])).split('x')[1].zfill(2)

		hex_string = '#' + red + green + blue

		return hex_string

	def update(self, dt):
		self.text_color = self.get_color(dt)
		self.text_surf = self.font.render(self.text, False, self.text_color)

	def display(self):
		self.display_surface.fill(GAME_OVER_BG_COLOR)
		self.display_surface.blit(self.text_surf, self.text_rect)

	def play_sounds(self):
		if not self.music_played:
			self.music.play()
			self.music_played = True

	def run(self, dt):
		self.play_sounds()

		self.event_loop()

		self.update(dt)
		self.display()
