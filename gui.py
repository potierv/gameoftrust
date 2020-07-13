#!/usr/bin/env python3

import json
import sys
import tkinter as tk
from threading import Thread, Lock
from dataclasses import dataclass
from enum import Enum, auto

class IOJob(Thread):

    def __init__(self, ui):
        Thread.__init__(self)
        self.ui = ui

    def run(self):
        self.ui.start_reading_input()
        for line in sys.stdin:
            self.ui.feed(line)
        self.ui.stop_reading_input()

class GameOfTrustUI(tk.Frame):

    # http://www.science.smith.edu/dftwiki/index.php/File:TkInterColorCharts.png
    class Style:
        board_color = 'bisque'
        board_margin_x = 5
        board_margin_y = 5
        cell_width = 20
        cell_height = 20
        cell_padding_x = 3
        cell_padding_y = 3
        cell_border_color = 'LavenderBlush4'
        cell_fill_color = {
            '-' : 'snow',
            'X' : 'IndianRed2',
            '0' : 'chartreuse',
        }

    class EventType(Enum):
        START = auto()
        STOP = auto()
        STATE = auto()

    @dataclass
    class State:
        round: int
        map: list

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.style = GameOfTrustUI.Style()
        self.zoom = 1.0
        self.current_index = 0
        self.states = []
        self.init_ui()
        self.feed_mutex = Lock()
        self.feed_list = []
        self.my_tick()

    def my_tick(self):
        refresh = False
        self.feed_mutex.acquire()
        events = self.feed_list
        self.feed_list = []
        self.feed_mutex.release()
        for type, state in events:
            if type is GameOfTrustUI.EventType.START:
                pass
            elif type is GameOfTrustUI.EventType.STOP:
                self.main.toolbox.timeline['to'] = len(self.states)
                self.main.toolbox.timeline.set(len(self.states))
                self.main.toolbox.timeline.grid(row=0, column=0)
            elif type is GameOfTrustUI.EventType.STATE:
                refresh = True
                self.states.append(state)
        if refresh:
            self.current_index = len(self.states) - 1
            self.refresh_grid()
        self.after(16, self.my_tick)

    def start_reading_input(self):
        self.feed_mutex.acquire()
        self.feed_list.append((GameOfTrustUI.EventType.START, None))
        self.feed_mutex.release()

    def stop_reading_input(self):
        self.feed_mutex.acquire()
        self.feed_list.append((GameOfTrustUI.EventType.STOP, None))
        self.feed_mutex.release()

    def feed(self, line):
        obj = json.loads(line.strip())
        state = GameOfTrustUI.State(obj['round'], obj['map'])
        self.feed_mutex.acquire()
        self.feed_list.append((GameOfTrustUI.EventType.STATE, state))
        self.feed_mutex.release()

    def init_ui(self):
        self.parent.title('Game of Trust')
        self.main = tk.Frame(self.parent)
        self.main.grid(row=0, column=0)
        self.main.toolbox = tk.Frame(self.main)
        self.main.toolbox.grid(row=0, column=0, sticky=tk.W)
        self.main.toolbox.timeline = tk.Scale(self.main.toolbox, from_=1, to=1, orient=tk.HORIZONTAL, command=self.set_timeline)

        self.main.toolbox.zoom_buttons = tk.Frame(self.main.toolbox)
        self.main.toolbox.zoom_buttons.grid(row=0, column=2)
        tk.Button(self.main.toolbox.zoom_buttons, text='-', command=self.zoom_out).grid(row=0, column=0)
        tk.Button(self.main.toolbox.zoom_buttons, text='+', command=self.zoom_in).grid(row=0, column=1)

        self.main.board = tk.Canvas(self.main, width=0, height=0,bg=self.style.board_color)
        self.main.board.grid(row=1, column=0, sticky=tk.W)
        self.main.board.cells = []

    def set_timeline(self, index):
        self.current_index = int(index) - 1
        self.refresh_grid()

    def zoom_out(self):
        self.zoom = max(0.2, self.zoom * 0.9)
        self.refresh_grid()
        
    def zoom_in(self):
        self.zoom = min(3, self.zoom * 1.1)
        self.refresh_grid()

    def refresh_grid(self):
        if len(self.states) != 0:
            self.set_grid(self.states[self.current_index].map)
        
    def clear_grid(self):
        for cell in self.main.board.cells:
            self.main.board.delete(cell)
        self.main.board.cells = []

    def set_grid(self, cells):
        cell_width = self.style.cell_width * self.zoom
        cell_height = self.style.cell_height * self.zoom
        cell_padding_x = self.style.cell_padding_x * self.zoom
        cell_padding_y = self.style.cell_padding_y * self.zoom
        board_margin_x = self.style.board_margin_x * self.zoom
        board_margin_y = self.style.board_margin_y * self.zoom

        self.clear_grid()

        board_width = cell_width * len(cells[0]) + cell_padding_x * (len(cells[0]) - 1) + board_margin_x * 2
        board_height = cell_height * len(cells) + cell_padding_y * (len(cells) - 1) + board_margin_y * 2
        self.main.board.config(width=board_width, height=board_height)

        for row in range(len(cells)):
            for col in range(len(cells[row])):
                top = row * (cell_height + cell_padding_x) + board_margin_x
                left = col * (cell_width + cell_padding_y) + board_margin_y
                bottom = top + cell_height
                right = left + cell_width
                fill = self.style.cell_fill_color[cells[row][col]]
                rect = self.main.board.create_rectangle(left,
                                                        top,
                                                        right,
                                                        bottom,
                                                        outline=self.style.cell_border_color,
                                                        fill=fill)
                self.main.board.cells.append(rect)

if __name__ == '__main__':
    root = tk.Tk()
    ui = GameOfTrustUI(root)
    io = IOJob(ui)
    io.start()
    root.mainloop()
    io.join()
