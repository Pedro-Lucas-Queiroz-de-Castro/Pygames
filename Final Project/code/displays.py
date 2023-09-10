import pygame


class FadeSurface:
	def __init__(self, display_surface, surfaces, pos, fade_speed,
		start_alpha=255, end_alpha=0, bg_color='black'):
		self.display_surface = display_surface

		self.surfaces = surfaces
		self.pos = pos
		self.rect = self.surfaces[0].get_rect(**self.pos)
		self.bg_surf = pygame.Surface((self.rect.width,self.rect.height))
		self.bg_surf.fill(bg_color)

		self.alpha = start_alpha

		self.fade_speed = fade_speed
		self.start_alpha = start_alpha
		self.end_alpha = end_alpha

		self.direction = 1 if start_alpha <= self.end_alpha else -1

		self.ended = False

	def reset(self):
		self.alpha = self.start_alpha
		self.ended = False

	def update(self, dt):
		self.alpha += self.fade_speed * dt * self.direction
		if self.direction == 1:
			self.alpha = min(self.alpha, self.end_alpha)
			if self.alpha >= self.end_alpha:
				self.ended = True
		elif self.direction == -1:
			self.alpha = max(self.alpha, self.end_alpha)
			if self.alpha <= self.end_alpha:
				self.ended = True

		for surface in self.surfaces:
			surface.set_alpha(self.alpha)

		self.bg_surf.set_alpha(self.alpha)

	def display(self, index, bg=True):
		if bg:
			self.display_surface.blit(self.bg_surf, self.rect)
		self.display_surface.blit(self.surfaces[index], self.rect)