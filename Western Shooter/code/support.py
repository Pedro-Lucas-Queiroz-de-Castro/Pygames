import pygame
from os import walk

def import_assets(path):
	for index, data in enumerate(walk(path)):
		if index == 0:
			folders = data[1]
			animations = {state: [] for state in folders}
		else:
			key = folders[index-1]
			file_names = sorted(data[2],
				key=lambda file_name: int(file_name.split('.')[0]))

			animations[key] = [
				pygame.image.load(path + '/' + key + '/'+ file_name).convert_alpha()\
					for file_name in file_names]

	return animations