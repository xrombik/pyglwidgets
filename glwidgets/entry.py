#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import glib
import copy

from glwidgets import nevents
from . import kbkeys
from . import glwidget
from . import fonts
from . import gltools
from . import colors
from . import tools
from . nevents import *
from .glimports import *
from .driver import safe_connect
from .driver import safe_disconnect
from .driver import map_keyval

__all__ = ('Entry', )


class Entry(glwidget.GlWidget):
    TICK_RATE = 150
    
    def __init__(self, pos, text=' ', rect_size=(150, 17),
                 font_name=fonts.DEFAULT_FONT_FACE,
                 font_size=fonts.DEFAULT_FONT_SIZE,
                 text_color=colors.ENTRY_TEXT,
                 bg_color=colors.GRAY):
        assert type(pos) is tuple
        assert len(pos) == 2
        assert type(rect_size) is tuple
        assert len(rect_size) == 2
        assert type(font_name) is str
        assert type(font_size) is int
        assert len(text_color) == 4
        assert isinstance(bg_color, (tuple, list))
        assert len(bg_color) == 4

        self.text_color = list(text_color)
        self.alphas = (self.text_color[3] - self.text_color[3] / 5, self.text_color[3])
        self.bg_color = list(bg_color)
        self.font = fonts.CairoFont(font_name, font_size)
        self.pos = pos
        self.size = rect_size
        self.text = text.encode('utf-8')
        self.ehid0 = None
        self.ehid1 = None
        self.ehid2 = None
        self.timer_id = None
        self.connect()
        self.cover = False
        self.cur_index = 0
        self.cur_tick = 0
        self.cur_pos = self.pos[0]
        self.cur_colors = ((255, 255, 255, 0), (255, 255, 255, 255))
        self.cur_col = self.cur_colors[self.cur_tick]
        self.on_edit_done = None
        self.user_data = None
        self.line_width = 2

    def redraw(self):
        x = self.pos[0]
        y = self.pos[1]
        p1 = x + self.size[0], y
        p2 = x + self.size[0], y + self.size[1]
        p3 = x, y + self.size[1]
        pts = p1, self.pos, p3, p2

        glNewList(self.dl, GL_COMPILE)
        # Подкладка
        gltools.draw_polygon(pts, colors.BLACK255)

        # Рамка
        gltools.draw_lines((self.pos, p1, p2, p3, self.pos), self.bg_color, self.line_width)
        # Введённый текст
        self.font.draw_text((x, y - self.line_width), self.text, self.text_color)
        # Курсор
        if self.timer_id:
            gltools.draw_lines(((self.cur_pos, y + self.size[1]), (self.cur_pos, y)), self.cur_col)
        glEndList()

    def on_timer(self, *_args):
        # Смена фаз курсора
        self.cur_tick += 1
        self.cur_tick %= len(self.cur_colors)
        self.cur_col = self.cur_colors[self.cur_tick]
        self.put_to_redraw()
        return True

    def on_button_press(self, _event, *_args):
        self.start_type() if self.cover else self.stop_type()
        self.cur_pos = self.pos[0] + self.font.get_text_width(self.text[:self.cur_index])

    def _motion_notify(self, gda, event):
        cover = gltools.check_rect(self.size[0], self.size[1], self.pos, event.x, event.y)
        if self.cover != cover:
            self.text_color[3] = self.alphas[cover]
            self.cover = cover
            self.put_to_redraw()
        return False

    def _on_key_press(self, _window, event):
        # Сохранить состояние, на случай если изменения будут не допустимыми
        save_text = copy.deepcopy(self.text)
        save_cur_index = self.cur_index
        save_cur_pos = self.cur_pos
        char_code, char_name = map_keyval(event.keyval)
        cur_shift = 0
        if char_code != 0:
            text_l = list(self.text.decode('utf-8'))
            text_l.insert(self.cur_index, unichr(char_code))
            cur_shift = 1
            self.text = ''
            for c in text_l:
                self.text += c
        if char_name == kbkeys.DELETE:
            if len(self.text.decode('utf-8')):
                text_l = list(self.text.decode('utf-8'))
                if self.cur_index < len(text_l):
                    text_l.pop(self.cur_index)
                self.text = ''
                for c in text_l:
                    self.text += c
        elif (char_name == kbkeys.RETURN) or (char_name == kbkeys.KPENTER):
            if self.on_edit_done is not None:
                self.on_edit_done(self)
        elif char_name == kbkeys.LEFT:
            cur_shift = -1
        elif char_name == kbkeys.RIGHT:
            cur_shift = 1
        elif char_name == kbkeys.BACKSPACE:
            if len(self.text.decode('utf-8')):
                text_l = list(self.text.decode('utf-8'))
                if self.cur_index > 0:
                    text_l.pop(self.cur_index - 1)
                self.text = ''
                for c in text_l:
                    self.text += c
                cur_shift = -1
        self.cur_index += cur_shift
        if self.cur_index < 0:
            self.cur_index = 0
        if len(self.text) > 0:
            max_index = len(self.text.decode('utf-8'))
            if self.cur_index > max_index:
                self.cur_index = max_index
        if len(self.text) == 0:
            self.cur_index = 0
        s0 = tools.str_cut(self.text, self.cur_index)
        self.cur_pos = self.pos[0] + self.font.get_text_width(s0)
        text_right_x = self.pos[0] + self.font.get_text_width(self.text)
        if (text_right_x >= self.pos[0] + self.size[0]) and (char_code != 0):
            self.text = save_text
            self.cur_index = save_cur_index
            self.cur_pos = save_cur_pos
        self.put_to_redraw()
        return True

    def connect(self):
        self.pc.append(('ehid0', safe_connect, 'motion-notify-event', self._motion_notify))
        self.pc.append(('ehid1', safe_connect, 'button-press-event', self.on_button_press))
        self.cur_pos = self.pos[0]
        self.cur_index = 0

    def disconnect(self):
        self.cover = False
        self.pc.append(('ehid0', safe_disconnect))
        self.pc.append(('ehid1', safe_disconnect))
        self.pc.append(('ehid2', safe_disconnect))

    def stop_type(self):
        self.pc.append(('ehid2', safe_disconnect))
        if self.timer_id is not None:
            glib.source_remove(self.timer_id)
            self.timer_id = None
            self.cur_tick = 0
            self.put_to_redraw()

    def start_type(self):
        self.pc.append(('ehid2', safe_connect, nevents.EVENT_KEY_PRESS, self._on_key_press))
        if self.timer_id is None:
            self.cur_tick = 1
            self.timer_id = glib.timeout_add(Entry.TICK_RATE, self.on_timer)
            self.put_to_redraw()
