import pygame


class Display:
    def __init__(self, font_path, font_size, pos, digits, obj=None, key=None):
        self.window = pygame.display.get_surface()

        self.obj = obj
        self.key = key
        self.var = self.obj.get_display_info(self.key) if self.obj else ''

        self.font = pygame.font.Font(font_path, font_size)
        self.surface = self.font.render('0'*digits, True, 'white')
        self.rect = self.surface.get_rect(**pos).inflate(10,10)

    def update(self):
        self.var = self.obj.get_display_info(self.key) if self.obj else ''
        self.surface = self.font.render(str(self.var), True, 'white')

    def display(self):
        pygame.draw.rect(self.window, 'black', self.rect)
        offset_rect = self.rect.copy()
        offset_rect.x += 10
        offset_rect.y += 10
        self.window.blit(self.surface, offset_rect)

    def run(self):
        self.update()
        self.display()


class FPSDisplay(Display):
    def __init__(self, font_path, font_size, pos, digits, update_interval):
        super().__init__(font_path, font_size, pos, digits)

        self.fps = 999
        self.frame_count = 0
        self.fps_sum = 0

        self.counter = 0
        self.update_interval = update_interval # seconds

    def update(self, dt):
        self.counter += dt
        self.frame_count += 1
        self.fps_sum += 1 / dt if dt != 0 else 0

        if self.counter >= self.update_interval:
            self.fps = self.fps_sum / self.frame_count
            self.surface = self.font.render(f'fps: {int(self.fps)}', True, 'white')

            self.counter = 0
            self.frame_count = 0
            self.fps_sum = 0

    def run(self, dt):
        self.update(dt)
        self.display()
