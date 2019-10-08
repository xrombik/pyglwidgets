#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glib
import os

# Свои модули
from . import gltools
from . import fonts
from .glimports import *


class ResourceCtl(object):
    DEFAULT_FREETYPE_FONT_FILE = 'LiberationSans-Regular.ttf'
    DEFAULT_FREETYPE_FONT_SIZE = 14

    def __init__(self, argv, dir_local='', dir_user='', dir_prog='', data_path='data'):
        assert type(dir_local) in (str, unicode)
        assert type(dir_user) in (str, unicode)
        assert type(dir_prog) in (str, unicode)
        assert type(data_path) in (str, unicode)
        assert os.path.exists(data_path)

        self.data_path = data_path

        local_path = glib.get_user_data_dir()
        self.user_save_path = os.path.join(local_path, dir_local, dir_user)
        self.prog_save_path = os.path.join(local_path, dir_local, dir_prog)
        prefix_dir = os.path.join(local_path, dir_local)
        if not os.path.exists(prefix_dir):
            os.mkdir(self.user_save_path)
        if not os.path.exists(self.user_save_path):
            os.mkdir(self.prog_save_path)
        if not os.path.exists(self.prog_save_path):
            os.mkdir(self.prog_save_path)
        print(u'Папка для хранения данных пользователя: %s' % self.user_save_path)
        print(u'Папка для хранения данных программы: %s' % self.prog_save_path)

        self.textures = dict()
        self.ft_fonts = dict()
        self.perm = 0  # Разрешения для оператора

    def uninit(self):
        self.ft_fonts.clear()
        glDeleteTextures(self.textures.values())

    def get_ft_font(self, font_file=DEFAULT_FREETYPE_FONT_FILE, font_size=DEFAULT_FREETYPE_FONT_SIZE):
        """
        Возвращает шрифт растеризованный в FreeType.
        :param font_file: Имя файла шрифта
        :param font_size: Высота шрифта во внутренних еденицах шрифта
        :return: FreeTypeFont
        """
        assert type(font_size) is int
        assert type(font_file) in (str, unicode)
        font_key = '%s %u' % (font_file, font_size)
        if font_key in self.ft_fonts:
            ft_font = self.ft_fonts[font_key]
        else:
            path = os.path.join(self.data_path, font_file)
            if not (os.path.exists(path) and os.path.isfile(path)):
                s = 'файл \'%s\' - не найден.' % path
                raise ValueError(s)
            print(u'генерация шрифта \'%s\' ...' % font_key)
            ft_font = fonts.FreeTypeFont(path, font_size)
            print(u'\tвыполнено.')
            self.ft_fonts[font_key] = ft_font
        return ft_font

    def get_texture(self, path):
        assert type(path) in (str, unicode), 'Должна быть строка'
        path = os.path.join(self.data_path, path)
        if self.textures.get(path) is None:
            if os.path.exists(path) and os.path.isfile(path):
                self.textures[path] = gltools.texture_from_file(path)
            else:
                s = 'ошибка: файл \'%s\' - не найден.' % path
                raise ValueError(s)
        return self.textures[path]

    def get_textures(self, fmt, count=1, begin=0):
        """
        Загружает массив структур из файлов с именами, соответствующим
        заданной строке-формату, например 'image_%u.png' значит 'image_0.png',
        'image_1.png' ...
        :param fmt: Строка-формат, куда подставляются значения от begin до сount
        :param count: Количество
        :param begin: Начальное значение индекса в строке-формате
        :return: Список текстур
        """
        assert type(fmt) in (str, unicode), 'Дожна быть строка'
        assert type(count) is int, 'Должен быть целым'
        assert (type(begin) is int) and (begin >= 0), 'Должен быть положительным целым: \'%s\'' % begin
        assert count > 0, 'Нужо загрузить хотя бы одну текстуру'
        return [self.get_texture(fmt % i) for i in range(begin, count)]
