import pygame
import numpy as np
import math

pygame.init()

pygame.display.set_caption("minimal program")

screen = pygame.display.set_mode((1024, 900))

pawn_w = pygame.image.load("white_ball.png")
pawn_w.set_alpha(None)
pawn_w.set_colorkey((200, 250, 200))
pawn_b = pygame.image.load("black_ball.png")
pawn_b.set_alpha(None)
pawn_b.set_colorkey((200, 250, 200))
background = pygame.image.load("bgd.png")
board = pygame.image.load("board.png")

pygame.display.set_icon(pawn_w)


class Point:

    def __init__(self, layer, x, y):
        self.x = x
        self.y = y
        self.layer = layer
        self.pos_x, self.pos_y = get_point_position(layer, x, y)
        self.state = 0
        self.neighbors = []

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


layers = np.empty((3, 3, 3), dtype=Point)


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
    pos_x, pos_y = point.get_position()
    if white == 1:
        point.change_state(1)
        screen.blit(pawn_w, (pos_x, pos_y))
    else:
        point.change_state(2)
        screen.blit(pawn_b, (pos_x, pos_y))


def redraw_board():
    screen.blit(background, (0, 0))
    screen.blit(board, (103, 100))
    for l in layers:
        for x in l:
            for p in x:
                if p:
                    if not p.get_state() == 0:
                        draw_on_point(p, p.get_state())
    pygame.display.flip()


def clear_screen():
    screen.blit(background, (0, 0))
    screen.blit(board, (103, 100))
    pygame.display.flip()


def switch_position(p1, p2):
    color = p1.get_state()
    p1.change_state(0)
    p2.change_state(color)
    redraw_board()


def remove_piece(p):
    p.change_state(0)
    redraw_board()


if __name__ == "__main__":
    layers = points_setup()
    running = True
    screen.fill((255, 255, 255))
    screen.blit(background, (0, 0))
    screen.blit(board, (103, 100))
    x = 1
    temp = None
    pygame.display.flip()
    # main loop
    while running:
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            if event.type == pygame.BUTTON_X1:
                pos = pygame.mouse.get_pos()
                point = which_point(pos)
                if point:
                    if x < 3:
                        draw_on_point(point, x)
                        pygame.display.flip()
                        x = x+1
                    else:
                        if point.get_state() > 0:
                            temp = point
                        else:
                            if point.is_neighbor(temp):
                                switch_position(temp, point)
                                temp = None

            if event.type == pygame.KEYDOWN:
                clear_screen()

            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
