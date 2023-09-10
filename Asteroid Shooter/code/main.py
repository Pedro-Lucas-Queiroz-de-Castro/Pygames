import pygame
from sys import exit
from random import randint, uniform, choice


def create_laser():
		laser_list.append(laser_surf.get_rect(center = (
					ship_rect.centerx,
					ship_rect.centery-10)))


def update_laser():
	for laser_rect in laser_list:
		laser_rect.y -= laser_speed

		if laser_rect.y < -1 * laser_surf.get_size()[0]:
			destroy_laser(laser_rect)


def destroy_laser(laser_rect):
	laser_list.remove(laser_rect)


def create_asteroid():
	surface = pygame.transform.rotozoom(asteroid_surf, randint(0, 360), uniform(0.5, 2))
	rectangle = surface.get_rect(midbottom = (randint(WIDTH//5, WIDTH-(WIDTH//5)), 0))\
	.inflate(-surface.get_size()[0]//4, -surface.get_size()[1]//4)

	speed = randint(asteroid_speeds[0], asteroid_speeds[1])
	vector = pygame.math.Vector2(round(choice([-1,-1,-1,0,1,1,1])*-100/((rectangle.centerx-WIDTH//2)+1)),
		randint(-2, -1)).normalize()

	asteroid_list.append((surface, rectangle, speed, vector))


def update_asteroid():
	global score

	for asteroid in asteroid_list:
		ast_surf, ast_rect, ast_speed, ast_vector = asteroid
		ast_rect.center -= ast_vector * ast_speed

		if ast_rect.top > HEIGHT:
			destroy_asteroid(asteroid)
			score -= 1


def destroy_asteroid(asteroid):
	try:
		asteroid_list.remove(asteroid)
	except:
		pass


def check_collisions():
	global score

	for asteroid in asteroid_list:
		if ship_rect.colliderect(asteroid[1]):
			play_sound(explosion_sound)
			music.stop()
			return True

		for laser_rect in laser_list:
			if laser_rect.colliderect(asteroid[1]):
				play_sound(explosion_sound)
				destroy_laser(laser_rect)
				destroy_asteroid(asteroid)

				score += 1


def check_screen_boundaries():
	if ship_rect.right > WIDTH:
		ship_rect.right = WIDTH
	elif ship_rect.left < 0:
		ship_rect.left = 0
	if ship_rect.top < 0:
		ship_rect.top = 0
	elif ship_rect.bottom > HEIGHT:
		ship_rect.bottom = HEIGHT


def check_win(score, win_score):
	return score >= win_score


def play_sound(sound):
	sound.play()


# Initial Setup
WIDTH, HEIGHT = 960, 540
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Asteroid Shooter')
clock = pygame.time.Clock()

# OBJECTS
# Background
background_surf = pygame.image.load('../images/background.png').convert()

# Font
font = pygame.font.Font('../images/subatomic.ttf', 90)
font2 = pygame.font.Font('../images/subatomic.ttf', 50)
game_over_surf = font.render("GAME OVER", True, 'white')
game_over_rect = game_over_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
win_surf = font.render("YOU WIN", True, 'white')
win_rect = win_surf.get_rect(center=(WIDTH//2, HEIGHT//2))

score = 0

# Sounds
music = pygame.mixer.Sound('../sounds/music.wav'); music.play(loops=-1)
explosion_sound = pygame.mixer.Sound('../sounds/explosion.wav')
laser_sound = pygame.mixer.Sound('../sounds/laser.ogg')

# Ship
ship_surf = pygame.image.load('../images/ship.png').convert_alpha()
ship_rect = ship_surf.get_rect(center=(WIDTH//2, 8*HEIGHT//10))
ship_direction = pygame.math.Vector2(0, 0)
ship_speed = 10

# Laser
laser_surf = pygame.image.load('../images/laser.png').convert_alpha()
laser_list = []
laser_speed = 25
can_shoot = True
shot_cooldown = 100
laser_timer = 0

# Asteroids
asteroid_surf = pygame.image.load('../images/asteroid.png').convert_alpha()
asteroid_list = []
asteroid_speeds = (4, 10)
asteroid_cooldown = 300
asteroid_timer = 10
can_create_asteroid = False


win = False
win_score = 30


# Main Loop
game_over = False
while True:
	# Event Loop
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			exit()

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE and game_over:
				ship_rect.center = (WIDTH//2, 8*HEIGHT//10)
				try: music.stop() 
				except: music.play()
				else: music.play()
				score = 0

				game_over = False
				win = False

	if not game_over and not win:
		# Cooldowns
		if pygame.time.get_ticks() - laser_timer > shot_cooldown: # laser
			can_shoot = True

		if pygame.time.get_ticks() - asteroid_timer > asteroid_cooldown: # asteroid
			can_create_asteroid = True

		# Input Getter
		keys = pygame.key.get_pressed()

		# movement
		if keys[pygame.K_UP] and keys[pygame.K_DOWN]:
			ship_direction.y = 0
		elif keys[pygame.K_UP]:
			ship_direction.y = -1
		elif keys[pygame.K_DOWN]:
			ship_direction.y = 1
		else:
			ship_direction.y = 0

		if keys[pygame.K_RIGHT] and keys[pygame.K_LEFT]:
			ship_direction.x = 0
		elif keys[pygame.K_RIGHT]:
			ship_direction.x = 1
		elif keys[pygame.K_LEFT]:
			ship_direction.x = -1
		else:
			ship_direction.x = 0

		if ship_direction.magnitude() > 0:
			ship_direction.normalize_ip()
		ship_rect.center += ship_direction * ship_speed

		# laser
		if keys[pygame.K_z] and can_shoot:
			play_sound(laser_sound)
			laser_timer = pygame.time.get_ticks()
			can_shoot = False

			create_laser()

		# asteroid
		if can_create_asteroid:
			create_asteroid()
			asteroid_timer = pygame.time.get_ticks()
			can_create_asteroid = False

		# Updates
		update_laser()
		update_asteroid()
		check_screen_boundaries()
		game_over = check_collisions()
		win = check_win(score, win_score)

		# Display
		screen.blit(background_surf, (0, 0))  # background

		for laser_rect in laser_list:       # laser
			screen.blit(laser_surf, laser_rect)

		screen.blit(ship_surf, ship_rect)    # ship

		for asteroid in asteroid_list:      # asteroid
			screen.blit(asteroid[0], asteroid[1])

		score_surf = font2.render(str(score), True, 'white')
		score_rect = score_surf.get_rect(center=(5*WIDTH//10, HEIGHT//10))
		screen.blit(score_surf, score_rect)

	else: # game over screen
		game_over = True

		asteroid_list.clear()
		laser_list.clear()

		screen.blit(background_surf, (0, 0))

		if win:
			screen.blit(win_surf, win_rect)
			screen.blit(score_surf, score_rect)
		else:
			screen.blit(game_over_surf, game_over_rect)
			screen.blit(score_surf, score_rect)


	pygame.display.update()
	clock.tick(60)
