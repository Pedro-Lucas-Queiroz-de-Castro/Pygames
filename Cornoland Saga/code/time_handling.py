import pygame


class Cooldown:
	def __init__(self, milliseconds):
		self.on = False
		self.milliseconds = milliseconds

	def start(self):
		self.on = True
		self.start_time = pygame.time.get_ticks()

	def end(self):
		self.on = False

	def update(self):
		if self.on:
			self.on = pygame.time.get_ticks() - self.start_time < self.milliseconds


class TimeWave:
	def __init__(self, milliseconds):
		self.milliseconds = milliseconds
		self.ticks = 0

		self.start_time = pygame.time.get_ticks()

		self.boolean = True

	def run(self):
		self.last_ticks = self.ticks

		self.ticks = (pygame.time.get_ticks() - self.start_time) // self.milliseconds

		if self.last_ticks != self.ticks:
			self.boolean = not self.boolean