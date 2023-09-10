from pygame import Vector2 as v


HAND_VECTOR_ANIMATIONS = {
'idle': [v(0,1),v(0,-1),v(0,-1),v(0,1)],
'walk': [v(-1,0),v(1,0)],
'poke': [v(1,0),v(-1,0)],
'pick': [v(1,0),v(0,1),v(0,1),v(0,1),v(0,1),v(0,1),v(0,1),v(-1,0),v(-1,0),v(-1,0),v(0,-1)],
'smash': [v(0,-1),v(0,-1),v(0,1),v(0,1),v(0,1)],
'rumble': [v(0,-1),v(-1,0),v(1,1)],
'rumble2': [v(-1,0),v(0,-1),v(1,1)],
'hold': [v(-1,0),v(0,0)]
}

# BECAUSE DELTATIME
# continuity | V

# velocidade = frame/segundo

# largura da animacao/velocidade = tempo em segundos da animacao completa

# magnitude/aspeed => pixels
# aspeed sobe | action_speed sobe & distancia desce

# manter a razao entre magnitude e velocidade significa manter a distancia percorrida.
# a velocidade de animação tem impacto inversamente proporcional no tempo da acao.

DEFAULT_HAND_VECTOR_MAGNITUDES = {'idle': 30, 'walk': 90, 'poke': 300, 'pick': 90, 'smash': 500,
'rumble': 80, 'rumble2': 120, 'hold': 50} 

DEFAULT_HAND_VECTOR_ANIMATIONS_SPEEDS = {'idle': 5.5, 'walk': 4, 'poke': 7, 'pick': 30, 'smash': 30,
'rumble': 20, 'rumble2': 25, 'hold': 4}



HAND_SCALES = {'punch': (2.5,2.5), 'pick': (1.5,1.5)}

HAND_ROTATIONS = {'pick': [0,10,20,30,40,50,60,70,80,90,100]}

HAND_ACTIONS = ['poke', 'pick', 'smash', 'rumble', 'rumble2', 'hold']
