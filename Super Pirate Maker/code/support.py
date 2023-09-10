import pygame
from pygame.image import load
from os import walk


def decimal_color_to_hex(RGB):
	red, green, blue = RGB

	red_str = hex(red).split('x')[1].zfill(2)
	green_str = hex(green).split('x')[1].zfill(2)
	blue_str = hex(blue).split('x')[1].zfill(2)

	return '#' + red_str + green_str + blue_str

def hex_color_to_decimal(hex_string):
    # Remova o caractere '#' da string
    hex_string = hex_string.strip('#')

    # Separe os componentes de cor (rr, gg, bb)
    red = hex_string[0:2]
    green = hex_string[2:4]
    blue = hex_string[4:6]

    # Converta os componentes de cor em valores decimais
    red_decimal = int(red, 16)
    green_decimal = int(green, 16)
    blue_decimal = int(blue, 16)

    return [red_decimal, green_decimal, blue_decimal]

def get_surface_sizes(surfaces):
	sizes = []

	for surf in surfaces:
		sizes.append(surf.get_size())

	return sizes


def deserialize_surfaces(surfaces, sizes, _format='RGBA'):
	deserialized_surfaces = []

	for surf, size in zip(surfaces, sizes):
		deserialized_surfaces.append(pygame.image.fromstring(surf, size, _format))

	return deserialized_surfaces


def serialize_surfaces(surfaces, _format='RGBA'):
	serialized_surfaces = []

	for surf in surfaces:
		serialized_surfaces.append(pygame.image.tostring(surf, _format))

	return serialized_surfaces


def flipped_assets(surfaces, horizontal, vertical):
	surfaces = surfaces.copy()
	flipped_surfaces = []

	for surf in surfaces:
		flipped_surf = pygame.transform.flip(surf,horizontal,vertical)
		flipped_surfaces.append(flipped_surf)

	return flipped_surfaces


def import_folder(path):
	surface_list = []

	for folder_name, sub_folders, img_files in walk(path):
		for image_name in img_files:
			full_path = path + '/' + image_name
			image_surf = pygame.image.load(full_path).convert_alpha()
			surface_list.append(image_surf)

	return surface_list


def import_folder_dict(path):
	surface_dict = {}

	for folder_name, sub_folders, img_files in walk(path):
		for image_name in img_files:
			full_path = path + '/' + image_name
			image_surf = pygame.image.load(full_path).convert_alpha()
			surface_dict[image_name.split('.')[0]] = image_surf
			
	return surface_dict


def import_folder_animation(path):
	full_data = list(walk(path))[1:]
	animations = {}

	for folder_path, sub_folders, files in full_data:
		folder_path = folder_path.replace('\\', '/')
		folder_name = folder_path.split('/')[-1]

		animations[folder_name] = [load(folder_path+'/'+file).convert_alpha() for file in files]

	return animations
