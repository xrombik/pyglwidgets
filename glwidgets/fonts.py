#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cairo
import inspect
import freetype

from . import colors
from . import gltools
from .glimports import *

__all__ = ('FreeTypeFont', 'CairoFont', 'DEFAULT_FONT_FACE', 'DEFAULT_FONT_SIZE', 'DEFAULT_DPI')

DEFAULT_FONT_FACE = 'Liberation Sans'
DEFAULT_FONT_SIZE = 18
DEFAULT_DPI = 96


def next_p2(a):
    rval = 1
    while rval < a:
        rval *= 2
    return rval


class FreeTypeFont(object):
    """
    Реализация шрифтов на посимволных display lists
    """
    # Алфавит используемых символов. Можно добавить символы при необходимости.
    # Количество зарезервированных индексов display lists и текстур будет равно
    # самому большому значению кода символа из этой таблицы.
    ALPHABET = \
        (u'й', u'э', u'ц', u'у', u'к', u'е', u'н', u'г', u'ш', u'щ',
         u'з', u'х', u'ъ', u'ф', u'ы', u'в', u'а', u'п', u'р', u'о',
         u'л', u'д', u'ж', u'э', u'я', u'ч', u'с', u'м', u'и', u'т',
         u'ь', u'б', u'ю', u'Й', u'Ц', u'У', u'К', u'Е', u'Н', u'Г',
         u'Ш', u'Щ', u'З', u'Х', u'Ъ', u'Ф', u'Ы', u'В', u'А', u'П',
         u'Р', u'О', u'Л', u'Д', u'Ж', u'Э', u'Я', u'Ч', u'С', u'М',
         u'И', u'Т', u'Ь', u'Б', u'Ю', u'Q', u'W', u'E', u'R', u'T',
         u'Y', u'U', u'I', u'O', u'P', u'A', u'S', u'D', u'F', u'G',
         u'H', u'J', u'K', u'L', u'Z', u'X', u'C', u'V', u'B', u'N',
         u'M', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9',
         u'0', u'-', u'=', u'!', u'@', u'#', u'$', u'%', u'^', u'&',
         u'*', u'(', u')', u'_', u'+', u'`', u'ё', u'!', u'\"', u';',
         u'%', u':', u'?', u'.', u'/', u'\\', u'<', u'>', u',', u' ',
         u'q', u'w', u'e', u'r', u't', u'y', u'u', u'i', u'o', u'p',
         u'a', u's', u'd', u'f', u'g', u'h', u'j', u'k', u'l', u'z',
         u'x', u'c', u'v', u'b', u'n', u'm', u'[', u']', u'{', u'}')

    def __init__(self, file_name, font_height=DEFAULT_FONT_SIZE, dpi=DEFAULT_DPI, line_spacing=1.5):
        range_dl = 0
        for ordch in map(ord, FreeTypeFont.ALPHABET):
            if range_dl < ordch:
                range_dl = ordch

        self.range = range_dl + 1
        self.size = font_height

        viewport = glGetIntegerv(GL_VIEWPORT)
        self.parent_hight = viewport[3]

        self.dl_pushScreenCoordinateMatrix = glGenLists(1)
        glNewList(self.dl_pushScreenCoordinateMatrix, GL_COMPILE)
        glPushAttrib(GL_TRANSFORM_BIT)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(viewport[0], viewport[2], viewport[3], viewport[1], -1, 1)
        glPopAttrib()
        glEnable(GL_TEXTURE_2D)
        glEndList()

        self.dl_pop_projection_matrix = glGenLists(1)
        glNewList(self.dl_pop_projection_matrix, GL_COMPILE)
        glDisable(GL_TEXTURE_2D)
        glPushAttrib(GL_TRANSFORM_BIT)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glPopAttrib()
        glEndList()

        self.height = line_spacing * font_height
        self.range_dl = range_dl
        self.face = freetype.Face(file_name)
        self.face.set_char_size(font_height << 6, font_height << 6, dpi, dpi)
        self.list_base = glGenLists(self.range)
        self.textures = glGenTextures(self.range)
        self.chars_widths = [0] * self.range
        self.ord_map_dict = dict()
        self.text_widths = dict()

        # Генерация display lists и сохранение ширин символов
        for ch in FreeTypeFont.ALPHABET:
            self.chars_widths[ord(ch)] = self._make_dlist(ch)

    def get_text_width(self, text):
        """
        Возвращает ширину текста. Для многострочного -
        ширину самой широкой строки.
        :param text:
        :return:
        """
        assert type(text) is unicode
        if text in self.text_widths:
            return self.text_widths[text]
        text_width = 0
        text_width_line = 0
        for ch in text:
            text_width += self.chars_widths[ord(ch)]
            if ch == u'\n':
                if text_width > text_width_line:
                    text_width_line = text_width
                text_width = 0
        if text_width > text_width_line:
            text_width_line = text_width
        self.text_widths[text] = text_width_line
        return text_width_line

    def draw_gluint_lines(self, pos, lines, color=colors.WHITE):
        glCallList(self.dl_pushScreenCoordinateMatrix)
        glEnable(GL_TEXTURE_2D)
        glListBase(self.list_base)
        y = pos[1]
        glColor4ub(*color)
        for line in lines:
            glPushMatrix()
            glLoadIdentity()
            glTranslatef(pos[0], y, 0)
            glCallLists(line)
            glPopMatrix()
            y += self.height
        glDisable(GL_TEXTURE_2D)
        glCallList(self.dl_pop_projection_matrix)

    def _str_to_gluint(self, s):
        if s not in self.ord_map_dict:
            ms = map(ord, s)
            self.ord_map_dict[s] = ms
        else:
            ms = self.ord_map_dict[s]
        return ms

    def draw_text(self, pos, s, color=colors.WHITE):
        # type: (FreeTypeFont, tuple, str, tuple) -> None
        """
        Рисует текст с учётом перевода строки
        :param pos: Кортеж положения на экране из X и Y координат
        :param s:
        :param color:
        :return:
        """
        assert type(s) is unicode
        glCallList(self.dl_pushScreenCoordinateMatrix)
        glListBase(self.list_base)
        glColor4ub(*color)
        y = pos[1]
        for si in s.split('\n'):
            ms = self._str_to_gluint(si)
            glPushMatrix()
            glLoadIdentity()
            glTranslatef(pos[0], y, 0)
            glCallLists(ms)
            glPopMatrix()
            y += self.height
        glCallList(self.dl_pop_projection_matrix)

    def __del__(self):
        glDeleteLists(self.dl_pushScreenCoordinateMatrix, 1)
        glDeleteLists(self.dl_pop_projection_matrix, 1)
        glDeleteLists(self.list_base, self.range_dl)
        glDeleteTextures(self.textures)

    def _make_dlist(self, ch):
        """
        Создаёт display list одного символа
        :param ch:
        :return:
        """
        char_index = self.face.get_char_index(ord(ch))
        self.face.load_glyph(char_index)
        glyph = self.face.glyph
        bitmap = self.face.glyph.bitmap

        width = next_p2(bitmap.width)
        height = next_p2(bitmap.rows)
        expanded_data = bytearray(2 * width * height)
        for j in range(height):
            for i in range(width):
                val = 0
                if not ((i >= bitmap.width) or (j >= bitmap.rows)):
                    val = bitmap.buffer[i + bitmap.width * j]
                expanded_data[2 * (i + j * width)] = val
                expanded_data[2 * (i + j * width) + 1] = val
        glBindTexture(GL_TEXTURE_2D, self.textures[ord(ch)])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_LUMINANCE_ALPHA, GL_UNSIGNED_BYTE, str(expanded_data))
        del expanded_data

        x = float(bitmap.width) / float(width)
        y = float(bitmap.rows) / float(height)

        dl_index = self.list_base + ord(ch)
        glNewList(dl_index, GL_COMPILE)
        glBindTexture(GL_TEXTURE_2D, self.textures[ord(ch)])
        glTranslatef(glyph.bitmap_left, 0, 0)
        glPushMatrix()
        glTranslatef(0, -float(glyph.bitmap_top), 0)
        glBegin(GL_QUADS)
        glTexCoord2d(0, y); glVertex2f(0, bitmap.rows)
        glTexCoord2d(x, y); glVertex2f(bitmap.width, bitmap.rows)
        glTexCoord2d(x, 0); glVertex2f(bitmap.width, 0)
        glTexCoord2d(0, 0); glVertex2f(0, 0)
        glEnd()
        glPopMatrix()
        glTranslatef(self.face.glyph.advance.x >> 6, 0, 0)
        glEndList()
        return bitmap.width


class CairoFont(object):
    font_items = dict()
    image_surface0 = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)
    cairo_context = cairo.Context(image_surface0)
    cairo_context.select_font_face(DEFAULT_FONT_FACE)
    cairo_context.set_font_size(DEFAULT_FONT_SIZE)

    def __init__(self, face=DEFAULT_FONT_FACE, font_hight=DEFAULT_FONT_SIZE, predraw=None):
        assert type(face) is str
        assert type(font_hight) is int
        self.cc0 = cairo.Context(CairoFont.image_surface0)  # Поверхность для вычисления размера текста
        self.cc0.select_font_face(face)
        self.cc0.set_font_size(font_hight)
        self.face = face  # название начертания букв
        self.size = font_hight  # размер букв
        self.texture_id = glGenTextures(1)

        if predraw is not None:
            assert inspect.isfunction(predraw)
            self.predraw = predraw

    def __del__(self):
        glDeleteTextures([self.texture_id])

    def __new__(cls, face=DEFAULT_FONT_FACE, face_size=DEFAULT_FONT_SIZE, predraw=None):
        assert type(face) is str
        assert type(face_size) is int
        font_key = (face, face_size)
        if font_key in CairoFont.font_items:
            return CairoFont.font_items[font_key]
        else:
            font_item = super(CairoFont, cls).__new__(cls)
            CairoFont.font_items[(face, face_size)] = font_item
            print(u'fonts.py: шрифт создан \'%s %u\'' % (face, face_size))
            return font_item

    def get_text_width(self, text):
        xbearing, ybearing, width, height0, xadvance, yadvance = self.cc0.text_extents(text)
        return int(xadvance + 0.5)

    def get_text_hight(self):
        fascent, fdescent, fheight, fxadvance, fyadvance = self.cc0.font_extents()
        return int(fheight + 0.5)

    def draw_text(self, pos, text, color=colors.WHITE):
        # Вычислить размер в пикселях который будет занимать текст
        xbearing, ybearing, width, height0, xadvance, yadvance = self.cc0.text_extents(text)
        fascent, fdescent, fheight, fxadvance, fyadvance = self.cc0.font_extents()
        height = (text.count('\n') + 1) * fheight
        # Нарисовать текcт в текстуру:
        # 1) создать изображение текста в буфере
        cis = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(xadvance), int(height))
        cc = cairo.Context(cis)
        cc.select_font_face(self.face)
        cc.set_font_size(self.size)
        cc.set_operator(cairo.OPERATOR_SOURCE)
        cc.set_source_rgba(1.0, 1.0, 1.0, 1.0)

        y = fascent
        for t in text.split('\n'):
            cc.move_to(0, y)
            cc.show_text(t)
            y += fheight

        # 2) Назначить буфер в текстуру
        texture = gltools.data_to_texture(self.texture_id, cis.get_data(), int(xadvance), int(height))
        cis.finish()
        gltools.draw_texture(texture, pos, color)
