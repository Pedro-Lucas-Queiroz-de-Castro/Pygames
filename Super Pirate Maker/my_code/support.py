import pygame
from os import walk

def all_true(dictionary, keys):
	return bool(produto_lista([int(dictionary[key]) for key in keys]))

def produto_lista(lista):
    produto = 1
    for numero in lista:
        produto *= numero
    return produto

def reverse_dict(dictionary):
	return {value: key for key, value in dictionary.items()}

def num_loop(num, minimun, maximun) -> float|int:
	if not minimun < num <\
		 maximun:
			if num < minimun:
				num = maximun
			elif num > maximun:
				num = minimun

	return num

def import_list_folder(path) -> list:
	surfaces = []

	for folder_path, sub_folders, img_files in walk(path):
		for img_name in img_files:
			full_path = path + '/' + img_name
			surface = pygame.image.load(full_path).convert_alpha()
			surfaces.append(surface)

	return surfaces

def import_dict_folder(path) -> dict:
	surfaces = {}

	for folder_path, sub_folders, img_files in walk(path):
		for img_name in img_files:
			full_path = path + '/' + img_name
			surfaces[img_name.split('.')[0]] = pygame.image.load(full_path).convert_alpha()

	return surfaces

def import_dict_animations(path) -> dict:
	surfaces = {}

	for folder_path, sub_folders, img_files in list(walk(path))[1:]:
		folder_path = folder_path.replace('\\', '/')
		folder_name = folder_path.split('/')[-1]

		surfaces[folder_name] = import_list_folder(folder_path)

	return surfaces