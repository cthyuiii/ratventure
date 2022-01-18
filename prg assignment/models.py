from random import randint, choice

class Game:
    def __init__(self, towns=None, orb=None, hero_pos=[0, 0], day=1):
        # Generate location of towns randomly when creating new game
        if towns == None:
            # Split the areas into 4 sections. Each section is at least 3 steps away from each other
            area1 = [[3, 0], [3, 1], [4, 0], [4, 1], [5, 0], [5, 1], [6, 0], [6, 1]]
            area2 = [[0, 3], [1, 3], [0, 4], [1, 4], [0, 5], [1, 5], [0, 6], [1, 6]]
            area3 = [[6, 3], [6, 4], [7, 3], [7, 4], [7, 5]]
            area4 = [[3, 7], [4, 6], [4, 7]]
            
            self.towns = [[0, 0]]
            self.towns.append(choice(area1))
            self.towns.append(choice(area2))
            self.towns.append(choice(area3))
            self.towns.append(choice(area4))
        else:
            self.towns = towns

        # For debugging purposes
        # self.towns = [[0, 0], [1, 3], [2, 5], [3, 1], [6, 4]]

        # Generates location of orb randomly when creating new game
        if orb == None:
            valid_locations = []
            for i in range(8):
                for j in range(8):
                    valid_locations.append([i, j])
            
            # Orb cannot be in the top left region
            for i in range(4):
                for j in range(4):
                    valid_locations.remove([i, j])
            valid_locations.remove([7, 7])

            # Orb cannot be in the same position as a town
            for coord in self.towns:
                if coord in valid_locations:
                    valid_locations.remove(coord)

            self.orb = choice(valid_locations)
        else:
            self.orb = orb

        # For debugging purposes
        # print("ORB POSITION:", self.orb)

        # Position of the hero
        self.hero_position = hero_pos
        # Position of rat king
        self.rat_king = [7, 7]
        # Number of days
        self.day = day
        # Map of the game
        self.world_map = [[' ' for i in range(8)] for j in range(8)]
        for r, c in self.towns:
            self.world_map[r][c] = 'T'
        r, c = self.rat_king
        self.world_map[r][c] = 'K'

    def new_day(self):
        self.day += 1
    
    # Checks whether hero is in a town
    def in_town(self):
        r, c = self.hero_position
        return self.world_map[r][c] == "T"
    
    # Checks whether hero is in same position as Rat King
    def with_rat_king(self):
        r, c = self.hero_position
        return self.world_map[r][c] == "K"

    # Checks whether user enters a valid move,
    # Moves the hero if move is valid
    def is_valid_move(self, direction):
        if direction == "W":
            if self.hero_position[0] > 0:
                self.hero_position[0] -= 1
                return True
            else:
                return False
        elif direction == "A":
            if self.hero_position[1] > 0:
                self.hero_position[1] -= 1
                return True
            else:
                return False
        elif direction == "S":
            if self.hero_position[0] < 7:
                self.hero_position[0] += 1
                return True
            else:
                return False
        elif direction == "D":
            if self.hero_position[1] < 7:
                self.hero_position[1] += 1
                return True
            else:
                return False
        else:
            return False
    
    # Display the map
    def __str__(self):
        # Creates a deepcopy of the world map
        temp = []
        for row in self.world_map:
            temp.append(list(row))
        
        # Insert hero in map
        row, col = self.hero_position
        if temp[row][col] == "T":
            temp[row][col] = "H/T"
        elif temp[row][col] == "K":
            temp[row][col] = "H/K"
        else:
            temp[row][col] = "H"
            
        # Prints out structure of map
        display = ""
        for row in temp:
            display += "+---+---+---+---+---+---+---+---+"
            display += "\n"
            for ele in row:
                display += "|"
                display += "{:^3}".format(ele)
            display += "|\n"
        display += "+---+---+---+---+---+---+---+---+"
        return display

# Base class of each character
class Character:
    def __init__(self, name, min_damage, max_damage, defence, hp):
        self.name = name
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.defence = defence
        self.hp = hp
        self.dead = False

    # Display info of the character
    def __str__(self):
        return '''{}\nDamage: {}-{}\nDefence: {}\nHP: {}\n'''\
            .format(self.name, self.min_damage, self.max_damage, self.defence, self.hp)


# Class of basic rat
class Rat(Character):
    def __init__(self, name="Rat", min_damage=1, max_damage=3, defence=1, hp=10, gold=5, multiplier=1):
        super().__init__(name, min_damage+multiplier, max_damage+multiplier, defence, hp)
        self.gold = gold
    
    def attack(self, other):
        atk = randint(self.min_damage, self.max_damage)
        # Modifies attack damage based on hero's defence
        atk -= other.defence
        if atk > 0:
            other.hp -= atk
        else:
            atk = 0
            
        print(f"Ouch! {self.name} hit you for {atk} damage\n")
        if other.hp <= 0:
            other.dead = True


# New rat enemy with poison effect
class PoisonRat(Rat):
    def __init__(self, multiplier=1):
        super().__init__("Poison Rat", 2, 4, 1, 8, 6, multiplier)
    
    def attack(self, other):
        super().attack(other)
        # Hero will get poisoned for 3 combat rounds
        if other.poison == 0:
            other.poison = 3
            print("You have been poisoned for 3 rounds")
            print("You will take 1 damage per combat round\n")


# New rat enemy that decreases defence of hero
class CorruptRat(Rat):
    def __init__(self, multiplier=1):
        super().__init__("Corrupt Rat", 2, 4, 1, 8, 10, multiplier)
    
    def attack(self, other):
        # Defence reduced by 1 for 3 rounds
        if other.corrupt == 0:
            other.corrupt = 3
            other.defence -= 1
            print("Your defence has been reduced by 1 for 3 rounds\n")
        super().attack(other)


class RatKing(Rat):
    def __init__(self, hp=25):
        super().__init__("The Rat King", 8, 12, 5, hp, 0, 0)


# Hero class        
class Hero(Character):
    def __init__(self, hero_hp=20, hero_hasOrb=False):
        super().__init__("The Hero", 2, 4, 1, hero_hp)
        self.hasOrb = hero_hasOrb
        self.poison = 0
        self.corrupt = 0
        self.total_gold = 0
        self.inventory = []

        # When loading from save, if hero has obtained orb of power,
        # increase damage and defence by 5
        if self.hasOrb:
            self.min_damage += 5
            self.max_damage += 5
            self.defence += 5

    def attack(self, other):
        atk = randint(self.min_damage, self.max_damage)

        # Does not deal damage if enemy is the Rat King and the Hero does not have Orb of Power
        if type(other) == RatKing and self.hasOrb == False:
            atk = 0
            print("You do not have the Orb of Power. The Rat King is immune.")

        # Modifies attack damage based on enemy's defence
        atk -= other.defence
        if atk > 0:
            other.hp -= atk
        else:
            atk = 0

        # Print damage dealt
        print(f"You dealt {atk} damage to {other.name}")
        # Check if enemy is dead, earns gold if enemy is killed
        if other.hp <= 0:
            other.dead = True
            self.total_gold += other.gold
            print(f"{other.name} is dead. You are victorious!")

    # Reset effects at the end of combat
    def remove_effects(self):
        self.poison = 0
        self.corrupt = 0
 
    # Increase damage and defence when hero gets orb
    def get_orb(self):
        if not self.hasOrb:
            self.min_damage += 5
            self.max_damage += 5
            self.defence += 5
            self.hasOrb = True
            print("You have found the Orb of Power")
            print("Your attack increases by 5!")
            print("Your defense increases by 5!")
            print()

    # Print out hero information
    def __str__(self):
        data = super().__str__()
        data += f"Gold: {self.total_gold}\n"
        if self.hasOrb:
            data += "You are holding the Orb of Power\n"
        return data
