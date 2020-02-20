#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import gtk
from .text import *
from .gltools import *
from .driver import safe_connect
from .driver import safe_disconnect


class TextRegulator(StaticText):
    """
    Ввод данных движением мыши
    """
    KEY_TO_VALUE = {u'1': 1.0, u'2': 2.0, u'3': 3.0, u'4': 4.0, u'5': 5.0, u'6': 6.0, u'7': 7.0, u'8': 8.0, u'9': 9.0,
                    u'0': 10.0, u'-': 0.0}

    def __init__(self, pos=(0, 0), fmt='%03f', val_min=0, val_max=100, val=50, size=(40, 24),
                 scale=0.01, axis=1, font=None, color=(255, 255, 255, 150), user_proc=None, user_data=None):
        """
        :param pos: Координаты на экране в пикселях
        :param fmt: Текстовой фрмат отображения, например 'Масштаб %s км'
        :param val_min: Начальное значение регулятора
        :param val_max: Конечное значение регулятора
        :param scale: Шаг изменения значения на один пиксель перемещения мыши
        :param axis: Ось координат используемая для изменения параметра: 0 - ось X, 1 - ось Y
        :param val: Текущее значение регулятора
        :param font: Шрифт текста
        :param color: Цвет текста
        :param user_proc: Процедура вызываемая при изменения значения
        :param user_data: Данные пользователя
        :return:
        """
        assert type(color) is tuple  # Цвет должен состоять из четырёх компонент в кортеже
        assert len(color) == 4  # Цвет должен состоять из четырёх компонент в кортеже
        for c in color:
            assert type(c) is int  # Значение цвета должно быть целым
            assert 0 <= c <= 255  # Значение цвета должно быть от 0 до 255 включительно
        assert type(pos) is tuple
        assert len(pos) == 2
        assert type(pos[0]) is int
        assert type(pos[1]) is int
        assert type(fmt) is str
        assert type(axis) is int
        assert axis in (0, 1)  # 0 - ось X, 1 - ось Y
        assert type(size) is tuple
        assert len(size) == 2
        assert type(size[0]) is int
        assert type(size[1]) is int
        assert (font is None) or (type(font) is fonts.CairoFont)
        if user_proc is not None:
            assert (inspect.isfunction(user_proc))  # Должна быть функцией

        super(TextRegulator, self).__init__(pos, fmt, font, color)
        self.format = fmt
        self.min = val_min
        self.max = val_max
        self.scale = scale
        self.val = val
        self.axis = axis
        self.prev = pos[axis]
        self.pc.append(('ehid0', safe_connect, 'button-press-event', self._button_press))
        self.text = self.get_text()
        self.size = size
        self.ehid_kp = None
        self.ehid0 = None
        self.ehid1 = None
        self.ehid2 = None
        self.user_proc = user_proc
        self.user_data = user_data
        r, g, b, a = color
        self.color = r, g, b, 160
        self.rect_col = 0, 0, 0, 0
        fascent, fdescent, fheight, fxadvance, fyadvance = self.font.cc0.font_extents()
        self.fdescent = int(fdescent + 0.5)
        self.points = self.pos, \
                      (self.pos[0] + self.size[0], self.pos[1]), \
                      (self.pos[0] + self.size[0], self.pos[1] - self.size[1] - self.fdescent), \
                      (self.pos[0], self.pos[1] - self.size[1] - self.fdescent)

    def redraw(self):
        glNewList(self.dl, GL_COMPILE)
        draw_polygon(self.points, self.rect_col)
        self.font.draw_text(self.pos, self.get_text(), self.color)
        glEndList()

    def key_press_callback(self, window, event):
        """
        Вызывается при нажатии на клавишы клавиатуры, когда экземпляр в фокусе ввода
        :param window: Дескриптор окна программы
        :param event: Событие gtk
        :return: Ничего
        """
        char = unichr(gtk.gdk.keyval_to_unicode(event.keyval))
        if char in TextRegulator.KEY_TO_VALUE:
            mul_val = TextRegulator.KEY_TO_VALUE[char]
            val = self.val
            self.val = self.min + (float(self.max - self.min) / float(len(TextRegulator.KEY_TO_VALUE) - 1)) * mul_val
            if val != self.val:
                if self.user_proc is not None:
                    self.user_proc(self)

    def _button_press(self, *args):
        """
        Вызывается при нажатии на кнопку мыши
        :param args:
        :return:
        """
        event = args[1]
        if event.button != 1:  # 1 - левая кнопка мыши, 2 - средняя, 3 - правая.
            return
        cover = check_rect(self.size[0], self.size[1], self.pos, event.x, event.y)
        if cover:
            self.pc.append(('ehid_kp', safe_connect, 'key-press-event', self.key_press_callback))
            self.pc.append(('ehid1', safe_connect, 'motion-notify-event', self._motion_notify))
            self.pc.append(('ehid2', safe_connect, 'button-release-event', self._button_release))
            self.prev = (event.x, event.y)[self.axis]
            self.text = self.get_text()
            r, g, b, a = self.color
            self.color = r, g, b, 250
        else:
            self.pc.append(('ehid_kp', safe_disconnect))

    def _button_release(self, *args):
        """
        Вызывается при отпускании кнопки мыши
        :param args:
        :return:
        """
        event = args[1]
        if event.button != 1:  # 1 - левая кнопка мыши, 2 - средняя, 3 - правая.
            return
        if self.ehid1 is not None:
            self.pc.append(('ehid1', safe_disconnect))
            self.prev = self.pos[self.axis]
            self.text = self.get_text()
            r, g, b, a = self.color
            self.color = r, g, b, 160
        if self.ehid2 is not None:
            self.pc.append(('ehid2', safe_disconnect))

    def _motion_notify(self, *args):
        """
        Вызывается при движении мыши
        :param args:
        :return:
        """
        event = args[1]
        pos = event.x, event.y
        delta = self.prev - pos[self.axis]
        self.val += float(delta) * self.scale
        self._pass_limits()
        self.prev = pos[self.axis]
        cur_text = self.get_text()
        if self.text != cur_text:
            self.text = cur_text
            if self.user_proc:
                self.user_proc(self)
            self.put_to_redraw()
        return False

    def get_text(self):
        """
        Возвращает отображаемый текст в заданном формате
        :return:
        """
        return self.format % self.val

    def get_val(self):
        """
        Возвращает значение регулятора
        :return:
        """
        return self.val

    def _pass_limits(self):
        """
        Отсекает значение по заданным границам
        :return:
        """
        if self.val > self.max:
            self.val = float(self.max)
        if self.val < self.min:
            self.val = float(self.min)
