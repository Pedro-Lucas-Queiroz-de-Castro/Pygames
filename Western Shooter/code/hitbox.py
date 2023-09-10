import pygame

class StaticHitbox(pygame.Rect):
	def __init__(self, pos, width, height):
		super().__init__(pos[0], pos[1], width, height)

# class DynamicHitbox(pygame.Rect):
# 	def __init__(self):
# 		super().__init__()