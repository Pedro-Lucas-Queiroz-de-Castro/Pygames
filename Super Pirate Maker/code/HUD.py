import pygame

from settings import *


class HUDGroup(pygame.sprite.Group):
	def __init__(self, player, heart_container_surf):
		super().__init__()

		self.display_surface = pygame.display.get_surface()
		self.player = player
		self.player_last_health = self.player.health
		self.heart_containers = []
		self.heart_container_surf = heart_container_surf
		self.heart_surf_width = self.heart_container_surf.get_width()

		self.create_heart_containers()

	def create_heart_containers(self):
		positions = [
		 (HEART_CONTAINERS_START_X + (self.heart_surf_width + HEART_CONTAINERS_GAP) * i, HEART_CONTAINERS_Y)
		 for i in range(self.player_last_health)]

		for pos in positions:
			self.heart_containers.append(HeartContainer(self.heart_container_surf, pos))

	def delete_heart_containers(self):
		for i in range(self.player_last_health-self.player.health):
			self.heart_containers.pop()

		self.player_last_health = self.player.health

	def update(self):
		self.delete_heart_containers()

	def custom_draw(self):
		for sprite in self.sprites():
			self.display_surface.blit(sprite.image, sprite.rect)

		for sprite in self.heart_containers:
			self.display_surface.blit(sprite.image, sprite.rect)



class HeartContainer(pygame.sprite.Sprite):
	def __init__(self, surf, pos):
		super().__init__()

		self.image = surf
		self.rect = self.image.get_rect(topleft=pos)
