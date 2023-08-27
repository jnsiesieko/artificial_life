import random

# всемкискампис

BOT_HP = 20  # Bot health
CHANCE = 1  # % Chance of chromosome mutation
FIELD_WIDTH = 50  # Field size


class Cage:  # Empty cage class needed for other classes
    type: str = "Cage"  # This variable is needed to check the class for type, you could probably think of a better way.

    def __init__(self, x: int, y: int) -> None:
        # coordinates needed to determine the position of the cell
        self.x: int = x
        self.y: int = y


class Bot(Cage):  # A class that realizes our bots
    type: str = "Bot"  # Same with Cage

    def __init__(self, x: int, y: int, chromosome: list = None, index_color: int = None) -> None:
        super().__init__(x, y)

        self.index: int = 0  # Is the most important variable in determining how a chromosome works

        # If the chromosome is already there, it mutates, if not, it's randomly generated
        if chromosome:
            self.chromosome: list = self.mutation(chromosome)
        else:
            self.chromosome: list = self.generate_chromosome()

        # To get the bot color, to differentiate between different bot behaviors

        if index_color:
            self.index_color: int = index_color
        else:
            self.index_color = random.randint(0, 95)

        self.color: tuple = self.get_color()

        self.alpha: int = random.randint(0, 3)  # Rotation angle

        self.hp: int = BOT_HP  # Bot health

        self.points: int = 0  # Bot points

    # Function for chromosome generation
    @staticmethod
    def generate_chromosome() -> list:
        return [[random.randint(0, 95) for _ in range(9)] for _ in range(96)]

    # Function for chromosome mutation
    @staticmethod
    def mutation(chromosome: list) -> list:
        chance: int = CHANCE  # Chance of chromosome mutation
        new_chromosome = []
        for line in chromosome:
            new_line = []
            for number in line:
                if chance >= random.randint(0, 100):
                    new_line.append(random.randint(0, 95))
                else:
                    new_line.append(number)
            new_chromosome.append(new_line)
        return new_chromosome

    # Color retrieval functions
    def get_color(self):

        # Function of the arithmetic mean of three numbers
        def average_of_three(number1: int, number2: int, number3: int):
            return (number1 + number2 + number3) // 3

        a: list = []
        b: list = []
        c: list = []

        for lines in self.chromosome:
            a.append(255 / 96 * average_of_three(lines[0], lines[3], lines[6]))
            b.append(255 / 96 * average_of_three(lines[1], lines[4], lines[7]))
            c.append(255 / 96 * average_of_three(lines[2], lines[5], lines[8]))
        return a[self.index_color], b[self.index_color], c[self.index_color]

    # Bot motion function
    def step(self, forward: bool = True) -> None:
        if forward:
            if self.alpha == 0:
                self.y = (self.y + 1) % FIELD_WIDTH
            elif self.alpha == 1:
                self.x = (self.x + 1) % FIELD_WIDTH
            elif self.alpha == 2:
                self.y = (self.y - 1) % FIELD_WIDTH
            elif self.alpha == 3:
                self.x = (self.x - 1) % FIELD_WIDTH
        else:
            if self.alpha == 0:
                self.y = (self.y - 1) % FIELD_WIDTH
            elif self.alpha == 1:
                self.x = (self.x - 1) % FIELD_WIDTH
            elif self.alpha == 2:
                self.y = (self.y + 1) % FIELD_WIDTH
            elif self.alpha == 3:
                self.x = (self.x + 1) % FIELD_WIDTH

    # Bot rotation function
    def rotate(self, right: bool = True) -> None:
        if right:
            self.alpha = (self.alpha + 1) % 4
        else:
            self.alpha = (self.alpha - 1) % 4

    # Function for obtaining coordinates of visible bot cells
    # I decided to make it in the Bot class itself
    def get_coordinates_vision(self) -> tuple:
        if self.alpha == 0:
            return [self.x, (self.y + 1) % FIELD_WIDTH], [self.x, (self.y + 2) % FIELD_WIDTH]
        elif self.alpha == 1:
            return [(self.x + 1) % FIELD_WIDTH, self.y], [(self.x + 2) % FIELD_WIDTH, self.y]
        elif self.alpha == 2:
            return [self.x, (self.y - 1) % FIELD_WIDTH], [self.x, (self.y - 2) % FIELD_WIDTH]
        elif self.alpha == 3:
            return [(self.x - 1) % FIELD_WIDTH, self.y], [(self.x - 2) % FIELD_WIDTH, self.y]

    # The most important function responsible for the work of the bot
    def brain(self, index_vision: int, ahead_of_the_bot: bool = False, ahead_of_the_food: bool = False) -> str:
        code: str = ""  # The code is necessary for further knowledge of what action the bot has

        self.index = self.chromosome[self.index][index_vision]  # obtaining the following index

        if 0 <= self.index <= 31:  # Step forward
            if not ahead_of_the_bot and not ahead_of_the_food:
                self.step()
        elif 32 <= self.index <= 47:  # Right turn
            self.rotate()
        elif 48 <= self.index <= 63:  # Left turn
            self.rotate(right=False)
        elif 64 <= self.index <= 79:  # Attack
            if ahead_of_the_bot:
                code = "A"
        elif 80 <= self.index <= 95:  # Eating
            if ahead_of_the_food:
                self.hp += 20
                code = "E"

        self.hp -= 1
        self.points += 1

        return code


class Food(Cage):  # Food grade
    type = "Food"  # Same with Cage

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.freshness: int = random.randint(100, 200)  # Food freshness, reaching the value 0 food is removed


# Filter auxiliary function
def creation_is_x_y(x: int, y: int):
    def f(obj: Cage):
        if obj.x == x and obj.y == y:
            return True
        else:
            return False

    return f


# Filter auxiliary function
def is_bot(obj: Cage) -> bool:
    if obj.type == "Bot":
        return True
    else:
        return False


# Filter auxiliary function
def is_food(obj: Cage) -> bool:
    if obj.type == "Food":
        return True
    else:
        return False


class Map:  # Field class
    def __init__(self) -> None:

        self.field: list = []  # List of all objects on the field

        self.best: Bot = Bot(0, 0)  # The best bot in the field

        self.time: int = 0  # Field time

    # Function for obtaining bot visibility index
    @staticmethod
    def get_index_vision(vision_item: tuple) -> int:
        if vision_item[0].type == "Cage" and vision_item[-1].type == "Cage":
            return 0
        elif vision_item[0].type == "Cage" and vision_item[-1].type == "Food":
            return 1
        elif vision_item[0].type == "Food" and vision_item[-1].type == "Cage":
            return 2
        elif vision_item[0].type == "Food" and vision_item[-1].type == "Food":
            return 3
        elif vision_item[0].type == "Cage" and vision_item[-1].type == "Bot":
            return 4
        elif vision_item[0].type == "Bot" and vision_item[-1].type == "Cage":
            return 5
        elif vision_item[0].type == "Bot" and vision_item[-1].type == "Bot":
            return 6
        elif vision_item[0].type == "Food" and vision_item[-1].type == "Bot":
            return 7
        elif vision_item[0].type == "Bot" and vision_item[-1].type == "Food":
            return 8

    # Field function
    def step(self):

        # If there are no bots on our field, we create three random ones
        if len(list(filter(is_bot, self.field))) <= (FIELD_WIDTH * FIELD_WIDTH) // 200:
            for _ in range(
                    round(((((FIELD_WIDTH * FIELD_WIDTH) // 200) - len(list(filter(is_bot, self.field)))) * 0.1))):
                self.field.append(Bot(random.randint(0, FIELD_WIDTH - 1), random.randint(0, FIELD_WIDTH - 1)))
                self.field.append(Bot(random.randint(0, FIELD_WIDTH - 1), random.randint(0, FIELD_WIDTH - 1)))

        # If we don't have enough food on the field, we create it
        if len(list(filter(is_food, self.field))) <= (FIELD_WIDTH * FIELD_WIDTH) // 2:
            for _ in range(
                    round(((((FIELD_WIDTH * FIELD_WIDTH) // 2) - len(list(filter(is_food, self.field)))) * 0.01))):
                self.field.append(Food(random.randint(0, FIELD_WIDTH - 1), random.randint(0, FIELD_WIDTH - 1)))

        # Running all over the field
        for item in self.field:
            if item.type == "Food":
                item.freshness -= 1
                if item.freshness <= 0:
                    self.field.remove(item)

            elif item.type == "Bot":
                if filter(creation_is_x_y(item.x, item.y), self.field) is None:
                    continue
                vision_item = []
                for c in item.get_coordinates_vision():
                    try:
                        i = list(filter(creation_is_x_y(*c), self.field))[0]
                    except:
                        i = Cage(0, 0)
                    vision_item.append(i)

                vision = vision_item[0]

                ahead_of_the_bot = False

                if vision_item[0].type == "Bot":
                    ahead_of_the_bot = True
                ahead_of_the_food = False
                if vision_item[0].type == "Food":
                    ahead_of_the_food = True

                code = item.brain(self.get_index_vision(vision_item),
                                  ahead_of_the_bot=ahead_of_the_bot,
                                  ahead_of_the_food=ahead_of_the_food)

                if code == "A" and ahead_of_the_bot:
                    vision.hp -= 20
                    if vision.hp <= 0:
                        self.field.append(Food(item.x, item.y))
                        self.field.remove(vision)
                elif code == "E":
                    self.field.remove(vision)

                if item.hp >= 80:
                    item.hp /= 2
                    if random.choice([True, False]):
                        if random.choice([True, False]):
                            self.field.append(Bot((item.x + 1) % FIELD_WIDTH, item.y, chromosome=item.chromosome,
                                                  index_color=item.index_color))
                        else:
                            self.field.append(Bot((item.x - 1) % FIELD_WIDTH, item.y, chromosome=item.chromosome,
                                                  index_color=item.index_color))
                    else:
                        if random.choice([True, False]):
                            self.field.append(Bot(item.x, (item.y + 1) % FIELD_WIDTH, chromosome=item.chromosome,
                                                  index_color=item.index_color))
                        else:
                            self.field.append(Bot(item.x, (item.y - 1) % FIELD_WIDTH, chromosome=item.chromosome,
                                                  index_color=item.index_color))

                if item.hp <= 0:
                    self.field.append(Food(item.x, item.y))
                    self.field.remove(item)

                if len(list(filter(is_bot, self.field))) != 0:
                    best = list(sorted(list(filter(is_bot, self.field)), key=lambda x: x.points))[-1]
                    if self.best.points < best.points:
                        self.best = best
                self.time += 1
