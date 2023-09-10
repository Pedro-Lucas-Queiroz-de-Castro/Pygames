import pygame
from settings import *
from random import choice, randint
from sys import exit
from player import Player
from car import Car
from objects import SimpleObject, LongObject


class AllSprites(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.offset = pygame.math.Vector2()
		self.background = pygame.image.load('../graphics/main/map.png').convert()
		self.foreground = pygame.image.load('../graphics/main/overlay.png').convert_alpha()

	def custom_draw(self, display_surface, player):
		# update offset
		self.offset.x = (player.rect.centerx - WINDOW_WIDTH/2)
		self.offset.y = (player.rect.centery - WINDOW_HEIGHT/2)

		# background
		display_surface.blit(self.background, -self.offset)

		# sprites
		for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
			display_surface.blit(sprite.image, sprite.rect.bottomright-self.offset)

		# foreground
		display_surface.blit(self.foreground, -self.offset)


def try_generate_car():
	random_pos = choice(CAR_START_POSITIONS) #choice(car_start_positions)
	# car_start_positions.remove(random_pos)

	if random_pos not in car_selected_positions:
		car_selected_positions.append(random_pos)
		pos = (random_pos[0], random_pos[1] + randint(-8, 8))
		Car([all_sprites, obstacle_sprites], pos)

	if len(car_selected_positions) > 5:
		# car_start_positions.append(car_selected_positions[0])
		del car_selected_positions[0]


# SETUP
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Frogger')
clock = pygame.time.Clock()


# GROUPS
all_sprites = AllSprites()
obstacle_sprites = pygame.sprite.Group()

# SPRITES
player = Player([all_sprites], obstacle_sprites, (2062, 3274))

# TIMER
car_timer = pygame.event.custom_type()
pygame.time.set_timer(car_timer, CAR_GENERATION_TIME)
car_start_positions = CAR_START_POSITIONS
car_selected_positions = []

# LEVEL OBJECTS
for image_name in SIMPLE_OBJECTS:
	surface = pygame.image.load(f'../graphics/objects/simple/{image_name}.png').convert_alpha()
	for pos in SIMPLE_OBJECTS[image_name]:
		SimpleObject([all_sprites, obstacle_sprites], surface, pos)

for image_name in LONG_OBJECTS:
	surface = pygame.image.load(f'../graphics/objects/long/{image_name}.png').convert_alpha()
	for pos in LONG_OBJECTS[image_name]:
		LongObject([all_sprites, obstacle_sprites], surface, pos)

# GAME STATE
game_over = False
font = pygame.font.Font('../fonts/The Wild Breath of Zelda.otf', 90)
color_channel_hex = '00'

# MUSICS
main_music = pygame.mixer.Sound('../audio/Attack of the Killer Queen.mp3')
victory_music = pygame.mixer.Sound('../audio/Ayrton Senna.mp3')
lose_musics = [pygame.mixer.Sound('../audio/Faint Courage.mp3') for i in range(3)]
lose_musics.append(pygame.mixer.Sound('../audio/Vasco.mp3'))
lose_musics[-1].set_volume(0.2)


# MAINLOOP
main_music.play(loops=-1)
while True:
	dt = clock.tick(60) / 1000

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			exit()
		if event.type == car_timer:
			try_generate_car()

	if player.rect.top < 1180 and not game_over:
		play_victory_music = True
		game_over = True


	if player.car_collide:
		main_music.stop()
		if not pygame.mixer.get_busy():
			choice(lose_musics).play(loops=-1)

		color_channel_decimal = int(color_channel_hex, 16)
		color_channel_hex = format(color_channel_decimal+1 if color_channel_decimal < 255\
		 else color_channel_decimal, '02x')

		end_message = font.render('FOI DE VASCO', False, f'#{color_channel_hex}0000')

		screen.fill('black')
		screen.blit(end_message, (screen.get_width()/2-end_message.get_width()/2,
			screen.get_height()/2-end_message.get_height()/2))

	elif game_over:
		main_music.stop()
		if not pygame.mixer.get_busy():
			victory_music.play(loops=-1)

		color_channel_decimal = int(color_channel_hex, 16)
		color_channel_hex = format(color_channel_decimal+1 if color_channel_decimal < 255\
		 else color_channel_decimal, '02x')

		end_message = font.render('VICTORY', False, f'#00{color_channel_hex}00')

		screen.fill('black')
		screen.blit(end_message, (screen.get_width()/2-end_message.get_width()/2,
			screen.get_height()/2-end_message.get_height()/2))

	else:
	# UPDATE
		all_sprites.update(dt)

	# DRAW
		screen.fill('black')
		all_sprites.custom_draw(screen, player)

	pygame.display.update()
