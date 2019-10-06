#!/usr/bin/env python
# -*- coding: utf-8 -*-


from . import glwidget
from . import colors
from . import fonts
from .glimports import *


class DynamicText(glwidget.GlWidget):
    """
    Выводит текст на экран. Использовать для часто изменяющихся надписей,
    т.к. работает намного быстрее чем StaticText, и не создаёт текстуры.
    Текст может	содержать перевод строки, что будет учитываться при отображении.
    """

    def __init__(self, font, pos=(0, 0), text=u'', color=colors.WHITE):
        # Санитарная проверка входных параметров
        assert type(font) is fonts.FreeTypeFont, "Должен быть шрифт FreeTypeFont"
        assert (type(text) is unicode) or (type(text) is str), "Должна быть строка, т.е. text=u\'123\'"
        assert (type(pos) is list) or (type(pos) is tuple), "Должен быть список или кортеж"
        assert len(pos) == 2, "Должно быть две координаты X и Y"
        assert type(pos[0]) is int, "Координата X. Должно быть целое"
        assert type(pos[1]) is int, "Координата Y. Должно быть целое"
        assert (type(color) is list) or (type(color) is tuple), "Должен быть список или кортеж"
        assert len(color) == 4, "Должно быть 4 компонента цвета"
        for col in color:
            assert type(col) is int, "Значение компонента цвета. Должны быть целым"
            assert 0 <= col <= 255, "Диапазон значений компонента цвета"
        viewport = glGetIntegerv(GL_VIEWPORT)

        self.pos = pos
        self.parent_height = viewport[3]
        self.lines = list()
        self.font = font
        self.color = color
        self._text_to_lines(text)

    def _text_to_lines(self, text):
        if type(text) is str:
            text = unicode(text)
            self.is_str = True
        elif type(text) is unicode:
            self.is_str = False
        del self.lines[:]
        text = text.split('\n')
        for line in text:
            self.lines.append(tuple(map(ord, line)))

    def set_text(self, text):
        self._text_to_lines(text)
        self.put_to_redraw()

    @property
    def text(self):
        pass

    # TODO: Не работает, т.к. переопределяется методом __setattr__() базового класса.
    @text.setter
    def text(self, text):
        self._text_to_lines(text)
        self.put_to_redraw()

    @text.getter
    def text(self):
        text_out = u''
        for ord_line in self.lines:
            line = u''
            for ord_uch in ord_line:
                line += unichr(ord_uch)
            text_out += line + u'\n'
        if self.is_str:
            text_out = str(text_out)
        return text_out

    def redraw(self):
        glNewList(self.dl, GL_COMPILE)
        self.font.draw_gluint_lines((self.pos[0], self.pos[1]), self.lines, self.color)
        glEndList()


class StaticText(glwidget.GlWidget):
    """
    Выводит текст на экран. Текст может содержать перевод строки.
    """

    def __init__(self, pos, text='', font=None, user_data=None, color=colors.WHITE):
        assert type(pos) is tuple
        assert len(pos) == 2
        assert type(pos[0]) is int
        assert type(pos[1]) is int
        assert (type(text) is str) or (type(text) is unicode)
        assert (font is None) or (type(font) is fonts.CairoFont)

        self.pos = pos
        viewport = glGetIntegerv(GL_VIEWPORT)
        self.parent_height = viewport[3]
        self.text = text
        self.color = list(color)
        self.user_data = user_data
        self.rdc = [GL_COMPILE_AND_EXECUTE]
        if font is None:
            self.font = fonts.CairoFont()
        else:
            self.font = font

    def redraw(self):
        glNewList(self.dl, self.rdc[0])
        self.font.draw_text(self.pos, self.text, self.color)
        glEndList()
        self.rdc[0] = GL_COMPILE

    def __del__(self):
        super(StaticText, self).__del__()
        glDeleteLists(self.dl, 1)
