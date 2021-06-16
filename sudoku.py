import random
import sys
from copy import deepcopy
import time
from ursina import *
from direct.stdpy import thread


def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == ' ':
                return i, j
    return None


def dfs(board, time_sleep=False):
    if time_sleep:
        time.sleep(0.1)
    found = find_empty(board)
    if not found:
        return True
    else:
        row, col = find_empty(board)
    if board[row][col] == ' ':
        nums = list(range(1, 10))
        random.shuffle(nums)
        for i in nums:
            if is_valid(row, col, board, i):
                board[row][col] = str(i)
                if dfs(board, time_sleep):
                    return True
                board[row][col] = ' '
    return False


def is_valid(row, col, board, num):
    for i in range(9):
        if (board[i][col] == str(num) and i != row) or (board[row][i] == str(num) and i != col):
            return False

    for i in range(row//3*3, row//3*3+3):
        for j in range(col//3*3, col//3*3+3):
            if board[i][j] == str(num) and (i != row or j != col):
                return False
    return True


def quiz_board(board, count=45):
    board_ = deepcopy(board)
    all_ = [(i, j) for i in range(9) for j in range(9)]
    random_index = random.sample(all_, count)
    for row, col in random_index:
        board_[row][col] = ' '
    return board_


def make_board():
    temp = [[' '] * 9 for _ in range(9)]
    dfs(temp)
    return quiz_board(temp)


class Game(Entity):
    def __init__(self):
        super().__init__()
        quiz = make_board()
        self.auto_mode = False
        self.board = [[Block(
            position=((-4 + col) * 0.8, (4 - row) * 0.8),
            loc=(row, col),
            text=quiz[row][col],
            click_callback=self.click_callback,
            input_callback=self.input_callback)
            for col in range(9)]
                for row in range(9)]

        self.reset_button = Button(
            parent=scene,
            text='Reset ',
            color=color.azure,
            scale=1.5,
            position=(6, 0),
            on_click=self.reset
        )
        self.auto_button = Button(
            parent=scene,
            text='Auto ',
            color=color.azure,
            scale=1.5,
            position=(6, -2),
            on_click=self.auto
        )
        self.vlines = [Entity(
            model='quad',
            color=color.black,
            position=(-3.6+2.4*i, 0),
            scale=(.05, 7.2)) for i in range(4)]

        self.hlines = [Entity(
            model='quad',
            color=color.black,
            position=(0, -3.6+2.4*i),
            scale=(7.2, .05)) for i in range(4)]

        self.num_board = [[self.board[i][j].text for j in range(9)] for i in range(9)]
        self.copy_board = deepcopy(self.num_board)

        self.success = Text('Success!!')
        self.success.x = 0
        self.success.y = 0.05
        self.success.background = True
        self.success.visible = False

    @staticmethod
    def reset():
        scene.clear()
        return Game()

    def update(self):
        if self.auto_mode:
            for i in range(9):
                for j in range(9):
                    self.board[i][j].text = self.copy_board[i][j]
            if self.is_completed():
                self.success.visible = True
                self.auto_mode = False

    def auto(self):
        self.num_board = [[self.board[i][j].text for j in range(9)] for i in range(9)]
        self.copy_board = deepcopy(self.num_board)
        self.auto_mode = True
        thread.start_new_thread(function=dfs, args=(self.copy_board, True))

    def click_callback(self, loc):
        for row in range(9):
            for column in range(9):
                if self.board[row][column].clicked and loc != (row, column):
                    self.board[row][column].clicked = False
                    self.board[row][column].color = color.gray

    def input_callback(self):
        self.num_board = [[self.board[i][j].text for j in range(9)] for i in range(9)]
        for i in range(9):
            for j in range(9):
                if self.num_board[i][j] == ' ':
                    self.board[i][j].text_color = color.white
                    continue
                if not is_valid(i, j, self.num_board, self.num_board[i][j]):
                    self.board[i][j].text_color = color.red
                else:
                    self.board[i][j].text_color = color.white
        if self.is_completed():
            self.success.visible = True

    def is_completed(self):
        for row in range(9):
            for col in range(9):
                if self.board[row][col].text == ' ' or self.board[row][col].text_color == color.red:
                    return False
        return True


class Block(Button):
    def __init__(self, position, loc, text, click_callback, input_callback):
        super().__init__()
        self.parent = scene
        self.model = 'quad'
        self.color = color.gray
        self.position = position
        self.loc = loc
        self.scale = 0.75
        self.clicked = False
        self.text = text
        self.click_callback = click_callback
        self.input_callback = input_callback

    def input(self, key):
        if self.clicked:
            if self.text == key:
                self.color = color.gray
                self.clicked = False
                return
            if key in '123456789':
                self.text = key
                self.input_callback()
                self.color = color.gray
                self.clicked = False

            elif key == '0' or key == 'backspace':
                self.text = ' '
                self.input_callback()
                self.color = color.gray
                self.clicked = False

    def on_click(self):
        self.click_callback(self.loc)
        if not self.clicked:
            self.clicked = True
            self.color = color.dark_gray
        else:
            self.clicked = False
            self.color = color.gray


if __name__ == '__main__':
    window.title = 'sudoku'
    window.borderless = False
    app = Ursina()
    game = Game()
    app.run()
