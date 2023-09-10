import pygame
import json

from os import walk
from math import sin



def scale_graphics_with_direction_and_state(animations, scale_offset, default_sizes={}):
	if default_sizes == None:
		default_sizes = {}

	for direction, states in animations.items():
		for state, frames in states.items():

			if 'all' in default_sizes.keys():
				animations[direction][state] =\
				scale_list_of_surfaces(frames,
				 	default_sizes['all'][0]*scale_offset,
				 	default_sizes['all'][1]*scale_offset)

			elif default_sizes:
				if default_sizes[state]:
					animations[direction][state] =\
					scale_list_of_surfaces(frames,
					 	default_sizes[state][0]*scale_offset,
					 	default_sizes[state][1]*scale_offset)
				else:
					w = frames[0].get_width()
					h = frames[0].get_height()
					animations[direction][state] =\
					scale_list_of_surfaces(frames,w*scale_offset,h*scale_offset)

			else:
				w = frames[0].get_width()
				h = frames[0].get_height()
				animations[direction][state] =\
				scale_list_of_surfaces(frames,w*scale_offset,h*scale_offset)


def get_direction_state_animations_copy(animations):
		animations_copy = {}
		surfaces = []

		for k1, sides in animations.items():
			animations_copy[k1] = {}
			for k2, frames in sides.items():
				animations_copy[k1][k2] = [surface.copy() for surface in frames]				

		return animations_copy


def sin_wave(x):
	return sin(x)


def write_json_file(folderpath, filename, data={}):
    # Caminho completo para o arquivo
    filename += '.json'
    filepath = folderpath+'/'+filename

    # Abre o arquivo em modo de escrita
    with open(filepath, 'w') as json_file:
        # Escreve os dados no arquivo JSON
        json.dump(data, json_file)
        json_file.write('\n')


def append_json_file(folderpath, filename, data={}):
	filepath = folderpath+'/'+filename+'.json'

	existent_data = read_json_file(filepath)
	new_data = existent_data.copy()
	for key, value in data.items():
		new_data[key] = value

	write_json_file(folderpath, filename, new_data)


def read_json_file(filepath):
    try:
        # Abre o arquivo em modo de leitura
        with open(filepath, 'r') as json_file:
            # Carrega os dados do arquivo JSON em uma lista de dicionários
            dados = json.load(json_file)
            return dados

    except FileNotFoundError:
    	print(f'File not found.')
    	return {}

    except Exception as e:
        print(f"Error when reading file '{filepath}': {str(e)}")
        return {}


def get_filenames(path):
	return list(walk(path))[0][2]


def get_foldernames(path):
	return list(walk(path))[0][1]


def relative_scaled_surface(surface, x, y):
	surface = pygame.transform.scale(
		surface,
		(surface.get_width()*x,
		surface.get_height()*y))

	return surface


def relative_scaled_surfaces(surfaces, x, y):
	scaled_surfaces = []

	for surf in surfaces:
		surf = pygame.transform.scale(
			surf,
			(surf.get_width()*x,
			surf.get_height()*y))

		scaled_surfaces.append(surf)

	return scaled_surfaces


def get_joystick_components(joystick):
	components_name = {
	'buttons':
	['triangle','circle','cross','square','L1','R1','L2','R2','select','start','home','lstick','rstick',
	'.', '..', '...'],
	'axes':
	['hlaxis', 'vlaxis', 'hraxis', 'vraxis', '.', '..', '...'],
	'hats':
	['lhat', 'rhat']
	}

	booleans = {}

	for b in range(joystick.get_numbuttons()):
		booleans[components_name['buttons'][b]] = joystick.get_button(b)

	for a in range(joystick.get_numaxes()):
		booleans[components_name['axes'][a]] = joystick.get_axis(a)

	for h in range(joystick.get_numhats()):
		booleans[components_name['hats'][h]] = joystick.get_hat(h)

	return booleans


def line_pick(list_):
	list_ = list_.copy()
	pick = list_[0]
	list_.pop(0)
	list_.append(pick)

	return pick, list_


def numloop(num, increment, minimum, maximum):
	num += increment

	if num > maximum:
		num = minimum
	elif num < minimum:
		num = maximum

	return num


def tend_to(number, number_to_tend, increment):
	if number < number_to_tend:
		number = min(number_to_tend, number+increment)
	elif number > number_to_tend:
		number = max(number_to_tend, number-increment)

	return number


def key_from_value(dicti, value):
	for k, v in dicti.items():
		if v == value:
			return k


def get_surfaces_from_folder(path):
	surfaces = []

	for file in get_filenames(path):
		surfaces.append(pygame.image.load(path+'/'+file).convert_alpha())

	return surfaces


def get_animations_from_folder_with_subfolders(path, flip=None,
	flipkeys={'n':'normal', 'h':'h flipped', 'v':'v flipped', 'b':'both flipped'}):

	animations = {}

	for folder in get_foldernames(path):
		animations[folder] = {k: {} for k in flipkeys.values()} if flip else {}

		for subfolder in get_foldernames('/'.join([path,folder])):
			if flip:

				for fliptype, key in flipkeys.items():
					surfaces = get_surfaces_from_folder('/'.join([path,folder,subfolder]))

					match fliptype:
						case 'n':
							pass
						case 'h':
							surfaces = flip_list_of_surfaces(surfaces,True,False)
						case 'v':
							surfaces = flip_list_of_surfaces(surfaces,False,True)
						case 'b':
							surfaces = flip_list_of_surfaces(surfaces,True,True)
					
					animations[folder][key][subfolder] = surfaces
								
			else:
				animations[folder][subfolder] = get_surfaces_from_folder('/'.join([path,folder,subfolder]))


	return animations


def flip_list_of_surfaces(list_, flipx, flipy):
	new_list = []

	for surface in list_:
		new_list.append(pygame.transform.flip(surface,flipx,flipy))

	return new_list


def scale_list_of_surfaces(list_, x, y):
	new_list = []

	for surface in list_:
		new_list.append(pygame.transform.scale(surface,(x,y)))

	return new_list


def alphafill(surface, color):
	surface = surface.copy()
	new_surface = pygame.mask.from_surface(surface).to_surface()
	new_surface.set_colorkey('black')
	new_surface.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
	return new_surface


def get_animations_from_folder_with_subfolders_spritesheet_edition(path, width, height, flip=None,
	flipkeys={'n':'normal', 'h':'h flipped', 'v':'v flipped', 'b':'both flipped'}):

	animations = {}

	for folder in get_foldernames(path):
		animations[folder] = {k: {} for k in flipkeys.values()} if flip else {}

		for subfolder in get_foldernames('/'.join([path,folder])):
			if flip:

				for fliptype, key in flipkeys.items():
					surfaces = get_surfaces_from_spritesheets(
						get_surfaces_from_folder('/'.join([path,folder,subfolder])),
						width, height)

					match fliptype:
						case 'n':
							pass
						case 'h':
							surfaces = flip_list_of_surfaces(surfaces,True,False)
						case 'v':
							surfaces = flip_list_of_surfaces(surfaces,False,True)
						case 'b':
							surfaces = flip_list_of_surfaces(surfaces,True,True)

					animations[folder][key][subfolder] = surfaces

			else:
				animations[folder][subfolder] = get_surfaces_from_spritesheets(
						get_surfaces_from_folder('/'.join([path,folder,subfolder])),
						width, height)

	return animations


def get_surfaces_from_spritesheets(spritesheets, width, height):
	surfaces = []
	for spritesheet in spritesheets:

		full_width = spritesheet.get_width()
		full_height = spritesheet.get_height()

		for y in range(0,full_height,height):
			for x in range(0,full_width,width):

				rect = pygame.Rect(x,y,width,height)

				# get subsurface/frame
				if (full_width - x) / width >= 1 and (full_height - y) / height >= 1:
					frame = spritesheet.subsurface(rect)
				else:
					frame = None

				if frame:
					surfaces.append(frame)

	return surfaces


def apply_anchor(set_rect, get_rect, anchor, scale_offset):
	set_anchor = anchor[0]

	get_anchor = anchor[1][0]
	get_anchor_offset = (anchor[1][1][0]*scale_offset, anchor[1][1][1]*scale_offset)

	setattr(set_rect, set_anchor, sum_tuples(getattr(get_rect, get_anchor),get_anchor_offset))


def sum_tuples(*tuples):
	components = {}
	for tup in tuples:
		for i, comp in enumerate(tup):
			if i in components:
				components[i] += comp
			else:
				components[i] = comp

	return tuple(components.values())


def get_points_between(a, b, step=1):
	points = [a]
	ax, ay = a
	bx, by = b

	for y in range(ay, by, step):
		for x in range(ax, bx, step):
			points.append((x,y))

	points.append(b)

	return points


def sort_group(group, key):
	sprites = group.sprites()
	group.remove(sprites)
	group.add(sorted(sprites, key=key))



def convert_str_tuple_to_vector(str_tuple):
	x, y = str_tuple.replace('vector','').replace('(','').replace(')','').split(',')

	x, y = float(x), float(y)

	return pygame.math.Vector2(x,y)


