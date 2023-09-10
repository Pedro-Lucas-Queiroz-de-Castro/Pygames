import pygame

pygame.init()
pygame.display.set_mode((600,400))

def get_highest_bit(mask):
    positions = mask.outline()

    if len(positions) == 0:
        highest_bit = -1
    else:
    	highest_bit = min(positions, key=lambda pos: -pos[0])

    return highest_bit[0]

# Exemplo de uso
surface = pygame.image.load('../graphics/player/adventurer-run3-00.png').convert_alpha()
surface = pygame.transform.scale(surface, (surface.get_width()*4, surface.get_height()*4))
mask = pygame.mask.from_surface(surface)
bit_mais_alto = get_highest_bit(mask)

print("O bit mais alto é:", bit_mais_alto)
