import random


class GameError(Exception):
    pass


class BoardOutException(GameError):
    pass


class InvalidPosition(GameError):
    pass


class Dot:
    x = None
    y = None

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'{{{self.x}, {self.y}}}'

    def out(self):
        return 6 <= self.x or self.x < 0 or 6 <= self.y or self.y < 0


class Ship:
    length = None
    first_point = None
    direction = None
    lives = None
    body = []
    hit_list = []

    def __init__(self, length, first_point, direction):
        self.length = length
        self.first_point = first_point
        self.direction = direction
        self.lives = length
        if direction == 1:
            # Заполняем тело корабля точками
            self.body = [Dot(x + first_point.x, first_point.y) for x in range(length)]
        elif direction == 2:
            self.body = [Dot(first_point.x, y + first_point.y) for y in range(length)]

    def __eq__(self, other):
        # Сравниваем 2 корабля, являются ли они одни и тем же
        return self.length == other.length and self.first_point == other.first_point and self.direction == other.direction

    def contour(self):  # Генерируем область вокруг корабля
        result = []
        for dot in self.body:
            # Создание точек вокруг горизонтали
            if self.direction == 1:
                result.append(Dot(dot.x, dot.y - 1))
                result.append(Dot(dot.x, dot.y + 1))
            # Создание точек вокруг вертикали
            if self.direction == 2:
                result.append(Dot(dot.x + 1, dot.y))
                result.append(Dot(dot.x - 1, dot.y))
        # Корабль горизонтально
        if self.direction == 1:
            #  Добавляем область слева
            result.append(Dot(self.first_point.x - 1, self.first_point.y - 1))
            result.append(Dot(self.first_point.x - 1, self.first_point.y))
            result.append(Dot(self.first_point.x - 1, self.first_point.y + 1))
            #  Добавляем область справа
            result.append(Dot(self.body[-1].x + 1, self.body[-1].y - 1))  # От хвоста корабля
            result.append(Dot(self.body[-1].x + 1, self.body[-1].y))
            result.append(Dot(self.body[-1].x + 1, self.body[-1].y + 1))
        # Корабль вертикально
        if self.direction == 2:
            # Область сверху
            result.append(Dot(self.first_point.x - 1, self.first_point.y - 1))
            result.append(Dot(self.first_point.x, self.first_point.y - 1))
            result.append(Dot(self.first_point.x + 1, self.first_point.y - 1))
            # Область снизу
            result.append(Dot(self.body[-1].x - 1, self.body[-1].y + 1))
            result.append(Dot(self.body[-1].x, self.body[-1].y + 1))
            result.append(Dot(self.body[-1].x + 1, self.body[-1].y + 1))
        return result


class Board:
    cels = None
    ships = None
    hid = False
    alives_count = None

    def __init__(self, hid):
        self.cels = [[], [], [], [], [], []]
        self.ships = []
        self.alives_count = 0
        self.hid = hid
        for x in range(6):
            for y in range(6):
                self.cels[x].append('~')

    def add_ship(self, ship):
        if len(self.ships) >= 6:
            raise BoardOutException('Превышен лимит кораблей')
        if ship in self.ships:
            raise InvalidPosition('Корабль уже на доске')
        for dot in ship.body:  # Точки внутри нового корабля
            for board_ship in self.ships:  # Корабль из стопки кораблей на доске
                if dot in board_ship.body or dot in board_ship.contour():  # Входит ли точка нового корабля в расположение кораблей на доске
                    raise InvalidPosition('Нельзя поставить корабль на данную позицию')
            if dot.out():
                raise BoardOutException('Корабль выходит за пределы')
        self.ships.append(ship)
        self.alives_count += 1
        if not self.hid:
            for dot in ship.body:
                self.cels[dot.x][dot.y] = '■'

    def print(self, debug=False):
        print('=' * 80)
        for y in range(-1, 6):
            for x in range(-1, 6):
                if x == -1 and y == -1:
                    print('  | ', end='')
                elif x == -1:
                    print(str(y + 1 if not debug else y) + ' | ', end='')
                elif y == -1:
                    print(str(x + 1 if not debug else x) + ' | ', end='')
                else:
                    print(str(self.cels[x][y]) + ' | ', end='')
            print()
        print('=' * 80)

    def shot(self, dot):
        if dot.out():
            raise BoardOutException('Выстрел выходит за пределы')
        elif str(self.cels[dot.x][dot.y]) in 'X.':
            raise InvalidPosition('Нельзя стрелять по использованным точкам')
        for ship in self.ships:
            if dot in ship.body:
                self.cels[dot.x][dot.y] = 'X'
                ship.lives -= 1
                if ship.lives == 0:
                    self.alives_count -= 1
                return True
        if self.cels[dot.x][dot.y] == '~':
            self.cels[dot.x][dot.y] = '.'
        return False

# b = Board(hid=True)
# b.add_ship(Ship(3, Dot(3, 4), 1))
# c = Board(hid=False)
# c.add_ship(Ship(2, Dot(3, 2), 1))
# b.print(debug=True)
# c.print(debug=True)


class Player:
    board = None
    enemy_board = None

    def __init__(self, board, enemy_board):
        self.board = board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError()

    def move(self):
        reshot = True
        while reshot:
            reshot = False
            shot_dot = self.ask()  # Спрашиваем про выстрел
            try:
                reshot = self.enemy_board.shot(shot_dot)  # Производим выстрел
                if reshot and self.enemy_board.hid:
                    self.enemy_board.print()
                    print('Попал!')
            except (BoardOutException, InvalidPosition) as error:
                reshot = True
                if self.enemy_board.hid:
                    print(error)
            if self.enemy_board.alives_count == 0:
                reshot = False


class Ai(Player):
    def ask(self):
        return Dot(random.randint(0, 5), random.randint(0, 5))


class User(Player):
    def ask(self):
        x, y = input('Введите координату выстрела через пробел:\n').split(' ', maxsplit=2)
        return Dot(int(x) - 1, int(y) - 1)


class Game:
    user_player = None
    user_board = None
    ai_board = None
    ai_player = None

    def __init__(self):
        self.user_board = self.random_board(hidden=False)
        self.ai_board = self.random_board(hidden=True)
        self.user_player = User(self.user_board, self.ai_board)
        self.ai_player = Ai(self.ai_board, self.user_board)

    def random_board(self, hidden):
        counter = 0
        board = None
        while True:
            if counter >= 2000:
                counter = 0
            if counter == 0:
                board = Board(hidden)
            if len(board.ships) >= 6:
                break
            length = 3 if len(board.ships) == 0 else (2 if len(board.ships) < 3 else 1)
            try:
                board.add_ship(
                    ship=Ship(
                        length=length,
                        first_point=Dot(x=random.randint(0, 6 - length), y=random.randint(0, 6 - length)),
                        direction=random.randint(1, 2),
                    )
                )
            except (InvalidPosition, BoardOutException):
                pass
            counter += 1
        return board

    def greet(self):
        print('Приветствую тебя путник!')
        print('Во время игры следуйте инструкциям:')

    def loop(self):
        end_game = False
        winner = None
        while not end_game:
            self.user_board.print()
            self.ai_board.print()
            self.user_player.move()
            if self.ai_board.alives_count == 0:
                winner = 'Пользователь'
                break
            self.ai_player.move()
            if self.user_board.alives_count == 0:
                winner = 'Компьютер'
                break
        self.user_board.print()
        self.ai_board.print()
        print(f'Победитель: {winner}')

    def start(self):
        self.greet()
        self.loop()


Game().start()


