import pygame


class MusicToggle:
	def __init__(self, music1, music2, length, loops, volume):
		self.music1 = music1
		self.music2 = music2
		self.current_music = music1

		self.length = length
		self.loops = loops
		self.volume = volume

		self.active = False

	def start(self):
		self.start_time = pygame.time.get_ticks()
		pygame.mixer.music.load(self.current_music)
		pygame.mixer.music.play(loops=self.loops)
		self.active = True

	def toggle(self):
		current_seconds =\
			((pygame.time.get_ticks()-self.start_time)/1000)%self.length

		if self.current_music == self.music1:
			self.current_music = self.music2
		else:
			self.current_music = self.music1

		pygame.mixer.music.load(self.current_music)
		pygame.mixer.music.set_volume(self.volume)
		pygame.mixer.music.play(start=current_seconds, loops=self.loops)

	def stop(self):
		pygame.mixer.music.stop()