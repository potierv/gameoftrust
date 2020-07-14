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
        board_bg_color = 'bisque'
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
        self.feed_mutex.acquire()
        events = self.feed_list
        self.feed_list = []
        self.feed_mutex.release()
        for type, state in events:
            if type is GameOfTrustUI.EventType.START:
                pass
            elif type is GameOfTrustUI.EventType.STOP:
                self.time.grid(row=1, column=0)
                self.time.timeline['to'] = len(self.states)
                self.set_timeline(len(self.states))
            elif type is GameOfTrustUI.EventType.STATE:
                self.states.append(state)
        self.time.timeline['length'] = self.parent.winfo_width() - self.time.buttons.winfo_width() - 8
        self.current_index = max(0, len(self.states) - 1)
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

        menubar = tk.Menu(self.parent)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='Quit', command=self.parent.quit)
        menubar.add_cascade(label='File', menu=filemenu)
        self.parent.config(menu=menubar)

        self.boardinfo = tk.Frame(self.parent)
        self.boardinfo.grid(row=0, column=0)
        self.boardinfo.inspector = tk.Frame(self.boardinfo)
        self.boardinfo.inspector.grid(row=0, column=0)
        self.boardinfo.view = tk.Frame(self.boardinfo)
        self.boardinfo.view.grid(row=0, column=1)
        self.boardinfo.view.board = tk.Canvas(self.boardinfo.view, width=0, height=0,bg=self.style.board_bg_color)
        self.boardinfo.view.board.grid(row=0, column=0)
        self.boardinfo.view.board.cells = []
        self.boardinfo.view.status = tk.Frame(self.boardinfo.view)
        self.boardinfo.view.status.grid(row=1, column=0)
        tk.Button(self.boardinfo.view.status, text='-', command=self.zoom_out).grid(row=0, column=0)
        tk.Button(self.boardinfo.view.status, text='+', command=self.zoom_in).grid(row=0, column=1)
        self.time = tk.Frame(self.parent)
        self.time.buttons = tk.Frame(self.time)
        tk.Button(self.time.buttons, text='|<', command=self.jump_to_first).grid(row=0, column=0)
        tk.Button(self.time.buttons, text='<|', command=self.prev_state).grid(row=0, column=1)
        tk.Button(self.time.buttons, text='>', command=self.play_pause).grid(row=0, column=2)
        tk.Button(self.time.buttons, text='|>', command=self.next_state).grid(row=0, column=3)
        tk.Button(self.time.buttons, text='>|', command=self.jump_to_last).grid(row=0, column=4)
        self.time.buttons.grid(row=0, column=0)
        self.time.timeline = tk.Scale(self.time, from_=1, to=1, orient=tk.HORIZONTAL, command=self.set_timeline)
        self.time.timeline.grid(row=0, column=1)

    def jump_to_first(self):
        self.set_timeline(1)

    def prev_state(self):
        self.set_timeline(self.current_index) # because set_timeline index is 1-based

    def play_pause(self):
        pass

    def next_state(self):
        self.set_timeline(self.current_index + 2) # because set_timeline index is 1-based

    def jump_to_last(self):
        self.set_timeline(len(self.states))

    def set_timeline(self, index):
        self.current_index = max(1, min(len(self.states), int(index))) - 1
        self.time.timeline.set(self.current_index + 1) # it's fine, Scale internal checks prevent from infinite recursion
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
        for cell in self.boardinfo.view.board.cells:
            self.boardinfo.view.board.delete(cell)
        self.boardinfo.view.board.cells = []

    def set_grid(self, cells):
        cell_width = self.style.cell_width * self.zoom
        cell_height = self.style.cell_height * self.zoom
        cell_padding_x = self.style.cell_padding_x * self.zoom
        cell_padding_y = self.style.cell_padding_y * self.zoom

        self.clear_grid()

        board_width = self.parent.winfo_width() - self.boardinfo.inspector.winfo_width()
        board_height = self.parent.winfo_height() - self.boardinfo.view.status.winfo_height() - max(42, self.time.winfo_height()) - 8
        self.boardinfo.view.board.config(width=board_width, height=board_height)

        for row in range(len(cells)):
            for col in range(len(cells[row])):
                top = row * (cell_height + cell_padding_x)
                left = col * (cell_width + cell_padding_y)
                bottom = top + cell_height
                right = left + cell_width
                fill = self.style.cell_fill_color[cells[row][col]]
                rect = self.boardinfo.view.board.create_rectangle(left,
                                                               top,
                                                               right,
                                                               bottom,
                                                               outline=self.style.cell_border_color,
                                                               fill=fill)
                self.boardinfo.view.board.cells.append(rect)

if __name__ == '__main__':
    root = tk.Tk()
    ui = GameOfTrustUI(root)
    io = IOJob(ui)
    io.start()
    root.mainloop()
    io.join()
