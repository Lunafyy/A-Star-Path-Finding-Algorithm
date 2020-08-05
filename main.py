import pygame
import math
import time

from queue import PriorityQueue

class Colour:
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 255, 0)
    PINK = (255, 0, 255)
    YELLOW = (255, 255, 0)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    PURPLE = (128, 0, 128)
    ORANGE = (255, 165 ,0)
    GREY = (128, 128, 128)
    TURQUOISE = (64, 224, 208)
    

class PathFinding(object):
    def __init__(self, DIMENSIONS: tuple):
        self.DIMENSIONS = DIMENSIONS
        self.X = self.DIMENSIONS[0]
        self.Y = self.DIMENSIONS[1]
        
        self.timestart = None
        self.timeend = None

        self.SETUP_WINDOW()

        self.MAIN(self.WINDOW, self.X)

    def SETUP_WINDOW(self):
        self.WINDOW = pygame.display.set_mode(self.DIMENSIONS)
        pygame.display.set_caption("A* Pathfinding Algorithm Visualizer by CJ")

    def CREATE_GRID(self, ROWS, WIDTH):
        GRID = []
        GAP = WIDTH // ROWS
        for x in range(ROWS):
            GRID.append([])
            for y in range(ROWS):
                node = Node(x, y, GAP, ROWS)
                GRID[x].append(node)

        return GRID

    def DRAW_GRID(self, WIN, ROWS, WIDTH):
        GAP = WIDTH // ROWS
        for X in range(ROWS):
            pygame.draw.line(WIN, Colour.BLACK, (0, X*GAP), (WIDTH, X*GAP))
            for Y in range(ROWS):
                pygame.draw.line(WIN, Colour.BLACK, (Y*GAP, 0), (Y*GAP, WIDTH))

    def DRAW(self, WIN, GRID, ROWS, WIDTH):
        WIN.fill(Colour.WHITE)

        for X in GRID:
            for NODE in X:
                NODE.DRAW(WIN)

        self.DRAW_GRID(WIN, ROWS, WIDTH)
        pygame.display.update()

    def GET_CLICKED_POSITION(self, POS, ROWS, WIDTH):
        GAP = WIDTH // ROWS
        Y, X = POS

        ROW = Y // GAP
        COL = X // GAP

        return ROW, COL

    def MAIN(self, WIN, WIDTH):
        ROWS = 50
        GRID = self.CREATE_GRID(ROWS, WIDTH)

        START_POS = None
        END_POS = None

        RUN = True
        STARTED = False

        while RUN:
            self.DRAW(WIN, GRID, ROWS, WIDTH)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    RUN = False

                if STARTED:
                    continue
                
                if pygame.mouse.get_pressed()[0]:
                    POS = pygame.mouse.get_pos()
                    ROW, COL = self.GET_CLICKED_POSITION(POS, ROWS, WIDTH)
                    NODE = GRID[ROW][COL]

                    if not START_POS:
                        if NODE != END_POS:
                            START_POS = NODE
                            START_POS.SET_STARTING()

                    elif not END_POS:
                        if NODE != START_POS:
                            END_POS = NODE
                            END_POS.SET_ENDING()

                    elif NODE != END_POS and NODE != START_POS:
                        NODE.SET_BARRIER()

                elif pygame.mouse.get_pressed()[2]:
                    POS = pygame.mouse.get_pos()
                    ROW, COL = self.GET_CLICKED_POSITION(POS, ROWS, WIDTH)
                    NODE = GRID[ROW][COL]

                    if NODE == START_POS:
                        START_POS = None
                    elif NODE == END_POS:
                        END_POS = None
                    elif NODE.COLOUR != Colour.WHITE:
                        NODE.RESET()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not STARTED:
                        for ROW in GRID:
                            for NODE in ROW:
                                NODE.UPDATE_SURROUNDING(GRID)
                        self.timestart = time.time()
                        self.ALGORITHM(lambda: self.DRAW(WIN, GRID, ROWS, WIDTH), GRID, START_POS, END_POS)
                        print("That took " + str(int(self.timeend-self.timestart)) + "s")
        pygame.quit()

    def DISPLAY_PATH(self, C_F, END_POS, DRAW):
        blocks = 0
        while END_POS in C_F:
            blocks += 1
            END_POS = C_F[END_POS]
            END_POS.SET_PATH()
            DRAW()
        print("STEPS : " + str(blocks))

    def HEURISTIC(self, X, Y):
        X1, Y1 = X
        X2, Y2 = Y
        return abs(X1-X2) + abs(Y1-Y2)

    def ALGORITHM(self, DRAW, GRID, START_POS, END_POS):
        COUNTER = 0
        O_S = PriorityQueue()
        O_S.put((0, COUNTER, START_POS))
        C_F = {}
        G_SCORE = {NODE: float("inf") for ROW in GRID for NODE in ROW}
        G_SCORE[START_POS] = 0
        F_SCORE = {NODE: float("inf") for ROW in GRID for NODE in ROW}
        F_SCORE[START_POS] = self.HEURISTIC(START_POS.LOCATION, END_POS.LOCATION)

        O_S_H = {START_POS}

        while not O_S.empty():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
            
            CURRENT = O_S.get()[2]
            O_S_H.remove(CURRENT)

            if CURRENT == END_POS:
                self.timeend = time.time()

                self.DISPLAY_PATH(C_F, END_POS, DRAW)
                return True
            
            for SURROUNDER in CURRENT.SURROUNDING:
                TEMP_G_SCORE = G_SCORE[CURRENT] + 1

                if TEMP_G_SCORE < G_SCORE[SURROUNDER]:
                    C_F[SURROUNDER] = CURRENT
                    G_SCORE[SURROUNDER] = TEMP_G_SCORE
                    F_SCORE[SURROUNDER] = TEMP_G_SCORE + self.HEURISTIC(SURROUNDER.LOCATION, END_POS.LOCATION)
                    if SURROUNDER not in O_S_H:
                        COUNTER += 1
                        O_S.put((F_SCORE[SURROUNDER], COUNTER, SURROUNDER))
                        O_S_H.add(SURROUNDER)
                        SURROUNDER.SET_OPEN()
            
            DRAW()
            if CURRENT != START_POS:
                CURRENT.SET_CLOSED()
        self.timeend = time.time()
        return False


class Node(object):
    def __init__(self, ROW: int, COL: int, WIDTH: int, ROWS: int):
        self.X = ROW * WIDTH
        self.Y = COL * WIDTH
        self.ROW = ROW
        self.COL = COL
        self.ROWS = ROWS
        self.WIDTH = WIDTH
        self.MY_COLOUR = Colour.WHITE
        self.SURROUNDING = []

    def __str__(self):
        return f"A {self.COLOUR.title()} Node at {self.MY_LOCATION} with the dimensions {self.MY_DIMENSIONS}"
    
    @property
    def COLOUR(self):
        return self.MY_COLOUR
    @property
    def LOCATION(self):
        return self.X, self.Y
    @property
    def OPEN(self):
        return self.MY_COLOUR == Colour.GREEN
    @property
    def CLOSED(self):
        return self.MY_COLOUR == Colour.RED
    @property
    def BARRIER(self):
        return self.MY_COLOUR == Colour.BLACK
    @property
    def STARTING_NODE(self):
        return self.MY_COLOUR == Colour.ORANGE
    @property
    def ENDING_NODE(self):
        return self.MY_COLOUR == Colour.BLUE
    @property
    def PATH(self):
        return self.MY_COLOUR == Colour.PINK
    

    def SET_OPEN(self):
        self.MY_COLOUR = Colour.GREEN
    def SET_CLOSED(self):
        self.MY_COLOUR = Colour.RED
    def SET_BARRIER(self):
        self.MY_COLOUR = Colour.BLACK
    def SET_STARTING(self):
        self.MY_COLOUR = Colour.ORANGE
    def SET_ENDING(self):
        self.MY_COLOUR = Colour.BLUE
    def SET_PATH(self):
        self.MY_COLOUR = Colour.PINK

    def DRAW(self, WIN):
        pygame.draw.rect(WIN, self.COLOUR, (self.X, self.Y, self.WIDTH, self.WIDTH))
    def UPDATE_SURROUNDING(self, GRID):
        self.SURROUNDING.clear()
        if self.ROW < self.ROWS-1 and not GRID[self.ROW+1][self.COL].BARRIER:
            self.SURROUNDING.append(GRID[self.ROW+1][self.COL])

        if self.ROW > 0 and not GRID[self.ROW-1][self.COL].BARRIER:
            self.SURROUNDING.append(GRID[self.ROW-1][self.COL])

        if self.COL < self.ROWS-1 and not GRID[self.ROW][self.COL+1].BARRIER:
            self.SURROUNDING.append(GRID[self.ROW][self.COL+1])

        if self.COL > 0 and not GRID[self.ROW][self.COL-1].BARRIER:
            self.SURROUNDING.append(GRID[self.ROW][self.COL-1])
    def RESET(self):
        self.MY_COLOUR = Colour.WHITE
        return True

    def __lt__(self, other):
        return False

if __name__ == "__main__":
    x = PathFinding((800, 800))
    # v = Node((50, 50), (10,10), 100, Colour.RED)