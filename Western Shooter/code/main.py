import pygame, sys
from settings import * 
from player import Player
from pytmx.util_pygame import load_pygame
from sprite import Sprite
from hitbox import StaticHitbox
from bullet import Bullet
from entity import Entity
from support import import_assets
from monsters import Coffin, Cactus, Cat

class AllSprites(pygame.sprite.Group):
	def __init__(self):
		super().__init__()

		self.background = pygame.image.load('../graphics/other/bg.png').convert()
		self.offset = pygame.math.Vector2()

	def custom_draw(self, display_surface, player):
		# update offset
		self.offset.x = player.rect.centerx - display_surface.get_width() / 2
		self.offset.y = player.rect.centery - display_surface.get_height() / 2

		# background
		display_surface.blit(self.background, -self.offset)

		# sprites
		for sprite in sorted(self.sprites(), key=lambda sprite: sprite.overlap_pos):
			offset_rect = sprite.rect.copy()
			offset_rect.center -= self.offset
			display_surface.blit(sprite.image, offset_rect)

			# for DEBUG
			# offset_hitbox = sprite.hitbox.copy()
			# offset_hitbox.center -= self.offset

			# if sprite == player:
			#   pygame.draw.rect(display_surface, 'blue', offset_rect)
			# 	pygame.draw.rect(display_surface, 'red', offset_hitbox)
			# else:
			# 	pygame.draw.rect(display_surface, 'green', offset_hitbox)

			# monster face player DEBUG
			# if hasattr(sprite, 'name') and sprite.name.lower() in ('cactus', 'coffin'):
			# 	pygame.draw.line(display_surface, 'red', sprite.rect.center-self.offset,
			# 		player.rect.center-self.offset)


class Game:
	def __init__(self):
		pygame.init()
		self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		pygame.display.set_caption('Western shooter')
		self.clock = pygame.time.Clock()

		# groups
		self.all_sprites = AllSprites()
		self.collision_objects = []
		self.bullet_sprites = pygame.sprite.Group()
		self.entity_sprites = pygame.sprite.Group()

		self.bullet_image =\
		 pygame.image.load('../graphics/other/particle.png').convert_alpha()

		self.bullet_sound = pygame.mixer.Sound('../sound/bullet.wav')
		self.bullet_sound.set_volume(0.3)
		self.music = pygame.mixer.Sound('../sound/music.mp3')

		self.import_entities_assets()
		self.setup()

	def create_bullet(self, pos, direction, shooter, speed):
		Bullet(pos, direction, self.bullet_image, [self.all_sprites,self.bullet_sprites],
			self.collision_objects, shooter, speed)
		self.bullet_sound.play()

	def bullet_collision(self):
		# if pygame.sprite.spritecollide(self.player, self.bullet_sprites, True):
		# 	self.player.get_damage(10)	

		for bullet in self.bullet_sprites.sprites():
			# entities
			for entity in self.entity_sprites.sprites():
				if pygame.sprite.collide_mask(bullet, entity):
					if bullet.shooter != entity:
						entity.get_damage(bullet.shooter.attack_power)
						bullet.kill()
			# obstacles
			for hitbox in self.collision_objects:
				if bullet.rect.colliderect(hitbox):
					bullet.kill()

	def import_entities_assets(self):
		self.entity_animations = {}
		for entity in PATHS.keys():
			self.entity_animations[entity] = import_assets(PATHS[entity])

	def setup(self):
		# tmx map
		tmx_map = load_pygame('../data/map.tmx')
		tile_width, tile_height = tmx_map.tilewidth, tmx_map.tileheight

		# fences
		for x, y, surface in tmx_map.get_layer_by_name('Fence').tiles():
			Sprite('Fence', surface, (x*tile_width, y*tile_height), [self.all_sprites])

		# objects
		for obj in tmx_map.get_layer_by_name('Object'):
			Sprite(obj.name, obj.image, (obj.x, obj.y), [self.all_sprites])

		# entities
		for obj in tmx_map.get_layer_by_name('Entities'):
			name = obj.name.lower()
			if name == 'player':
				self.player = Player(name, (obj.x,obj.y), [self.all_sprites, self.entity_sprites],
					self.entity_animations[name], self.collision_objects,
					self.create_bullet)
			elif name == 'cat':
				Cat(name, (obj.x,obj.y), [self.all_sprites, self.entity_sprites],
					self.entity_animations[name], self.collision_objects,
					self.player, self.entity_sprites)
			elif name == 'coffin':
				Coffin(name, (obj.x,obj.y), [self.all_sprites, self.entity_sprites],
					self.entity_animations[name], self.collision_objects,
					self.player, self.entity_sprites)
			elif name == 'cactus':
				Cactus(name, (obj.x,obj.y), [self.all_sprites, self.entity_sprites],
					self.entity_animations[name], self.collision_objects, self.create_bullet, 
					self.player)

		# hitboxes
		self.set_hitboxes(tmx_map)
	
	def set_hitboxes(self, tmx_map):
		references = tmx_map.get_layer_by_name('References')
		reference_dict = {ref.name: ref for ref in references}

		hitboxes = tmx_map.get_layer_by_name('Hitboxes')
		hitbox_dict = {name: [] for name in reference_dict}
		standard_hitboxes = []

		for name in hitbox_dict:
			for hitbox in hitboxes:
				if hitbox.name == name:
					hitbox_dict[name].append(hitbox)
				else:
					standard_hitboxes.append(hitbox)
		
		for name in reference_dict.keys():
			hitboxes = hitbox_dict[name]
			reference = reference_dict[name]

			for hitbox in hitboxes:
				Xdistance = hitbox.x - reference.x
				Ydistance = hitbox.y - reference.y

				for sprite in self.all_sprites:
					try:
						sprite_name = sprite.name
					except AttributeError:
						continue

					if sprite_name and\
					sprite_name == name:

						x = sprite.pos[0] + Xdistance
						y = sprite.pos[1] + Ydistance

						self.collision_objects.append(
							StaticHitbox((x, y), hitbox.width, hitbox.height))

		for hitbox in standard_hitboxes:
			self.collision_objects.append(
				StaticHitbox((hitbox.x, hitbox.y), hitbox.width, hitbox.height))

	def update(self, dt):
		self.all_sprites.update(dt)
		self.bullet_collision()

	def draw(self):
		self.display_surface.fill('black')
		self.all_sprites.custom_draw(self.display_surface, self.player)

	def run(self):
		self.music.play(loops=-1)
		while True:
			dt = self.clock.tick() / 1000

			# event loop 
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()

			self.update(dt)
			self.draw()

			pygame.display.update()

if __name__ == '__main__':
	game = Game()
	game.run()
