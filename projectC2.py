from random import randint

class Dot: #Создаем основной класс для дальнейшего пользования
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"

class BoardException(Exception): #Класс исключений и его дочерние классы
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелись за доску"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту точку"

class BoardWrongShipException(BoardException):
    pass

class Ship: #Создаем класс описывающий корабли
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ships_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ships_dots.append(Dot(cur_x, cur_y))

        return ships_dots

    def shooten(self, shot): #Функция для проверки выстрела
        return shot in self.dots

class Board: #Класс описывающий доску
    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid
        self.count = 0
        self.fielde = [["0"] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def __str__(self): #Вывод доски
        res = ""
        res += "   | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.fielde):
            res += f"\n {i +1 } | " + " | ".join(row) + " |"

        if self.hid: #Скрывает корабли противника
            res = res.replace("■", "0")
        return res

    def out(self, d): #Проверка выстрела в области поля
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb = False): #Выделяет контуры корабля
        near = [
            (-1,-1), (-1,0), (-1,1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.fielde[cur.x][cur.y] = "T"
                    self.busy.append(cur)

    def add_ship(self, ship): #Добавляет корабль на поле битвы
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.fielde[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d): #Функция выстрела и его проверка
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships: #Попадание по кораблю
            if ship.shooten(d):
                ship.lives -= 1
                self.fielde[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.fielde[d.x][d.y] = "T"
        print("Мимо!")
        return False

    def begin(self): #Пустой список уже использованных полей
        self.busy = []

    def defeat(self): #Условие поражения
        return self.count == len(self.ships)

class Player: #Класс для создания противника и игрока
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0,5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d

class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print("Введите 2 координаты!")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа!")
                continue

            x, y = int(x), int(y)

            return Dot(x-1, y-1)

class Game: #Логика игры
    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self): #Попытка расставить корабли игрока
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint (0, self.size), randint(0, self.size)), l, randint(0,1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass

        board.begin()
        return board

    def random_board(self): #Повторение в случае возвращения None
        board = None
        while board is None:
            board = self.try_board()
        return board

    def welcome(self): #Приветствие
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def print_board(self): #Печать игрового поля
        print("-" * 20)
        print("Доска пользователя:")
        print(self.us.board)
        print("-" * 20)
        print("Доска противника:")
        print(self.ai.board)
        print("-" * 20)

    def loop(self): #Цикл игры с ее результатами
        num = 0
        while True:
            self.print_board()
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит противник!")
                repeat = self.ai.move()

            if repeat:
                num -= 1

            if self.ai.board.defeat():
                self.print_board()
                print("Пользователь выиграл!")
                break

            if self.us.board.defeat():
                self.print_board()
                print("Противник выиграл!")
                break
            num += 1

    def start(self): #старт программы
        self.welcome()
        self.loop()

g = Game()
g.start()