import pygame

# Inicializar o Pygame e o mixer de áudio
pygame.init()
pygame.mixer.init()

# Carregar as músicas
musica1 = '../audio/Explorer.ogg'
musica2 = '../audio/MuffledExplorer.ogg'
music_length = 54 # seconds

on_water = False

# Função para pausar a música atual e iniciar a próxima música
def pausar_e_iniciar_proxima():
	global on_water, start_time

	on_water = not on_water
	pygame.mixer.music.pause()  # Pausar a música atual
	musica = musica2 if on_water else musica1
	pygame.mixer.music.load(musica)  # Carregar a próxima música

	current_seconds = ((pygame.time.get_ticks()-start_time)/1000) % music_length
	print(current_seconds)
	pygame.mixer.music.play(start=current_seconds, loops=-1)  # Iniciar a próxima música

# Carregar a primeira música
pygame.mixer.music.load(musica1)

# Reproduzir a primeira música
pygame.mixer.music.play()
start_time = pygame.time.get_ticks()

screen = pygame.display.set_mode((300,300))

# Loop principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                pausar_e_iniciar_proxima()

    pygame.display.update()
