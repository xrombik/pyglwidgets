#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import glib
import copy

from . import glwidget
from . import fonts
from . import gltools
from . import colors
from . import tools
from .glimports import *
from .driver import safe_connect
from .driver import safe_disconnect

__all__ = ('Entry', )


class Entry(glwidget.GlWidget):
    TICK_RATE = 150
    
    def __init__(self, pos, text=' ', rect_size=(150, 17),
                 font_name=fonts.DEFAULT_FONT_FACE,
                 font_size=fonts.DEFAULT_FONT_SIZE,
                 text_color=colors.ENTRY_TEXT,
                 bg_color=(255, 127, 127, 255)):
        assert type(pos) is tuple
        assert len(pos) == 2
        assert type(rect_size) is tuple
        assert len(rect_size) == 2
        assert type(font_name) is str
        assert type(font_size) is int
        assert len(text_color) == 4
        assert type(bg_color) is tuple
        assert len(bg_color) == 4

        self.text_color = list(text_color)
        self.bg_color = bg_color
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
        glNewList(self.dl, GL_COMPILE)
        # Рамка
        pos = self.pos[0], self.pos[1]
        p0 = pos
        p1 = pos[0] + self.size[0], pos[1]
        p2 = pos[0] + self.size[0], pos[1] + self.size[1]
        p3 = pos[0], pos[1] + self.size[1]
        gltools.draw_lines((p0, p1, p2, p3, p0), self.bg_color, self.line_width)
        pts = p1, p0, p3, p2
        # Подкладка
        gltools.draw_polygon(pts, (0, 0, 0, 240))
        # Введённый текст
        self.font.draw_text((self.pos[0], self.pos[1] + self.size[1] + 2), self.text)
        # Курсор
        if self.timer_id:
            gltools.draw_line((self.cur_pos, self.pos[1] + self.size[1]), (self.cur_pos, self.pos[1]), self.cur_col)
        glEndList()

    def on_timer(self, *_args):
        # Смена фаз курсора
        self.cur_tick += 1
        self.cur_tick %= len(self.cur_colors)
        self.cur_col = self.cur_colors[self.cur_tick]
        self.put_to_redraw()
        return True

    def on_button_press(self, _event, *_args):
        if self.cover:
            self.start_type()
        else:
            self.stop_type()
        self.cur_pos = self.pos[0] + self.font.get_text_width(self.text[:self.cur_index])

    def _motion_notify(self, *args):
        event = args[1]
        self.cover = gltools.check_rect(self.size[0], self.size[1], self.pos, event.x, event.y)
        self.text_color[3] = 100 + 100 * self.cover
        return False

    def _on_key_press(self, _window, event):
        # Сохранить состояние, на случай если изменения будут не допустимыми
        save_text = copy.deepcopy(self.text)
        save_cur_index = self.cur_index
        save_cur_pos = self.cur_pos
        # Преобразовать данные события в распознаваемые константы
        char_code = gtk.gdk.keyval_to_unicode(event.keyval)
        char_name = gtk.gdk.keyval_name(event.keyval)
        cur_shift = 0
        if char_code != 0:
            text_l = list(self.text.decode('utf-8'))
            text_l.insert(self.cur_index, unichr(char_code))
            cur_shift = 1
            self.text = ''
            for c in text_l:
                self.text += c
        if char_name == 'Delete':
            if len(self.text.decode('utf-8')):
                text_l = list(self.text.decode('utf-8'))
                if self.cur_index < len(text_l):
                    text_l.pop(self.cur_index)
                self.text = ''
                for c in text_l:
                    self.text += c
        elif (char_name == 'Return') or (char_name == 'KP_Enter'):
            if self.on_edit_done is not None:
                self.on_edit_done(self)
        elif char_name == 'Left':
            cur_shift = -1
        elif char_name == 'Right':
            cur_shift = 1
        elif char_name == 'BackSpace':
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
        self.pc.append(('ehid2', safe_connect, 'key-press-event', self._on_key_press))
        if self.timer_id is None:
            self.cur_tick = 1
            self.timer_id = glib.timeout_add(Entry.TICK_RATE, self.on_timer)
            self.put_to_redraw()
