import pygame
import numpy as np
import math
import random
import time
import alpha_beta

MAX, MIN = 1000, -1000

display_width = 900
display_height = 1024

pygame.init()

pygame.display.set_caption("Shax")

screen = pygame.display.set_mode((display_height, display_width))

pawn_w = pygame.image.load("2.png")

pawn_b = pygame.image.load("1.png")

pawn_w = pygame.transform.scale(pawn_w, (80, 80))
pawn_w.set_alpha(None)
pawn_w.set_colorkey((200, 250, 200))
pawn_b = pygame.transform.scale(pawn_b, (80, 80))
pawn_b.set_alpha(None)
pawn_b.set_colorkey((200, 250, 200))
background = pygame.image.load("bgd.png")
board = pygame.image.load("board.png")

pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.load("Bread.ogg")


put_sound1 = pygame.mixer.Sound("putting_sound1.ogg")
put_sound1.set_volume(0.3)
put_sound2 = pygame.mixer.Sound("putting_sound2.ogg")
put_sound2.set_volume(0.3)
move_sound1 = pygame.mixer.Sound("moving_sound1.ogg")
move_sound1.set_volume(0.3)
move_sound2 = pygame.mixer.Sound("moving_sound2.ogg")
move_sound2.set_volume(0.3)
take_sound1 = pygame.mixer.Sound("taking_sound1.ogg")
take_sound1.set_volume(0.3)
take_sound2 = pygame.mixer.Sound("taking_sound2.ogg")
take_sound2.set_volume(0.3)


pygame.display.set_icon(pawn_w)
phase = 0

pawns_count = [0, 0]
first_mill = 0
# This is Mills current, Mills opponent, Blocked current, Blocked opponent,
# Number of pieces current, Number of pieces opponent, Won?
current_stats = [0, 0, 0, 0, 0, 0, 0]

turn = 1
win_player = 0


class Point:

    def __init__(self, layer, x, y):
        self.x = x
        self.y = y
        self.layer = layer
        self.pos_x, self.pos_y = get_point_position(layer, x, y)
        self.state = 0
        self.neighbors = []

    def copy(self):
        p = Point(self.layer, self.x, self.y)
        p.change_state(self.state)
        p.neighbors = self.neighbors.copy()
        return p

    def get_position(self):
        return self.pos_x, self.pos_y

    def get_l_x_y(self):
        return self.layer, self.x, self.y

    def change_state(self, state):
        self.state = state

    def add_neighbor(self, point):
        self.neighbors.append(point)

    def get_neighbors(self):
        return self.neighbors

    def get_state(self):
        return self.state

    def print(self):
        print('Punkt, layer:'+str(self.layer)+', x:'+str(self.x)+', y:'+str(self.y))

    def is_neighbor(self, p):
        return self.neighbors.__contains__(p)

    def calculate_distance(self, p_x, p_y):
        result = pow((p_x-(self.pos_x+40)), 2)+pow((p_y-(self.pos_y+40)), 2)
        result = math.sqrt(float(result))
        return result


class TreeBranch:

    def __init__(self, parent):
        self.parent = parent
        self.move = None
        self.stats = []
        self.current_board = None
        self.next = {}
        self.score = 0
        self.children = []

    def print(self):
        print(self.move)
        print(self.stats)


    def heritage(self):
        self.move = self.parent.next.copy()
        self.current_board = copy(self.parent.current_board)

    def set_root(self):
        self.next['phase'] = phase
        self.next['turn'] = turn
        self.next['first_mill'] = first_mill
        self.next['double_exists'] = False
        self.stats = current_stats.copy()
        self.current_board = copy(layers)

    def set_point(self, l, x, y):
        self.move['point'] = self.current_board[l, x, y]

    def set_temp(self, l, x, y):
        self.move['temp'] = self.current_board[l, x, y]

    def add_child(self, child):
        self.children.append(child)

    def get_phase(self):
        return self.next['phase']

    def get_turn(self):
        return self.next['turn']

    def get_board(self):
        return self.current_board

    def get_children(self):
        return self.children

    def determine_stats(self):
        self.stats, self.score = evaluation(self.current_board)

    def determine_board(self):
        self.current_board, self.next = game_simulation(self.move, self.current_board)

    def determine_double(self, l, x, y):
        self.move['phase'] = self.next['phase']
        self.move['double'] = self.current_board[l, x, y]
        self.move['double_exists'] = True
        self.current_board, self.next = game_simulation(self.move, self.current_board)


layers = np.empty((3, 3, 3), dtype=Point)

def print_board(board):
    print(str(board[0,0,0].get_state())+'XX'+str(board[0,1,0].get_state())+'XX'+str(board[0,2,0].get_state()))
    print('X'+str(board[1, 0, 0].get_state()) + 'X' + str(board[1, 1, 0].get_state()) + 'X' + str(board[1, 2, 0].get_state())+'X')
    print('XX' + str(board[2, 0, 0].get_state()) + str(board[2, 1, 0].get_state()) + str(board[2, 2, 0].get_state()) + 'XX')
    print(str(board[0, 0, 1].get_state()) + str(board[1, 0, 1].get_state()) + str(board[2, 0, 1].get_state()) + 'X' + str(board[2, 2, 1].get_state()) + str(board[1, 2, 1].get_state()) + str(board[0, 2, 1].get_state()))
    print('XX' + str(board[2, 0, 2].get_state()) + str(board[2, 1, 2].get_state()) + str(board[2, 2, 2].get_state()) + 'XX')
    print('X' + str(board[1, 0, 2].get_state()) + 'X' + str(board[1, 1, 2].get_state()) + 'X' + str(board[1, 2, 2].get_state()) + 'X')
    print(str(board[0, 0, 2].get_state()) + 'XX' + str(board[0, 1, 2].get_state()) + 'XX' + str(board[0, 2, 2].get_state()))


def not_turn(t = None):
    if not t:
        t = turn
    if t == 1:
        return 2
    else:
        return 1

def add_neighbors(point):
    if point.x < 2:
        if layers[point.layer, point.x+1, point.y]:
            point.add_neighbor(layers[point.layer, point.x+1, point.y])
    if point.x > 0:
        if layers[point.layer, point.x - 1, point.y]:
            point.add_neighbor(layers[point.layer, point.x - 1, point.y])
    if point.y < 2:
        if layers[point.layer, point.x, point.y+1]:
            point.add_neighbor(layers[point.layer, point.x, point.y+1])
    if point.y > 0:
        if layers[point.layer, point.x, point.y-1]:
            point.add_neighbor(layers[point.layer, point.x, point.y-1])
    if point.x == 1 or point.y == 1:
        if point.layer < 2:
            point.add_neighbor(layers[point.layer+1, point.x, point.y])
        if point.layer > 0:
            point.add_neighbor(layers[point.layer-1, point.x, point.y])


def copy(board):
    new_board = np.empty((3, 3, 3), dtype=Point)
    for l in range(0,3):
        for x in range(0,3):
            for y in range(0,3):
                if board[l, x, y]:
                    new_board[l, x, y] = board[l, x, y].copy()

    return new_board


def points_setup():
    for l in range(0, 3):
        for i in range(0, 3):
            for j in range(0, 3):
                if not (i == 1 and j == 1):
                    layers[l, i, j] = Point(l, i, j)
                else:
                    layers[l, i, j] = None
    for l in range(0, 3):
        for x in range(0, 3):
            for y in range(0, 3):
                if not (x == 1 and y == 1):
                    add_neighbors(layers[l, x, y])
    return layers


def text_objects(text, font):
    textSurface = font.render(text, True, (0, 0, 0))
    return textSurface, textSurface.get_rect()


def get_point_position(layer, x, y):
    base_x = 0
    base_y = 0
    if layer == 0:
        base_x = 120 + (350*x)
        base_y = 80 + (350*y)
    if layer == 1:
        base_x = 240 + (230 * x)
        base_y = 200 + (230 * y)
    if layer == 2:
        base_x = 350 + (120 * x)
        base_y = 310 + (120 * y)
    return base_x, base_y


def which_point(pos):
    for i in layers:
        for j in i:
            for k in j:
                if k:
                    if k.calculate_distance(pos[0], pos[1]) < 60:
                        return k
    return None


def draw_on_point(point, white):
    if white == 1:
        point.change_state(1)
    else:
        point.change_state(2)
    redraw_board()


def redraw_board():
    screen.blit(background, (0, 0))
    screen.blit(board, (103, 100))
    for l in layers:
        for x in l:
            for p in x:
                if p:
                    if not p.get_state() == 0:
                        pos_x, pos_y = p.get_position()
                        if p.get_state() == 1:
                            screen.blit(pawn_w, (pos_x, pos_y))
                        else:
                            screen.blit(pawn_b, (pos_x, pos_y))
    score_update()


def game_reset():
    global turn, phase, first_mill, win_player
    for l in layers:
        for x in l:
            for p in x:
                if p:
                    p.change_state(0)
    screen.blit(background, (0, 0))
    screen.blit(board, (103, 100))
    pawns_count[0] = 0
    pawns_count[1] = 0
    turn = 1
    phase = 0
    first_mill = 0
    win_player = 0
    pygame.display.flip()


def message_display(text, x, y):
    largeText = pygame.font.Font('freesansbold.ttf', 30)
    TextSurf, TextRect = text_objects(text, largeText)
    TextRect.center = (x, y)
    screen.blit(TextSurf, TextRect)


def score_update():
    message_display('Tura: Gracz '+str(turn), (display_width/2)+50, 50)
    message_display('Białych: ' + str(pawns_count[0]), 100, 50)
    message_display('Czarnych: '+str(pawns_count[1]), display_width, 50)


def switch_position(p1, p2):
    color = p1.get_state()
    p1.change_state(0)
    p2.change_state(color)
    redraw_board()
    pygame.display.flip()


def animated_switch_position(p1: Point, p2: Point):
    color = p1.get_state()
    if color == 1:
        image = pawn_w
    else:
        image = pawn_b
    pos_x1, pos_y1 = p1.get_position()
    pos_x2, pos_y2 = p2.get_position()
    p1.change_state(0)
    redraw_board()
    r = random.randint(0, 1)
    if r == 0:
        move_sound1.play()
    else:
        move_sound2.play()
    time.sleep(0.2)
    if pos_x1 == pos_x2:
        if pos_y1 > pos_y2:
            dist = pos_y1-pos_y2
            temp = int(dist/30)
            while dist > 0:
                pos_y1 = pos_y1-temp
                screen.blit(image, (pos_x1, pos_y1))
                pygame.display.flip()
                redraw_board()
                dist = dist-temp
        else:
            dist = pos_y2 - pos_y1
            temp = int(dist / 30)
            while dist > 0:
                pos_y1 = pos_y1 + temp
                screen.blit(image, (pos_x1, pos_y1))
                pygame.display.flip()
                redraw_board()
                dist = dist - temp
    else:
        if pos_x1 > pos_x2:
            dist = pos_x1-pos_x2
            temp = int(dist / 30)
            while dist > 0:
                pos_x1 = pos_x1-temp
                screen.blit(image, (pos_x1, pos_y1))
                pygame.display.flip()
                redraw_board()
                dist = dist-temp
        else:
            dist = pos_x2 - pos_x1
            temp = int(dist / 30)
            while dist > 0:
                pos_x1 = pos_x1 + temp
                screen.blit(image, (pos_x1, pos_y1))
                pygame.display.flip()
                redraw_board()
                dist = dist - temp
    p2.change_state(color)
    redraw_board()
    pygame.display.flip()


def remove_piece(p):
    global phase, win_player
    state = p.get_state()
    pawns_count[state - 1] = pawns_count[state - 1] - 1
    if pawns_count[state-1] == 2:

        win_player = turn
        phase = 6

    r = random.randint(0, 1)
    if r == 0:
        take_sound1.play()
    else:
        take_sound2.play()
    p.change_state(0)
    redraw_board()
    pygame.display.flip()


def switch_turn():
    global turn
    if turn == 1:
        turn = 2
    else:
        turn = 1
    redraw_board()
    pygame.display.flip()
    print("Now it's player " + str(turn) + " turn")


def check_for_mills(board_layers, p: Point):
    player = p.get_state()
    l, x, y = p.get_l_x_y()
    mill = True
    if board_layers[1, x, y]:
        for i in range(0, 3):
            if board_layers[1, x, y].is_neighbor(board_layers[i, x, y]) or i == 1:
                if not board_layers[i, x, y].get_state() == player:
                    mill = False
            else:
                mill = False
        if mill:
            return True
    mill = True
    if board_layers[l, 1, y]:
        for i in range(0, 3):
            if board_layers[l, 1, y].is_neighbor(board_layers[l, i, y]) or i == 1:
                if not board_layers[l, i, y].get_state() == player:
                    mill = False
            else:
                mill = False
        if mill:
            return True
    mill = True
    if board_layers[l, x, 1]:
        for i in range(0, 3):
            if board_layers[l, x, 1].is_neighbor(board_layers[l, x, i]) or i == 1:
                if not board_layers[l, x, i].get_state() == player:
                    mill = False
            else:
                mill = False
        if mill:
            return True
    return False


def check_available_moves(player, board_layers):
    for l in board_layers:
        for x in l:
            for p in x:
                if p:
                    if p.get_state() == player:
                        for i in p.get_neighbors():
                            if i.get_state() == 0:
                                return True
    return False


def game_simulation(move, board_layers):
    next_move = {'phase': move['phase'], 'turn': move['turn'], 'first_mill': move['first_mill'], 'double_exists': False}
    if move['double_exists']:
        l, x, y = move['double'].get_l_x_y()
    else:
        l, x, y = move['point'].get_l_x_y()
    if 'temp' in move:
        l_t, x_t, y_t = move['temp'].get_l_x_y()

    if move['phase'] == 0:
        board_layers[l, x, y].change_state(move['turn'])
        if move['first_mill'] == 0 and check_for_mills(board_layers, move['point']):
            next_move['first_mill'] = move['turn']
        next_move['turn'] = not_turn(move['turn'])
        if count_player(2, board_layers) == 9:
            if move['first_mill'] == 0:
                next_move['phase'] = 2
                next_move['turn'] = not_turn(move['turn'])
            else:
                next_move['phase'] = 1
                next_move['turn'] = next_move['first_mill']

    else:
        if move['phase'] == 1:
            if not move['first_mill'] == 3:
                board_layers[l, x, y].change_state(0)
                next_move['turn'] = not_turn(move['turn'])
                if move['first_mill'] == 3:
                    next_move['phase'] = 2
                next_move['first_mill'] = 3
        else:
            if move['phase'] == 2:
                board_layers[l_t, x_t, y_t].change_state(0)
                board_layers[l, x, y].change_state(move['turn'])
                if check_for_mills(board_layers, move['point']):
                    next_move['turn'] = move['turn']
                    next_move['phase'] = 3
                else:
                    next_move['turn'] = not_turn(move['turn'])
            else:
                if move['phase'] == 3:
                        board_layers[l, x, y].change_state(0)
                        next_move['turn'] = not_turn(move['turn'])
                        if count_player(next_move['turn'], board_layers) < 3:
                            next_move['phase'] = 6
                        else:
                            next_move['phase'] = 2
                else:
                    if move['phase'] == 4:
                        board_layers[l_t, x_t, y_t].change_state(0)
                        board_layers[l, x, y].change_state(move['turn'])
                        next_move['phase'] = 2
    if not next_move['phase'] == 6 and not check_available_moves(next_move['turn'], board_layers):
        next_move['phase'] = 2
        next_move['turn'] = not_turn(next_move['turn'])
    return board_layers, next_move

def game(point):
    global turn, phase, first_mill, temp
    if phase == 0:
        if point.get_state() == 0:
            r = random.randint(0, 1)
            if r == 0:
                put_sound1.play()
            else:
                put_sound2.play()
            pawns_count[turn - 1] = pawns_count[turn - 1] + 1
            draw_on_point(point, turn)
            pygame.display.flip()
            if first_mill == 0 and check_for_mills(layers, point):
                first_mill = turn
                print('FOUND')
            switch_turn()
        if pawns_count[1] == 9:
            if first_mill == 0:
                phase = 2
                switch_turn()
            else:
                phase = 1

    else:
        if phase == 1:
            if not first_mill == 3:
                turn = first_mill
            if not turn == point.get_state() and not point.get_state() == 0:
                remove_piece(point)
                switch_turn()
                if first_mill == 3:
                    phase = 2
                first_mill = 3
        else:
            if phase == 2:
                if point.get_state() == turn:
                    temp = point
                if point.get_state() == 0:
                    if point.is_neighbor(temp):
                        animated_switch_position(temp, point)
                        temp = None
                        if check_for_mills(layers, point):
                            phase = 3
                        else:
                            switch_turn()
            else:
                if phase == 3:
                    if not turn == point.get_state():
                        remove_piece(point)
                        switch_turn()
                        if not phase == 6:
                            phase = 2
                else:
                    if phase == 4:
                        if point.get_state() == turn:
                            temp = point
                        if point.get_state() == 0:
                            if point.is_neighbor(temp):
                                animated_switch_position(temp, point)
                                temp = None
                                switch_turn()
                                phase = 2


def check_for_blocked(board_layers):
    blocked_list = [0,0]

    for l in board_layers:
        for x in l:
            for p in x:
                if p:
                    if not p.get_state()==0:
                        neighbors = p.get_neighbors()
                        blocked = True
                        for z in neighbors:
                            if z.get_state() == 0:
                                blocked = False
                        if blocked:
                            blocked_list[p.get_state()-1] = blocked_list[p.get_state()-1] + 1

    # print('Blocked current player: '+ str(blocked_list[turn-1])+', blocked opponent: '+ str(blocked_list[not_turn()-1]))
    return blocked_list


def count_mills(board_layers):
    mills = [0,0]
    mill_board_layers = [board_layers[0, 0, 1].get_state(), board_layers[0, 1, 0].get_state(), board_layers[0, 2, 1].get_state(),
                   board_layers[0, 1, 2].get_state()]
    for x in range(0,len(mill_board_layers)):
        if mill_board_layers[x] == 0:
            mill_board_layers[x] = -1

    for l in range(0,3):
        if not board_layers[l, 0, 1].get_state() == mill_board_layers[0]:
            mill_board_layers[0] = -1
        if not board_layers[l, 1, 0].get_state() == mill_board_layers[1]:
            mill_board_layers[1] = -1
        if not board_layers[l, 2, 1].get_state() == mill_board_layers[2]:
            mill_board_layers[2] = -1
        if not board_layers[l, 1, 2].get_state() == mill_board_layers[3]:
            mill_board_layers[3] = -1

        p = board_layers[l,0,0].get_state()
        if not p == 0:
            if board_layers[l,1,0].get_state()==p:
                if board_layers[l,2,0].get_state()==p:
                    mills[p-1] = mills[p-1]+1

            if board_layers[l,0,1].get_state()==p:
                if board_layers[l,0,2].get_state()==p:
                    mills[p-1] = mills[p-1]+1

        p = board_layers[l,2,2].get_state()

        if not p == 0:
            if board_layers[l, 2, 1].get_state() == p:
                if board_layers[l, 2, 0].get_state() == p:
                    mills[p - 1] = mills[p - 1] + 1

            if board_layers[l, 1, 2].get_state() == p:
                if board_layers[l, 0, 2].get_state() == p:
                    mills[p - 1] = mills[p - 1] + 1
    for x in mill_board_layers:
        if not x == -1:
            mills[x-1] = mills[x-1]+1

    # print('Mills current player: ' + str(mills[turn-1]) + ', mills opponent: ' + str(mills[not_turn()-1]))
    return mills

# This is Mills current, Mills opponent, Blocked current, Blocked opponent, Number of pieces current, Number of pieces opponent, Won?


def count_player(player, board_layers):
    counter = 0

    for l in board_layers:
        for x in l:
            for p in x:
                if p:
                    if p.get_state()==player:
                        counter = counter + 1

    return counter


def evaluation(board_layers):
    # Eval for: New Mills For Current, Removed Mills for Opponent
    eval_values = [31, 14, 10, 11, 1086]

    stats = [0, 0, 0, 0, 0, 0, 0]
    stats[0], stats[1] = count_mills(board_layers)
    stats[2], stats[3] = check_for_blocked(board_layers)
    stats[4] = count_player(turn, board_layers)
    stats[5] = count_player(not_turn(), board_layers)

    if stats[5] < 3:
        stats[6] = 1
    if stats[4] < 3:
        stats[6] = -1

    score = 0

    if stats[0] > current_stats[0]:
        score = score + eval_values[0]
    if stats[1] < current_stats[1]:
        score = score + eval_values[1]

    score = score + (eval_values[2]*(stats[2]-stats[3]))
    score = score + (eval_values[3]*(stats[4]-stats[5]))
    score = score + (stats[6]*eval_values[4])

    return stats, score


def AI_control():
    root = TreeBranch(None)
    root.set_root()

    # Tutaj ta 3 to głębokość :)
    finals = check_moves([root], 3)

    # TUTAJ KOD DO ALFA-BETA, NIECH ZWRACA GAŁĄŻ Z RUCHEM JAKI NALEŻY PODJĄĆ

    # przykład - to zwraca po prostu pierwszego rodzica z brzegu
    m = finals[0].parent.parent

    # TUTAJ KOD DO ALFA-BETA, NIECH ZWRACA GAŁĄŻ Z RUCHEM JAKI NALEŻY PODJĄĆ

    if 'temp' in m.move:
        t = m.move['temp']
    else:
        t = None
    if m.move['double_exists']:
        d = m.move['double']
    else:
        d = None

    p = m.move['point']

    return p, t, d


def check_moves(parents, depth):
    if depth == 0:
        return parents
    children = []
    for q in parents:
        b = q.get_board()
        ph = q.get_phase()
        if ph == 0:
            for l in b:
                for x in l:
                    for y in x:
                        if y:
                            if y.get_state() == 0:
                                p_l, p_x, p_y = y.get_l_x_y()
                                child = TreeBranch(q)
                                child.heritage()
                                child.set_point(p_l, p_x, p_y)
                                child.determine_board()
                                if child.next['phase'] == 1 and child.next['turn'] == q.get_turn():
                                    for l in b:
                                        for x in l:
                                            for y in x:
                                                if y:
                                                    if y.get_state() == not_turn(q.get_turn()):
                                                        d_l, d_x, d_y = y.get_l_x_y()
                                                        child.determine_double(d_l, d_x, d_y)
                                                        child.determine_stats()
                                                        children.append(child)
                                                        q.add_child(child)
                                else:
                                    child.determine_stats()
                                    children.append(child)
                                    q.add_child(child)
        if ph == 2 or ph == 4:
            for l in b:
                for x in l:
                    for y in x:
                        if y:
                            if y.get_state() == q.get_turn():
                                neighbors = y.get_neighbors()
                                for n in neighbors:
                                    p_l, p_x, p_y = n.get_l_x_y()
                                    if b[p_l, p_x, p_y].get_state() == 0:
                                        t_l, t_x, t_y = y.get_l_x_y()
                                        child = TreeBranch(q)
                                        child.heritage()
                                        child.set_point(p_l, p_x, p_y)
                                        child.set_temp(t_l, t_x, t_y)
                                        child.determine_board()
                                        if child.next['phase'] == 3:
                                            for l in b:
                                                for x in l:
                                                    for y in x:
                                                        if y:
                                                            if y.get_state() == not_turn(q.get_turn()):
                                                                d_l, d_x, d_y = y.get_l_x_y()
                                                                child.determine_double(d_l, d_x, d_y)
                                                                child.determine_stats()
                                                                children.append(child)
                                                                q.add_child(child)
                                        else:
                                            child.determine_stats()
                                            children.append(child)
                                            q.add_child(child)

        if ph == 1:
            for l in b:
                for x in l:
                    for y in x:
                        if y:
                            if y.get_state() == not_turn(q.get_turn()):
                                p_l, p_x, p_y = y.get_l_x_y()
                                child = TreeBranch(q)
                                child.heritage()
                                child.set_point(p_l, p_x, p_y)
                                child.determine_board()
                                child.determine_stats()
                                children.append(child)
                                q.add_child(child)
    return check_moves(children, depth-1)

    

if __name__ == "__main__":
   # pygame.mixer.music.play(-1)
    layers = points_setup()

    running = True
    screen.fill((255, 255, 255))
    screen.blit(background, (0, 0))
    screen.blit(board, (103, 100))
    temp = None
    pygame.display.flip()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.BUTTON_X1:
                print('PHASE: '+str(phase))
                pos = pygame.mouse.get_pos()
                point = which_point(pos)
                print(pawns_count)
                if point:
                    game(point)
                if phase == 6:
                    screen.blit(background, (0, 0))
                    largeText = pygame.font.Font('freesansbold.ttf', 120)
                    TextSurf, TextRect = text_objects('Gracz '+str(win_player) + ' wygrał!', largeText)
                    TextRect.center = (display_width/2+50, display_height/2-100)
                    screen.blit(TextSurf, TextRect)
                    pygame.display.flip()
                if phase == 2 and not check_available_moves(turn, layers):
                    phase = 4
                    switch_turn()
                current_stats, _ = evaluation(layers)
                if turn == 2:
                    p, t, d = AI_control()
                    l, x, y = p.get_l_x_y()
                    point = layers[l, x, y]
                    if t:
                        t_l, t_x, t_y = t.get_l_x_y()
                        temp = layers[t_l, t_x, t_y]
                    game(point)
                    if turn == 2:
                        d_l, d_x, d_y = d.get_l_x_y()
                        double = layers[d_l, d_x, d_y]
                        game(d)
                    if phase == 6:
                        screen.blit(background, (0, 0))
                        largeText = pygame.font.Font('freesansbold.ttf', 120)
                        TextSurf, TextRect = text_objects('Gracz '+str(win_player) + ' wygrał!', largeText)
                        TextRect.center = (display_width/2+50, display_height/2-100)
                        screen.blit(TextSurf, TextRect)
                        pygame.display.flip()
                    if phase == 2 and not check_available_moves(turn, layers):
                        phase = 4
                        switch_turn()

            if event.type == pygame.KEYDOWN:
                game_reset()
            if event.type == pygame.QUIT:
                running = False
