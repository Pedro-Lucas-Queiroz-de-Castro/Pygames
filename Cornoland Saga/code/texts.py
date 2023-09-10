import pygame

from filters import AlphaFade


class AlphaFadeText(AlphaFade):
	def __init__(self, display_surface, color, speed, font, text, AA, pos, start_alpha=0, end_alpha=255, direction=1):
		super().__init__(display_surface, color, speed, start_alpha, end_alpha, direction)

		self.surface = font.render(text, AA, color)
		self.surface.set_alpha(start_alpha)

		self.rect = self.surface.get_rect(**pos)

