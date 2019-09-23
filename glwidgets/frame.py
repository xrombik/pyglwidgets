#!/usr/bin/env python
# -*- coding: utf-8 -*-

import colors
import gltools

from .glwidget import *
from .glimports import *


class CairoFrame(GlWidget):
    """
    Создаёт рамку с заголовком и разделительными линиями.
    # TODO: Добавить события типа "курсор мыши в рамке", "курсор мыши вне рамки", "нажатие мыши в рамке"
    """
    frame_count = 0

    def __init__(self, pos=(0, 0), width=100, height=100, title=None):
        self.cis = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.cc = cairo.Context(self.cis)
        self.pos = pos
        self.txtr_id = glGenTextures(1)
        self.width, self.height = width, height
        self.dl = glGenLists(1)
        self.color_line = colors.GRIDF[0] / 4, colors.GRIDF[1] / 4, colors.GRIDF[2] / 4, 1.0
        self.color_frame_bk = 0.0, 0.0, 0.0, 0.0
        b, g, r, a = 0.11, 0.1, 0.09, 1.0
        self.color_head_bk = b, g, r, a
        self.color_text = b * 4.0, g * 5.0, r * 5.0, a
        self.header_height = 23
        self.font_name = DEFAULT_FONT_FACE
        self.font_size = DEFAULT_FONT_SIZE
        self.line_width = 3
        CairoFrame.frame_count += 1
        self.title = title
        self.lines = list()
        self.texts = list()
        self.cc.set_font_size(self.font_size)
        self.cc.select_font_face(self.font_name, cairo.FONT_SLANT_NORMAL)
        self.font_extents = self.cc.font_extents()  # fascent, fdescent, fheight, fxadvance, fyadvance
        self._show_text = True

    def set_title(self, title):
        assert type(title) is str, "Должна быть строка"
        self.title = title

    def add_line(self, pos0, pos1):
        self.lines.append((pos0, pos1))

    def add_text(self, pos0, text, col=None):
        # TODO: Делать .split() только здесь
        dy = len(text.split('\n')) * self.font_extents[2]
        if col is None:
            col = self.color_text
        else:
            col = float(col[2]) / 255.0, float(col[1] / 255.0), float(col[0] / 255.0), float(col[3] / 255.0)
        self.texts.append((pos0, text, col))
        return dy

    def show_text(self, val):
        # type: (CairoFrame, bool) -> None
        self._show_text = val

    def redraw(self):
        # Очистка поверхности
        clear_cairo_surface(self.cc)

        # Заливка
        self.cc.rectangle(self.line_width, self.header_height, self.width - self.line_width * 2,
                          self.height - self.header_height - self.line_width)
        self.cc.set_source_rgba(*self.color_frame_bk)
        self.cc.fill()

        # Заливка заголовка
        # pat = cairo.LinearGradient(self.line_width, self.line_width, self.line_width, self.header_height)
        # pat.add_color_stop_rgba(0.1, 0.2, 0.1, 0.1, 1.0)
        # pat.add_color_stop_rgba(0.7, 0.7, 0.7, 0.7, 1.0)
        # hatch = 0
        # self.cc.rectangle(self.line_width + hatch, self.line_width + hatch, self.width - self.line_width * 2 - hatch, self.header_height - self.line_width * 2)
        self.cc.rectangle(self.line_width, self.line_width, self.width - self.line_width * 2,
                          self.header_height - self.line_width * 2 + 4)
        # self.cc.set_source(pat)
        self.cc.set_source_rgba(*self.color_head_bk)
        self.cc.fill()

        # Линии
        self.cc.set_line_width(self.line_width)
        self.cc.move_to(self.line_width, self.line_width)
        self.cc.line_to(self.line_width, self.height - self.line_width)
        self.cc.line_to(self.width - self.line_width, self.height - self.line_width)
        self.cc.line_to(self.width - self.line_width, self.line_width)
        self.cc.line_to(self.line_width, self.line_width)
        self.cc.move_to(self.line_width, self.header_height)
        self.cc.line_to(self.width - self.line_width, self.header_height)
        self.cc.set_source_rgba(*self.color_line)
        self.cc.stroke()

        # Разделительные линии
        for poss in self.lines:
            pos0, pos1 = poss
            self.cc.move_to(pos0[0], pos0[1])
            self.cc.line_to(pos1[0], pos1[1])
            self.cc.stroke()

        xbearing, ybearing, text_width, text_height, xadvance, yadvance = self.cc.text_extents(self.title)

        fheight = self.font_extents[2]
        fdescent = self.font_extents[1]

        # Заголовок
        if self.title:
            self.cc.set_source_rgba(*self.color_text)
            x_pos = (self.width - text_width) / 2.0
            y_pos = self.header_height - (self.header_height - fheight) / 2.0 - fdescent - self.line_width / 2.0
            self.cc.move_to(x_pos, y_pos)
            self.cc.show_text(self.title)

        # Текст
        if self._show_text:
            for pos, txt, col in self.texts:
                txt = txt.split('\n')
                x_pos = pos[0];
                y_pos = pos[1]
                for t in txt:
                    self.cc.set_source_rgba(*col)
                    self.cc.move_to(x_pos, y_pos)
                    self.cc.show_text(t)
                    y_pos += fheight

        # Вывод в текстуру
        txtr = gltools.data_to_texture(self.txtr_id, self.cis.get_data(), self.width, self.height)

        # Вывод в opengl
        glNewList(self.dl, GL_COMPILE)
        gltools.draw_texture(txtr, self.pos)
        glEndList()

    def __del__(self):
        glDeleteLists(self.dl, 1)
        glDeleteTextures([self.txtr_id])
