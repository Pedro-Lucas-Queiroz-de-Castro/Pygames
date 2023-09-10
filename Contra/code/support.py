import pygame
from os import walk

def import_assets(path):
	animations = {}
	full_data = list(walk(path))[1:]

	for path, _, files in full_data:
		path = path.replace('\\', '/')
		folder = path.split('/')[-1]

		animations[folder] = [pygame.image.load(path+'/'+file).convert_alpha() 
		for file in files]

	return animations


def import_audio(path):
	sounds = {}
	files = list(walk(path))[0][2]

	for file in files:
		sounds[file.split('.')[0]] = pygame.mixer.Sound(path+'/'+file) 

	return sounds
