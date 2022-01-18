from random import choice
from models import *
from validation import *
import csv
import os


print("Welcome to Ratventure!")
print("----------------------")

# Function to allow player to move hero in the map
def move(game_map, hero):
	print(game_map)
	# Keep prompting user until move is valid
	valid = False
	while not valid:
		try:
			print("W = up; A = left; S = down; D = right")
			user_input = validate_move("Your move: ")

			valid = game_map.is_valid_move(user_input)
			if not valid:
				raise ValueError("You cannot move out of the map, please enter another move.\n")
		except ValueError as e:
			print(e)
	print(game_map)

	# Checks whether hero has found the Orb of Power
	if game_map.hero_position == game_map.orb:
		hero.get_orb()

	game_map.new_day()

# Find the general direction of orb from hero
def find_direction(hero_coord, orb_coord):
	# x and y represents the respective x and y coordinates of hero and orb
	y1, x1 = hero_coord
	y2, x2 = orb_coord

	if y2 < y1:
		if x2 < x1:
			return "northwest"
		elif x2 == x1:
			return "north"
		else:
			return "northeast"
	elif y2 == y1:
		if x2 < x1:
			return "west"
		else:
			return "east"
	else:
		if x2 < x1:
			return "southwest"
		elif x2 == x1:
			return "south"
		else:
			return "southeast"

# Save information of the game
# File will be saved in this format
"""
town_position1;town_position2;town_position3;town_position4;town_position5
orb_position
hero_position
hero.hp;hero.hasOrb
rat_king.hp
"""
def save_game(game_map, hero, rk):
	# Process towns position
	towns = []
	for r, c in game_map.towns:
		towns.append(f"{r},{c}")

	# Process number of days
	day_info = [game_map.day]

	# Process orb position
	r, c = game_map.orb
	orb_pos = [f"{r},{c}"]

	# Process hero position
	r, c = game_map.hero_position
	hero_pos = [f"{r},{c}"]

	# Process hero hp and whether hero has orb
	hero_info = []
	hero_info.append(hero.hp)
	hero_info.append(str(hero.hasOrb))

	# Process rat king hp
	rat_king_info = [rk.hp]

	# Write all information to file
	data = [towns, day_info, orb_pos, hero_pos, hero_info, rat_king_info]
	with open("save.txt", "w", newline='') as file:
		writer = csv.writer(file, delimiter=";")
		writer.writerows(data)
	
	print("Successfully saved game")


# Loads the information from save
# Returns Game, Hero and Rat King Objects
def load_game():
	try:
		# Read file
		with open("save.txt") as file:
			# If file is empty, start new game
			if os.stat("save.txt").st_size == 0:
				print("No saves detected, starting new game\n")
				return Game(), Hero(), RatKing()
			else:
				data = list(csv.reader(file, delimiter=';'))

		# Unpack towns information
		towns = []
		for ele in data[0]:
			r, c = ele.split(',')
			towns.append([int(r), int(c)])

		# Unpack day information
		day = int(data[1][0])
			
		# Unpack orb pos info
		r, c = data[2][0].split(',')
		orb_pos = [int(r), int(c)]

		# Unpack hero pos info
		r, c = data[3][0].split(',')
		hero_pos = [int(r), int(c)]

		# Unpack hero info
		hero_hp = int(data[4][0])
		if data[4][1] == "True":
			hero_hasOrb = True
		else:
			hero_hasOrb = False

		# Unpack rat king info
		rat_king_hp = int(data[5][0])

		# Generate the classes
		game_map = Game(towns, orb_pos, hero_pos, day)
		hero = Hero(hero_hp, hero_hasOrb)
		rk = RatKing(rat_king_hp)

		return game_map, hero, rk

	# If file is not found, starts new game
	except FileNotFoundError:
		print("No save file detected")
		return Game(), Hero(), RatKing()

	# If any other error occurs when reading file, 
	# file is corrupted and starts new game
	except Exception:
		print("Save file is corrupted, starting new game")
		return Game(), Hero(), RatKing()


# Prints out leaderboard
def print_leaderboard(leaderboard):
	print("===LEADERBOARD===")
	if len(leaderboard) == 0:
		print("No scores set")
	else:
		for row in leaderboard:
			print(f"Name: {row[0]}. Number of days: {row[1]}")
	print()


# Combat menu
def combat(game_map, hero, enemy):
	while not hero.dead and not enemy.dead:
		print("Encounter -", enemy)
		print("1) Attack")
		print("2) Run")
		user_input = validate_option("Enter choice: ", [1, 2])
		print()

		# After the hero attacks the enemy, if enemy is still alive, enemy will counter attack
		if user_input == 1:
			hero.attack(enemy)

			if not enemy.dead:
				enemy.attack(hero)

			# Checks whether hero is poisoned, poison effect will only last for 3 rounds
			# Decrease 1 debuff duration if hero is poisoned
			if hero.poison > 0:
				hero.hp -= 1
				print("You took 1 damage from poison")
				hero.poison -= 1
			
			# Checks if hero is corrupted
			if hero.corrupt > 0:
				# At the end of 3 rounds, restore hero defence
				if hero.corrupt == 1:
					hero.defence += 1
					hero.corrupt -= 1
				else:
					hero.corrupt -= 1
				print(f"You defence is reduced for {hero.corrupt} more rounds.")

		# User selects "Run and hide"
		elif user_input == 2:
			print("You run and hide.")
			print("1) View Character")
			print("2) View map")
			print("3) Move")
			print("4) Sense Orb")
			print("5) Exit Game")
			user_input = validate_option("Enter choice: ", [x for x in range(1, 6)])
			print()

			# If player enters anything besides 3 and 5, they will return to combat
			if user_input == 3:
				move(game_map, hero)
				return False # Return False to not quit the game
			elif user_input == 5:
				return True # Return True to quit the game

	# Check if hero was killed
	# If hero is killed, game ends and goes back to main menu
	if hero.dead:
		print("You have been killed")
		print("Game Over")
		return True # Return True to end the game since the Hero is dead
	else:
		return False # Hero is still alive, game continues


# Main game loop
def game_loop(game_map, hero, rk, leaderboard):
	# Keeps track of whether hero been to the wild after arriving at a town
	# Hero will meet an enemy whenever he steps out of the town
	outdoor = False
	# List of all enemies
	all_enemies = [Rat, PoisonRat, CorruptRat]
	# Damage bonus of enemies. As number of days increases, enemies will deal more damage
	# Increases difficulty of game as time passes by
	# +1 every 20 days
	multiplier = 0

	# Game loop continues until rat king is dead
	while not rk.dead:
		multiplier = game_map.day // 20

		# Checks whether hero is in a town
		if game_map.in_town():
			# Sets outdoor to False whenever hero steps into a town
			outdoor = False

			# Town menu
			print(f"Day {game_map.day}: You are in a town.")
			print("1) View Character")
			print("2) View map")
			print("3) Move")
			print("4) Reset")
			print("5) Save Game")
			print("6) Exit Game")
			user_input = validate_option("Enter choice: ", [x for x in range(1, 7)])
			print()

			if user_input == 1:
				print(hero)
			elif user_input == 2:
				print(game_map)
			elif user_input == 3:
				move(game_map, hero)
			elif user_input == 4:
				hero.hp = 20
				print("You are fully healed")

				game_map.new_day()
			elif user_input == 5:
				save_game(game_map, hero, rk)
			elif user_input == 6:
				break
		
		# Checks whether hero is with the Rat King
		elif game_map.with_rat_king():
			quit_game = combat(game_map, hero, rk)
			hero.remove_effects()

			if quit_game:
				break
		
		# Hero is in the wild
		else:
			print(f"Day {game_map.day}: You are out in the open.")
			if not outdoor:
				outdoor = True
				# Randomly chooses an enemy and goes into combat
				enemy = choice(all_enemies)(multiplier=multiplier)
				quit_game = combat(game_map, hero, enemy)
				hero.remove_effects()

				# Hero has died or user quits
				if quit_game:
					break
			
			# Outdoor menu that is not in combat
			else:
				print("1) View Character")
				print("2) View map")
				print("3) Move")
				print("4) Sense Orb")
				print("5) Exit Game")
				user_input = validate_option("Enter choice: ", [x for x in range(1, 6)])
				print()

				if user_input == 1:
					print(hero)
				elif user_input == 2:
					print(game_map)
				elif user_input == 3:
					move(game_map, hero)
				elif user_input == 4:
					if not hero.hasOrb:
						direction = find_direction(game_map.hero_position, game_map.orb)
						print(f"You sense the Orb of Power is to the {direction}\n")
					else:
						print("You have the Orb of Power\n")
				else:
					break
	
	if rk.dead:
		print("Congratulations you have defeated the Rat King")
		print("The world is saved")
		print()

		# Updates the leaderboard
		name = input("Please enter your name: ")
		leaderboard.append([name, game_map.day])
		# Sorts the leaderboard from lowest days to highest days
		leaderboard.sort(key=lambda x : x[1])
		# If there are more than 5 scores, remove the extra scores
		while len(leaderboard) > 5:
			leaderboard.pop()

		print_leaderboard(leaderboard)


def start_game():
	# Load leaderboard
	leaderboard = []
	try:
		with open("leadboard.txt") as file:
			if os.stat("save.txt").st_size != 0:
				for line in file:
					line = line[:-1]
					data = line.split(",")
					leaderboard.append([data[0], int(data[1])])

	# No leaderboard save file is found
	except FileNotFoundError:
		pass

	done = False
	while not done:
		# Initial selection of new game/resume game/ exit
		print("1) New Game")
		print("2) Resume Game")
		print("3) View Leaderboard")
		print("4) Exit Game")
		user_input = validate_option("Enter choice: ", [x for x in range(1, 5)])
		print()

		# Create new game
		if user_input == 1:
			game_map = Game()
			hero = Hero()
			rk = RatKing()
			game_loop(game_map, hero, rk, leaderboard)

		# Load game from save
		elif user_input == 2:
			game_map, hero, rk = load_game()

			game_loop(game_map, hero, rk, leaderboard)
		
		# View leaderboard
		elif user_input == 3:
			print_leaderboard(leaderboard)
		
		# Quit application
		elif user_input == 4:
			done = True

	# Update leaderboard
	with open("leadboard.txt", "w", newline='') as file:
			data = ""
			for row in leaderboard:
				data += f"{row[0]},{row[1]}\n"
			file.write(data)
			

	# Display to show that game has ended
	print("Application ended")


start_game()
