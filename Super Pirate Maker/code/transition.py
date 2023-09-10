import pygame
from settings import *
from pygame.math import Vector2 as vector


class Transition:
	def __init__(self, toggle):
		self.display_surface = pygame.display.get_surface()
		self.toggle = toggle
		self.active = False

		self.color = 'black'
		self.border_width = 0
		self.speed = 1000
		self.direction = 1

		self.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
		self.radius = vector(self.center).magnitude()
		self.threshold = self.radius + 100

	def animate(self, dt):
		self.state_update()

		self.border_width += self.speed * dt * self.direction
		pygame.draw.circle(self.display_surface, self.color, self.center, self.radius, int(self.border_width))

	def state_update(self):
		if self.border_width >= self.threshold:
			self.direction = -1
			self.toggle()
		elif self.border_width < 0:
			self.reset()

	def reset(self):
		self.active = False
		self.border_width = 0
		self.direction = 1

	def display(self, dt):
		if self.active:
			self.animate(dt)