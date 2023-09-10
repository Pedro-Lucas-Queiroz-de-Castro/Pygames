import pygame

from math import sin


def is_surface_empty(surface):
    # Cria uma máscara de transparência a partir do objeto Surface
    mask = pygame.mask.from_surface(surface)

    # Verifica se a máscara está vazia (todos os pixels transparentes)
    return mask.count() == 0

def invert(iterable):
	inverted_iterable = []
	for i in range(len(iterable)):
		inverted_iterable.append(iterable[(i+1)*-1])

	return inverted_iterable

def bool_to_things(boolean, a, b):
	if boolean:
		return a
	else:
		return b

def loop(num, minimun, maximun):
	if num < minimun:
		num = maximun
	elif num > maximun:
		num = minimun

	return num

def truncade(num, dplaces):
	return float(str(num).split('.')[0] + '.' + str(num).split('.')[1][:dplaces])

def get_beneath_rect(reference_rect, all_rects, beneath_top_or_bottom='top'):
	beneath_rects = [rect for rect in all_rects
		if rect.left >= reference_rect.left\
		and rect.right <= reference_rect.right\
		and rect.top >= getattr(reference_rect, beneath_top_or_bottom)]

	if len(beneath_rects) == 0:
		return None
	else:
		return min(beneath_rects, key=lambda rect: rect.top)

def get_basic_extreme_bits(mask):
    # positions = mask.outline()

    # if not len(positions) == 0:
    #     left = min(positions, key=lambda pos: pos[0])[0]
    #     right = max(positions, key=lambda pos: pos[0])[0]
    #     top = min(positions, key=lambda pos: pos[1])[1]
    #     bottom = max(positions, key=lambda pos: pos[1])[1]

    boundarie_rects = sorted(mask.get_bounding_rects(), key=lambda rect: rect.width*rect.height)

    if boundarie_rects:
	    bigger_rect = boundarie_rects[-1]

	    left = bigger_rect.left
	    top = bigger_rect.top
	    right = bigger_rect.right
	    bottom = bigger_rect.bottom

	    result = left, top, right, bottom

    else:
    	result = None
    
    return result
    	
def tend_to_n(x, n, speed):
	if x > n:
		y = max(n, x - speed)
	elif x < n:
		y = min(n, x + speed)
	else:
		y = n

	return y

def vector_sum(vectors):
	amount = pygame.math.Vector2(0,0)
	
	for v in vectors:
		amount += v

	return amount
