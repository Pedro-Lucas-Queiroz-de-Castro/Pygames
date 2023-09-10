import pygame
import pickle


def serialize_surface(surface):
    """Converte um objeto Surface do Pygame em uma representação serializável."""
    return pygame.image.tostring(surface, 'RGBA')


def deserialize_surface(serialized_data):
    """Reconstrói um objeto Surface do Pygame a partir de dados serializados."""
    return pygame.image.fromstring(serialized_data, surface.get_size(), 'RGBA')


# Exemplo de uso
surface = pygame.Surface((100, 100))  # Criando um objeto Surface

# Serializando o objeto Surface
serialized_surface = serialize_surface(surface)

# # Salvando os dados serializados usando o pickle
# with open('surface.pickle', 'wb') as file:
#     pickle.dump(serialized_surface, file)

# # Carregando os dados serializados usando o pickle
# with open('surface.pickle', 'rb') as file:
#     serialized_surface = pickle.load(file)

# # Reconstruindo o objeto Surface a partir dos dados serializados
restored_surface = deserialize_surface(serialized_surface)

print(restored_surface)
