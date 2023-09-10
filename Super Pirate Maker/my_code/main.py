import pygame
from support import *
from settings import *
from pygame.image import load
from editor import Editor

class Main:
	def __init__(self):
		pygame.init()
		self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		self.clock = pygame.time.Clock()

		self.imports()
		self.editor = Editor(self.land_tiles, self.water_bottom, self.animations, self.sky_handle_surface,
			self.previews, self.cloud_surfaces)

		# cursor
		surface = load('../graphics/cursors/mouse.png').convert_alpha()
		cursor = pygame.cursors.Cursor((0,0),surface)
		pygame.mouse.set_cursor(cursor)

	def imports(self):
		self.land_tiles = import_dict_folder('../graphics/terrain/land')
		self.water_bottom = load(
			'../graphics/terrain/water/water_bottom.png').convert_alpha()
		self.sky_handle_surface = load('../graphics/cursors/handle.png').convert_alpha()


		self.animations = {}
		for key, value in EDITOR_DATA.items():
			if value['graphics']:
				graphics = import_list_folder(value['graphics'])
				self.animations[key] = {
					'frame index': 0,
					'frames': graphics,
					'length': len(graphics),
					'speed': value['animation speed']}

		self.previews = {key: load(value['preview']).convert_alpha() for key, value in EDITOR_DATA.items()
		if value['preview']}

		self.cloud_surfaces = import_list_folder('../graphics/clouds')

	def run(self):
		while True:
			dt = self.clock.tick() / 1000
			
			self.editor.run(dt)

			pygame.display.update()


if __name__ == '__main__':
	main = Main()
	main.run() 