import pygame
from pygame.image import load
from settings import *
from support import num_loop

class Menu:
	def __init__(self):
		self.display_surface = pygame.display.get_surface()
		self.import_data()
		self.create_buttons()

	def import_data(self):
		self.menu_surfs = {}
		for key, value in EDITOR_DATA.items():
			if value['menu']:
				if value['menu'] not in self.menu_surfs.keys():
					self.menu_surfs[value['menu']] =\
					 [(key,load(value['menu_surf']).convert_alpha())]
				else:
					self.menu_surfs[value['menu']].\
					 append((key,load(value['menu_surf']).convert_alpha()))

	def create_buttons(self):
		# menu general rect
		size = MENU_GENERAL_RECT_SIZE
		margin = MENU_GENERAL_RECT_MARGIN
		l = WINDOW_WIDTH - (margin+size)
		t = WINDOW_HEIGHT - (margin+size)
		self.rect = pygame.Rect(l,t,size,size)

		# buttons rect
		generic_button_rect = pygame.Rect(self.rect.topleft,
			(size/2, size/2))
		button_margin = MENU_BUTTON_MARGIN

		self.tile_button_rect =\
		 generic_button_rect.copy().inflate(-button_margin*2,-button_margin*2)
		self.coin_button_rect =\
		 generic_button_rect.move(size/2,0).inflate(-button_margin*2,-button_margin*2)
		self.enemy_button_rect =\
		 generic_button_rect.move(0,size/2).inflate(-button_margin*2,-button_margin*2)
		self.palm_button_rect =\
		 generic_button_rect.move(size/2,size/2).\
		 inflate(-button_margin*2,-button_margin*2)

		# button objects
		self.buttons = pygame.sprite.Group()

		Button(self.tile_button_rect, self.buttons, self.menu_surfs['terrain'])
		Button(self.coin_button_rect, self.buttons, self.menu_surfs['coin'])
		Button(self.enemy_button_rect, self.buttons, self.menu_surfs['enemy'])
		Button(self.palm_button_rect, self.buttons, self.menu_surfs['palm fg'],
			self.menu_surfs['palm bg'])

	def click(self, mouse_pos, mouse_buttons):
		for button in self.buttons:
			if button.rect.collidepoint(mouse_pos):
				if mouse_buttons[1]: # middle mouse button click
					button.main_active = not button.main_active\
					 if button.items['alt'] else True
				if mouse_buttons[2]: # right mouse button click
					button.switch(1)
				return button.get_id()


	def highlight_indicator(self, index):
		match EDITOR_DATA[index]['menu']:
			case 'terrain':
				rect = self.tile_button_rect
			case 'coin':
				rect = self.coin_button_rect
			case 'enemy':
				rect = self.enemy_button_rect
			case 'palm fg':
				rect = self.palm_button_rect
			case 'palm bg':
				rect = self.palm_button_rect

		self.highlight_rect = rect
		pygame.draw.rect(self.display_surface, BUTTON_LINE_COLOR,
			rect.inflate(HIGHLIGHT_INFLATE),
			HIGHLIGHT_WIDTH, HIGHLIGHT_RADIUS)

	def display(self, index):
		self.buttons.update()
		self.buttons.draw(self.display_surface)
		self.highlight_indicator(index)
		# self.debug()

	def debug(self):
		# pygame.draw.rect(self.display_surface, 'red', self.rect)
		pygame.draw.rect(self.display_surface, 'blue', self.tile_button_rect)
		pygame.draw.rect(self.display_surface, 'yellow', self.coin_button_rect)
		pygame.draw.rect(self.display_surface, 'orange', self.enemy_button_rect)
		pygame.draw.rect(self.display_surface, 'green', self.palm_button_rect)


class Button(pygame.sprite.Sprite):
	def __init__(self, rect, group, items, items_alt=None):
		super().__init__(group)
		self.image = pygame.Surface(rect.size)
		self.rect = rect

		# items
		self.items = {'main': items, 'alt': items_alt}
		self.index = 0
		self.main_active = True

	def get_id(self):
		return self.items['main' if self.main_active else 'alt'][self.index][0]

	def switch(self, increment):
		self.index += increment
		self.index = num_loop(self.index,
			0, len(self.items['main' if self.main_active else 'alt'])-1)

	def update(self):
		self.image.fill(BUTTON_BG_COLOR)
		surf = self.items['main' if self.main_active else 'alt'][self.index][1]
		rect = surf.get_rect(center=(self.rect.width/2,self.rect.height/2))
		self.image.blit(surf,rect)
		# remeber, we are bliting in the self.image, because that,
		# we can't use the self.rect.center, the value is too large.
		# This happens because the self.rect reference surface is the display one,
		# in this case the self.image is the actual surface.
