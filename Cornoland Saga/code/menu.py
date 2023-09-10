import pygame, sys, support

from joystick_constants import *
from settings import *

from math import ceil
from time_handling import Cooldown


class Menu:
	def __init__(self, graphics, switch):
		self.graphics = graphics
		self.switch = switch

		self.display_surface = pygame.display.get_surface()
		self.window_width = self.display_surface.get_width()
		self.window_height = self.display_surface.get_height()

		self.logo = Logo(self.graphics['menu']['logo'],
			{'center': (self.window_width*MENU_LOGO_RELPOS[0], self.window_height*MENU_LOGO_RELPOS[1])})
		self.player = MenuPlayer(self.graphics['player']['right']['run sword sheathed'])
		self.background = MenuBackground(
			self.graphics['menu']['background']['bg'],
			self.graphics['menu']['background']['fg'])
		self.filter = ColorFilter('white', 100, (self.window_width, self.window_height), {'topleft':(0,0)})
		self.filter2 = ColorFilter('white', 30, (self.window_width, self.window_height), {'topleft':(0,0)})

		self.joystick = None

		self.buttons = ButtonGroup()
		self.set_buttons()

		self.selection_index = 0
		self.button_select_cooldown = Cooldown(150)

		self.select_button()

	def set_buttons(self):
		button_surfaces = [
			self.graphics['menu']['buttons']['main'],
			self.graphics['menu']['buttons']['hover'],
			self.graphics['menu']['buttons']['press']]

		font = pygame.font.Font('../fonts/Montaga-Regular.ttf', MENU_BUTTONS_FONT_SIZE)
		AA = True

		self.play_button = Button(
			pos={'center': (self.window_width*MENU_BUTTONS_RELPOS['play'][0],self.window_height*MENU_BUTTONS_RELPOS['play'][1])},
			command=lambda: self.switch('level'),
			surfaces=button_surfaces,
			groups=[self.buttons],
			widths=self.window_width*MENU_BUTTONS_RELWIDTH,
			heights=self.window_height*MENU_BUTTONS_RELHEIGHT,
			has_border=True,
			border_colors=MENU_BUTTONS_BORDER_COLORS,
			texts='PLAY',
			fonts=font,
			AA=AA,
			text_anchors='center',
			text_colors=MENU_BUTTONS_TEXT_COLORS,
			index=0
			)

		self.exit_button = Button(
			pos={'center': (self.window_width*MENU_BUTTONS_RELPOS['exit'][0],self.window_height*MENU_BUTTONS_RELPOS['exit'][1])},
			command=self.exit,
			surfaces=button_surfaces,
			groups=[self.buttons],
			widths=self.window_width*MENU_BUTTONS_RELWIDTH,
			heights=self.window_height*MENU_BUTTONS_RELHEIGHT,
			has_border=True,
			border_colors=MENU_BUTTONS_BORDER_COLORS,
			texts='EXIT',
			fonts=font,
			AA=AA,
			text_anchors='center',
			text_colors=MENU_BUTTONS_TEXT_COLORS,
			index=1
			)

	def exit(self):
		pygame.quit()
		sys.exit()

	def input(self):
		if self.joystick:
			play = self.joystick.get_button(START)
			up_down = ceil(self.joystick.get_axis(V_LEFT_AXIS)) or -1*self.joystick.get_hat(LEFT_HAT)[1]
			button_press = self.joystick.get_button(CROSS)
		else:
			keys = pygame.key.get_pressed()
			play = keys[pygame.K_RETURN]

			if keys[pygame.K_UP]:
				up_down = 1
			elif keys[pygame.K_DOWN]:
				up_down = -1
			else:
				up_down = 0

			button_press = keys[pygame.K_x]
		
		if play:
			self.switch('level')

		if not self.button_select_cooldown.on and not button_press:
			self.selection_index += up_down
			self.selection_index = support.loop(self.selection_index, 0, len(self.buttons.sprites())-1)

			self.button_select_cooldown.start()

		self.call_button_command(button_press)

	def select_button(self):
		for button in self.buttons.sprites():
			button.selected = button.index == self.selection_index

	def call_button_command(self, button_press):
		for button in self.buttons.sprites():
			button.joykey_pressed = button.selected and button_press

	def cooldowns(self):
		self.button_select_cooldown.update()

	def update(self, dt):
		self.cooldowns()

		self.input()

		self.select_button()

		self.background.update(dt)
		self.logo.update(dt)
		self.player.update(dt)
		self.buttons.update(dt)

	def draw(self):
		self.background.draw()
		self.filter.apply(self.display_surface)
		self.player.draw()
		self.filter2.apply(self.display_surface)
		self.logo.draw()
		self.buttons.custom_draw()


class Logo:
	def __init__(self, surface, pos):
		self.display_surface = pygame.display.get_surface()

		self.image = surface
		self.rect = self.image.get_rect(**pos)
		self.alpha = 0
		self.alpha_speed = 60
		self.image.set_alpha(self.alpha)

	def increase_alpha(self, dt):
		if self.alpha < 255:
			self.alpha += self.alpha_speed * dt
			self.alpha = min(255, self.alpha)

			self.image.set_alpha(self.alpha)

	def update(self, dt):
		self.increase_alpha(dt)

	def draw(self):
		self.display_surface.blit(self.image, self.rect)


class MenuPlayer:
	def __init__(self, animation):
		self.display_surface = pygame.display.get_surface()
		self.window_width = self.display_surface.get_width()
		self.window_height = self.display_surface.get_height()	

		self.animation = animation
		self.animation_speed = 8
		self.frame_index = 0

		self.image = self.animation[self.frame_index]
		self.rect = self.image.get_rect(midbottom=(self.window_width/2,self.window_height*(6/7)))

		self.set_alpha()

	def set_alpha(self):
		for surf in self.animation:
			surf.set_alpha(255//1)

	def animate(self, dt):
		self.frame_index += self.animation_speed * dt

		if self.frame_index >= len(self.animation):
			self.frame_index = 0

		self.image = self.animation[int(self.frame_index)]
	
	def update(self, dt):
		self.animate(dt)

	def draw(self):
		self.display_surface.blit(self.image, self.rect)


class MenuBackground:
	def __init__(self, bg, fg):
		self.display_surface = pygame.display.get_surface()
		self.window_width = self.display_surface.get_width()
		self.window_height = self.display_surface.get_height()	

		self.bg = self.scale(bg)
		self.fg = self.scale(fg)

		self.bg.set_alpha(255//1)
		self.fg.set_alpha(255//1)

		self.rects = {}
		self.positions = {}

		self.rects['bg 1'] = self.bg.get_rect(topleft=(0,0))
		self.positions['bg 1']= pygame.math.Vector2(self.rects['bg 1'].topleft)
		self.rects['bg 2'] = self.bg.get_rect(topleft=(self.window_width,0))
		self.positions['bg 2']= pygame.math.Vector2(self.rects['bg 2'].topleft)

		self.rects['fg 1'] = self.fg.get_rect(topleft=(0,0))
		self.positions['fg 1']= pygame.math.Vector2(self.rects['fg 1'].topleft)
		self.rects['fg 2'] = self.fg.get_rect(topleft=(self.window_width,0))
		self.positions['fg 2']= pygame.math.Vector2(self.rects['fg 2'].topleft)

		self.speed = 350

	def scale(self, surf):
		w, h = surf.get_width(), surf.get_height()

		surf_bottomright = pygame.math.Vector2(w,h)
		display_bottomright = pygame.math.Vector2(self.window_width,self.window_height)

		distance_from_surf_to_display_bottomright = display_bottomright - surf_bottomright
		x = distance_from_surf_to_display_bottomright.x
		y = distance_from_surf_to_display_bottomright.y

		scaled_surf = pygame.transform.scale(surf,(w+x, h+y))

		return scaled_surf

	def move(self, dt):
		for key in ('bg 1', 'bg 2', 'fg 1', 'fg 2'):
			self.positions[key].x -= self.speed * dt
			self.rects[key].x = round(self.positions[key].x)

	def loop(self):
		for key in ('bg 1', 'bg 2', 'fg 1', 'fg 2'):
			if self.rects[key].right <= 0:
				next_rect_key = key.split(' ')[0]+' '
				next_rect_key += '2' if '1' in key else '1'

				self.rects[key].left = self.rects[next_rect_key].right
				self.positions[key].x = self.rects[key].x

	def update(self, dt):
		self.move(dt)
		self.loop()

	def draw(self):
		self.display_surface.blit(self.bg, self.rects['bg 1'])
		self.display_surface.blit(self.bg, self.rects['bg 2'])

		self.display_surface.blit(self.fg, self.rects['fg 1'])
		self.display_surface.blit(self.fg, self.rects['fg 2'])


class ButtonGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()

		self.display_surface = pygame.display.get_surface()

	def custom_draw(self):
		for button in self.sprites():
			self.display_surface.blit(button.image, button.rect)
			button.image.blit(button.font_surface, button.font_rect)


class Button(pygame.sprite.Sprite):
	def __init__(self, pos, command, surfaces, groups, widths=None, heights=None, has_border=False, border_colors=('red','green','blue'), texts=None, text_colors=('red','green','blue'), fonts=None, AA=False, text_anchors='topleft', index=None):
		super().__init__(groups)

		main_surface, hover_surface, press_surface = surfaces

		self.index = index
		self.command = command

		self.widths = widths
		self.heights = heights


		self.main_surface = self.scale(main_surface, 0)
		self.hover_surface = self.scale(hover_surface, 1)
		self.press_surface = self.scale(press_surface, 2)

		pos = self.get_list_attributes(pos)
		self.main_rect = self.main_surface.get_rect(**pos[0])
		self.hover_rect = self.hover_surface.get_rect(**pos[1])
		self.press_rect = self.press_surface.get_rect(**pos[2])

		self.main_mask = pygame.mask.from_surface(self.main_surface)
		self.hover_mask = pygame.mask.from_surface(self.hover_surface)
		self.press_mask = pygame.mask.from_surface(self.press_surface)

		self.image = self.main_surface
		self.rect = self.main_rect
		self.mask = self.main_mask

		self.hovering = False
		self.pressing = False
		self.was_pressing = self.pressing

		self.has_border = has_border
		self.border_colors = border_colors

		if texts:
			fonts = fonts if fonts else pygame.font.SysFont('Calibri', 20)

			self.render_text(texts, text_colors, text_anchors, fonts, AA)

		self.alpha = 0
		self.alpha_speed = 60
		self.image.set_alpha(self.alpha)

		# joystick/keyboard
		self.joykey_pressed = False
		self.selected = False

	def increase_alpha(self, dt):
		if self.alpha < 255:
			self.alpha += self.alpha_speed * dt
			self.alpha = min(255, self.alpha)

			self.main_surface.set_alpha(self.alpha)
			self.hover_surface.set_alpha(self.alpha)
			self.press_surface.set_alpha(self.alpha)

	def get_list_attributes(self, attr):
		attr_list = [*attr].copy() if isinstance(attr, (list, tuple)) else attr

		if isinstance(attr, (list, tuple)):
			for i in range(3-len(attr)):
				attr_list.append(attr[0])
		else:
			attr_list = [attr]*3

		return attr_list

	def render_text(self, texts, colors, anchors, fonts, AA):
		texts = self.get_list_attributes(texts)
		colors = self.get_list_attributes(colors)
		anchors = self.get_list_attributes(anchors)
		fonts = self.get_list_attributes(fonts)

		self.main_font = fonts[0].render(texts[0], AA, colors[0])
		self.hover_font = fonts[1].render(texts[1], AA, colors[1])
		self.press_font = fonts[2].render(texts[2], AA, colors[2])

		self.main_font_rect = self.main_font.get_rect()
		self.hover_font_rect = self.hover_font.get_rect()
		self.press_font_rect = self.press_font.get_rect()

		setattr(self.main_font_rect, anchors[0], self.convert_pos(getattr(self.main_rect, anchors[0])))
		setattr(self.hover_font_rect, anchors[1], self.convert_pos(getattr(self.hover_rect, anchors[1])))
		setattr(self.press_font_rect, anchors[2], self.convert_pos(getattr(self.press_rect, anchors[2])))

	def convert_pos(self, pos):
		x = pos[0] - self.rect.x
		y = pos[1] - self.rect.y

		return x, y

	def scale(self, surf, index):
		width = self.get_list_attributes(self.widths)[index] if self.widths else surf.get_width()
		height = self.get_list_attributes(self.heights)[index] if self.heights else surf.get_height()

		scaled_surf = pygame.transform.scale(surf, (width, height))

		return scaled_surf

	def convert_pos(self, pos):
		x, y = self.rect.topleft

		converted_pos = pos[0]-x, pos[1]-y

		return converted_pos

	def check_hovering(self):
		pos = pygame.mouse.get_pos()

		if self.rect.collidepoint(pos) or self.selected:
			pos = self.convert_pos(pygame.mouse.get_pos())

			if self.selected:
				self.hovering = True
			elif self.mask.get_at(pos):
				self.hovering = True
			else:
				self.hovering = False

		else:
			self.hovering = False

	def check_pressed(self):
		if self.hovering:
			self.pressing = pygame.mouse.get_pressed()[0] or self.joykey_pressed
		else:
			if not pygame.mouse.get_pressed()[0]:
				self.pressing = False

	def call_command(self):
		if not self.pressing and self.was_pressing:
			self.command()

	def update_sprite(self):
		if self.pressing:
			self.image = self.press_surface
			self.rect = self.press_rect
			self.mask = self.press_mask

			self.font_surface = self.press_font
			self.font_rect = self.press_font_rect

		elif self.hovering:
			self.image = self.hover_surface
			self.rect = self.hover_rect
			self.mask = self.hover_mask

			self.font_surface = self.hover_font
			self.font_rect = self.hover_font_rect

		else:
			self.image = self.main_surface
			self.rect = self.main_rect
			self.mask = self.main_mask

			self.font_surface = self.main_font
			self.font_rect = self.main_font_rect

	def update(self, dt):
		self.was_pressing = self.pressing

		self.check_hovering()
		self.check_pressed()

		self.call_command()

		self.increase_alpha(dt)
		self.update_sprite()


class ColorFilter:
	def __init__(self, color, alpha, size, pos):
		self.image = pygame.Surface(size)
		self.image.fill(color)
		self.image.set_alpha(alpha)
		self.rect = self.image.get_rect(**pos)

	def apply(self, display_surface):
		display_surface.blit(self.image, self.rect)
