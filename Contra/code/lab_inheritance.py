class Entity:
	def __init__(self, name, **kwargs):
		super().__init__(**kwargs)
		self.name = name

	def move(self, speed):
		print('The monster has moved')
		print(f'It has a speed of {speed}')


class Monster:
	def __init__(self, health, energy, **kwargs):
		super().__init__(**kwargs)
		self.health = health
		self.energy = energy

	def attack(self, amount):
		print('The monster has attacked!')
		print(f'{amount} damage was dealt')
		self.energy -= 20


class Fish:
	def __init__(self, speed, has_scales, **kwargs):
		super().__init__(**kwargs)
		self.speed = speed
		self.has_scales = has_scales

	def swim(self):
		print(f'The fish is swimming at a speed of {self.speed}')


class Shark(Fish, Entity, Monster):
	def __init__(self, name, bite_strength, health, energy, speed, has_scales):
		self.bite_strength = bite_strength
		super().__init__(name=name, health=health, energy=energy, speed=speed,
			has_scales=has_scales)


entity = Entity('Vasco')
entity.move(67)

print('+'*50)

monster = Monster(10, 20)
monster.attack(10)

print('+'*50)

fish = Fish(30, 45)
fish.swim()

print('+'*50)

shark = Shark('Peppa', 10, 20, 30, 40, True)
shark.swim()