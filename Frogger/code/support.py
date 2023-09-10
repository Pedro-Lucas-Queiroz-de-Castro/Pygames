import pygame
from os import walk


def import_assets(path):
	data = list(walk(path))
	folders = data[0][1]

	if folders:
		surfaces =\
		{folder_name: 

		 [pygame.image.load(path+'/'+folder_name+'/'+image_name).convert_alpha()
		 for image_name in folder_data[2]]

		 for folder_name, folder_data in zip(folders, data[1:])}
	else:
		surfaces = [pygame.image.load(path+'/'+image_name).convert_alpha() for image_name in data[0][2]]

	return surfaces
