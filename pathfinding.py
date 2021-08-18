from queue import PriorityQueue
import pygame
import math
import sys
import colors as COLOR

WIDTH, HEIGHT = 800, 800
ROWS = 50

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pathfinding Visualization")


class Node:
    def __init__(self, row, col, size, total_rows):
        self.row = row
        self.col = col
        self.size = size
        self.total_rows = total_rows

        self.x = row * size
        self.y = col * size
        self.color = COLOR.WHITE
        self.neighbors = []

    def get_pos(self):
        return self.row, self.col

# STATE ????

    def is_closed(self):
        return self.color == COLOR.RED

    def is_open(self):
        return self.color == COLOR.GREEN

    def is_barrier(self):
        return self.color == COLOR.BLACK

    def is_start(self):
        return self.color == COLOR.ORANGE

    def is_end(self):
        return self.color == COLOR.TURQUOISE

    def reset(self):
        self.color = COLOR.WHITE

    def set_start(self):
        self.color = COLOR.ORANGE

    def set_closed(self):
        self.color = COLOR.RED

    def set_open(self):
        self.color = COLOR.GREEN

    def set_barrier(self):
        self.color = COLOR.BLACK

    def set_target(self):
        self.color = COLOR.TURQUOISE

    def set_path(self):
        self.color = COLOR.PURPLE

    def draw(self, win):
        pygame.draw.rect(
            win, self.color, (self.x, self.y, self.size, self.size))

    def update_neighbors(self, grid):
        self.neighbors = []
        # DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])

        # UP
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])

        # RIGHT
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])

        # LEFT
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


def calculate_manhattan_distance(p1, p2):
    return sum(abs(val1-val2) for val1, val2 in zip(p1, p2))


def make_grid(rows, width):
    grid = []
    size = width // rows

    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, size, rows)
            grid[i].append(node)

    return grid


# check this
def draw_grid(win, rows, width):
    size = width // rows
    for i in range(rows):
        pygame.draw.line(win, COLOR.GREY, (0, i * size), (width, i * size))
        for j in range(rows):
            pygame.draw.line(win, COLOR.GREY, (j * size, 0), (j * size, width))


def draw(win, grid, rows, width):
    win.fill(COLOR.WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    size = width // rows
    y, x = pos

    row = y // size
    col = x // size

    return row, col


def reconstruct_path(path, current, draw):
    while current in path:
        current = path[current]
        current.set_path()
        draw()


def a_star_algorithm(draw, grid, start, target):
    count = 0
    open_set = PriorityQueue()
    # start node with f score
    open_set.put((0, count, start))
    path = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = calculate_manhattan_distance(
        start.get_pos(), target.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == target:
            reconstruct_path(path, target, draw)
            target.set_target()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                path[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + \
                    calculate_manhattan_distance(
                        neighbor.get_pos(), target.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.set_open()

        draw()

        if current != start:
            current.set_closed()

    return False


def main():
    grid = make_grid(ROWS, WIDTH)

    start_pos = None
    target_pos = None

    run = True
    # started = False

    while run:
        draw(WIN, grid, ROWS, WIDTH)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # if started:
            #     continue

            if pygame.mouse.get_pressed()[0]:  # LEFT MOUSE BUTTON
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, WIDTH)
                node = grid[row][col]
                if not start_pos and node != target_pos:
                    start_pos = node
                    start_pos.set_start()

                elif not target_pos and node != start_pos:
                    target_pos = node
                    target_pos.set_target()

                elif node != target_pos and node != start_pos:
                    node.set_barrier()

            elif pygame.mouse.get_pressed()[2]:  # RIGHT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, WIDTH)
                node = grid[row][col]
                node.reset()
                if node == start_pos:
                    start_pos = None
                elif node == target_pos:
                    target_pos = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start_pos and target_pos:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    a_star_algorithm(lambda: draw(WIN, grid, ROWS, WIDTH),
                                     grid, start_pos, target_pos)

                if event.key == pygame.K_c or event.key == pygame.K_BACKSPACE:
                    start_pos = None
                    target_pos = None
                    grid = make_grid(ROWS, WIDTH)

    pygame.quit()


if __name__ == "__main__":
    main()
