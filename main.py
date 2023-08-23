#  видимость бота

#        0                0 - пустота    # - еда     @ - бот
#        0
#        *  - всего комбинаций 9!

#             0 0 # # 0 @ @ # @            направления
#             0 # 0 # @ 0 @ @ #                           ^
#             | | | | | | | | |                    0      | y
#             0 1 2 3 4 5 6 7 8                  3 * 1    +--> x
#                                                  2

#       длинна хромосомы = 96

#   шаг вперед          -   0 - 31
#   поворот направо     -   32 - 47
#   поворот налево      -   48 - 63
#   атаковать           -   64 - 79
#   есть                -   80 - 95


import random

import pygame


def average_of_three(a, b, c):
    return (a + b + c) // 3


FIELD_WIDTH = 50


class Cage:
    type = "Cage"

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y


class Bot(Cage):
    type = "Bot"

    def __init__(self, x, y, chromosome=None) -> None:
        super().__init__(x, y)
        self.points = 0
        self.index = 0
        self.hp = 90
        self.alpha = random.randint(0, 3)
        if chromosome:
            self.chromosome = self.mutation(chromosome)
        else:
            self.chromosome = self.generate_chromosome()

        self.color = self.get_color()

    @staticmethod
    def generate_chromosome():
        return [[random.randint(0, 95) for _ in range(9)] for _ in range(96)]

    @staticmethod
    def mutation(chromosome):
        ch = 3  # %
        new_chromosome = []
        for line in chromosome:
            new_line = []
            for num in line:
                if ch <= random.randint(0, 100):
                    new_line.append(random.randint(0, 95))
                else:
                    new_line.append(num)
            new_chromosome.append(new_line)
        return new_chromosome

    def get_color(self):
        a = []
        b = []
        c = []
        for lines in self.chromosome:
            a.append(255 / 96 * average_of_three(lines[0], lines[3], lines[6]))
            b.append(255 / 96 * average_of_three(lines[1], lines[4], lines[7]))
            c.append(255 / 96 * average_of_three(lines[2], lines[5], lines[8]))
        return sum(a) / len(a), sum(b) / len(b), sum(c) / len(c)

    def brain(self, index_vision, ahead_of_the_bot=False, ahead_of_the_food=False):
        code = ""

        self.index = self.chromosome[self.index][index_vision]
        if 0 <= self.index <= 31:
            if not ahead_of_the_bot and not ahead_of_the_food:
                self.step()
        elif 32 <= self.index <= 47:
            self.rotate()
        elif 48 <= self.index <= 63:
            self.rotate(right=False)
        elif 64 <= self.index <= 79:
            if ahead_of_the_bot:
                code = "A"
        elif 80 <= self.index <= 95:
            if ahead_of_the_food:
                self.hp += 40
                code = "E"
        self.hp -= 1
        self.points += 1
        return code

    def step(self, forward=True):
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

    def rotate(self, right=True):
        if right:
            self.alpha = (self.alpha + 1) % 4
        else:
            self.alpha = (self.alpha - 1) % 4

    def get_coordinates_vision(self):
        if self.alpha == 0:
            return [self.x, (self.y + 1) % FIELD_WIDTH], [self.x, (self.y + 2) % FIELD_WIDTH]
        elif self.alpha == 1:
            return [(self.x + 1) % FIELD_WIDTH, self.y], [(self.x + 2) % FIELD_WIDTH, self.y]
        elif self.alpha == 2:
            return [self.x, (self.y - 1) % FIELD_WIDTH], [self.x, (self.y - 2) % FIELD_WIDTH]
        elif self.alpha == 3:
            return [(self.x - 1) % FIELD_WIDTH, self.y], [(self.x - 2) % FIELD_WIDTH, self.y]


class Food(Cage):
    type = "Food"

    def __init__(self, x, y) -> None:
        super().__init__(x, y)
        self.freshness = 200


def is_x_y(x, y):
    def f(obj):
        if obj.x == x and obj.y == y:
            return True
        else:
            return False

    return f


def is_bot(obj):
    if obj.type == "Bot":
        return True
    else:
        return False


def is_food(obj):
    if obj.type == "Food":
        return True
    else:
        return False


class Map:
    def __init__(self) -> None:
        self.field = []
        self.best = Bot(0, 0)
        self.time = 0

    @staticmethod
    def get_index_vision(vision_item):
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

    def step(self):
        if len(list(filter(is_bot, self.field))) == 0:
            self.field.append(Bot(random.randint(0, FIELD_WIDTH - 1), random.randint(0, FIELD_WIDTH - 1)))
            self.field.append(Bot(random.randint(0, FIELD_WIDTH - 1), random.randint(0, FIELD_WIDTH - 1)))
            self.field.append(Bot(random.randint(0, FIELD_WIDTH - 1), random.randint(0, FIELD_WIDTH - 1)))

        if len(list(filter(is_food, self.field))) <= (FIELD_WIDTH * FIELD_WIDTH) // 3.5:
            self.field.append(Food(random.randint(0, FIELD_WIDTH - 1), random.randint(0, FIELD_WIDTH - 1)))
            self.field.append(Food(random.randint(0, FIELD_WIDTH - 1), random.randint(0, FIELD_WIDTH - 1)))

        for item in self.field:
            if item.type == "Food":
                item.freshness -= 1
                if item.freshness <= 0:
                    self.field.remove(item)
            elif item.type == "Bot":
                if filter(is_x_y(item.x, item.y), self.field) is None:
                    continue
                vision_item = []
                for c in item.get_coordinates_vision():
                    try:
                        i = list(filter(is_x_y(*c), self.field))[0]
                    except:
                        i = Cage(0, 0)
                    vision_item.append(i)

                vision = vision_item[0]

                ahead_of_the_bot = False
                if vision.type == "Bot":
                    ahead_of_the_bot = True
                ahead_of_the_food = False
                if vision.type == "Food":
                    ahead_of_the_food = True

                code = item.brain(self.get_index_vision(vision_item),
                                  ahead_of_the_bot=ahead_of_the_bot,
                                  ahead_of_the_food=ahead_of_the_food)

                if code == "A":
                    vision.hp -= 5
                    if vision.hp <= 0:
                        self.field.append(Food(item.x, item.y))
                        self.field.remove(vision)
                elif code == "E":
                    self.field.remove(vision)

                if item.hp >= 270:
                    if random.choice([True, False]):
                        if random.choice([True, False]):
                            self.field.append(Bot((item.x + 1) % FIELD_WIDTH, item.y, chromosome=item.chromosome))
                        else:
                            self.field.append(Bot((item.x - 1) % FIELD_WIDTH, item.y, chromosome=item.chromosome))
                    else:
                        if random.choice([True, False]):
                            self.field.append(Bot(item.x, (item.y + 1) % FIELD_WIDTH, chromosome=item.chromosome))
                        else:
                            self.field.append(Bot(item.x, (item.y - 1) % FIELD_WIDTH, chromosome=item.chromosome))

                if item.hp <= 0:
                    self.field.append(Food(item.x, item.y))
                    self.field.remove(item)
                if len(list(filter(is_bot, self.field))) != 0:
                    best = list(sorted(list(filter(is_bot, self.field)), key=lambda x: x.points))[-1]
                    if self.best.points < best.points:
                        self.best = best
                self.time += 1


if __name__ == '__main__':
    WIDTH_GAME = 900
    WIDTH_TABLO = 400
    W = WIDTH_GAME / FIELD_WIDTH
    FPS = 40

    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)

    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH_GAME + WIDTH_TABLO, WIDTH_GAME))
    pygame.display.set_caption("LIFE")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    m = Map()

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        m.step()

        screen.fill(WHITE)
        for item in m.field:
            pygame.draw.rect(screen, item.color if item.type == "Bot" else GREEN, (item.x * W, item.y * W, W, W))
        text_best = font.render(f'best: {m.best.points}', True, (180, 0, 0))
        text_time = font.render(f'time: {m.time}', True, (180, 0, 0))

        screen.blit(text_best, (WIDTH_GAME + 125 + 4 * W, 2 * W - 18 + 32*2))
        pygame.draw.rect(screen, m.best.color, (WIDTH_GAME + 110, 32*2, 4 * W, 4 * W))

        screen.blit(text_time, (WIDTH_GAME + 125, 10))

        pygame.display.flip()

    pygame.quit()
