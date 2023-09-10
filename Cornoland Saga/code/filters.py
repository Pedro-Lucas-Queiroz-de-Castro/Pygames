import pygame


class AlphaFade:
	def __init__(self, display_surface, color, speed, start_alpha=0, end_alpha=255, direction=1):
		self.display_surface = display_surface

		self.start_alpha = min(255, max(0, start_alpha))
		self.end_alpha = max(0, min(end_alpha, 255))

		if direction < 0:
			self.start_alpha, self.end_alpha = self.end_alpha, self.start_alpha

		self.alpha = self.start_alpha
		self.speed = speed # alpha increment per second if dt else per frame
		self.direction = direction

	def apply(self, dt=1):
		if self.direction < 0:
			self.alpha = max(self.end_alpha, self.alpha + self.speed * dt * self.direction)
		else:
			self.alpha = min(self.end_alpha, self.alpha + self.speed * dt * self.direction)

		self.surface.set_alpha(self.alpha)

		self.display_surface.blit(self.surface, self.rect)


class AlphaFadeFilter(AlphaFade):
	def __init__(self, display_surface, color, rect, speed, start_alpha=0, end_alpha=255, direction=1):
		super().__init__(display_surface, color, speed, start_alpha, end_alpha, direction)

		self.surface = pygame.Surface((rect.width, rect.height))
		self.surface.fill(color)
		self.surface.set_alpha(start_alpha)

		self.rect = rect