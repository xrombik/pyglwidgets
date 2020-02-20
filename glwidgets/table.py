#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import gtk

from . import gltools
from . import colors
from . import fonts
from . import entry
from . import tools
from . import GlWidget
from .glimports import *
from .glconst import *
from .fonts import DEFAULT_FONT_FACE
from .fonts import DEFAULT_FONT_SIZE
from .driver import safe_connect
from .driver import safe_disconnect


class Table(GlWidget):
    ROW_FLAG_NONE = 0
    ROW_FLAG_SELECTED = 1
    """ Флаг ряда таблицы. Если установлен, то ряд помечен как выбранный """

    @property
    def auto_widths(self):
        return self.get_widths == self.get_widths_auto

    @auto_widths.setter
    def auto_widths(self, val):
        self.get_widths = (self.get_widths_const, self.get_widths_auto)[val]
        self.size = self.update_rect()[2:5]
        self.put_to_redraw()
        
    @staticmethod
    def _on_2button_press_default(tbl, event):
        assert type(tbl) is Table
        x0, y0, w, h, ws, rh = tbl.update_rect()
        if tbl.i_cur_row is None:
            return
        cover = gltools.check_rect(w, h - rh, (tbl.pos[0], tbl.pos[1] + rh), event.x, event.y)
        if tbl.edit_proc(tbl.i_cur_column, tbl.i_cur_row) and cover:
            i, j = tbl.i_cur_row + 1, tbl.i_cur_column
            if i < len(tbl._rows):
                if j < len(tbl._rows[i]):
                    tbl.entry.text = copy.deepcopy(tbl._rows[i][j])
                    ep_x = tbl.pos[0]
                    for w in tbl.size[2][0:tbl.i_cur_column]:
                        ep_x += w
                    l_height = tbl.font.get_text_hight()
                    tbl.entry.pos = ep_x + tbl.line_width, tbl.pos[1] + (tbl.i_cur_row + 1 - tbl.view_begin) * \
                                    (l_height + tbl.line_width) + tbl.line_width * 2
                    tbl.entry.size = tbl.size[2][tbl.i_cur_column] - tbl.line_width * 2, l_height - tbl.line_width * 2
                    tbl.entry.show()
                    tbl.ehid2 = None
                else:
                    print('glwidgets.py:ошибка: обращение к колонке таблицы %u, но колонок всего %u' % (j, len(tbl._rows[i])))
            else:
                print('glwidgets.py:ошибка: обращение к строке таблицы %u, но строк всего %u' % (i, len(tbl._rows)))

    # TODO: Добавить возможность сортировки по нажатию на заголовок кнопкой мыши
    @staticmethod
    def column_auto_width_proc(font, s, _cx):
        """
        Используется для определения ширины колонки
        :param font: Шрифт используемый в таблице
        :param s: Строка ячейки заголовка таблицы
        :param _cx: Индекс колонки
        :return: Ширина колонки
        """
        return font.get_text_width(s)

    @staticmethod
    def edit_proc_default(_cx, _cy):
        """
        Используется для проверки разрешения на редактирование ячейки
        :param _cx: Индекс колонки
        :param _cy: Индекс строки
        :return: True - если редактирование в ячейке разрешено, False - если редактирование запрещено
        """
        return True

    @staticmethod
    def color_proc_horiz(_cx, cy):
        """
        Используется для определения цвета текста ячейки.
        :param _cx: Индекс колонки
        :param cy: Индекс строки
        :return: Цвет ячейки
        """
        if cy > 0:
            return colors.TABLE_TEXT
        return colors.SAND

    @staticmethod
    def color_proc_vert(cx, cy):
        """
        Используется для определения цвета текста ячейки.
        :param cx: Индекс колонки
        :param cy: Индекс строки
        :return: Цвет ячейки
        """
        if cy == 0:
            return colors.SAND
        if cx & 1:
            return colors.TABLE_TEXT
        return colors.SAND

    @staticmethod
    def default_bg_color_proc(i_cur_row, i_row, rows_flags, focus):
        # type: (int, int, list, bool) -> tuple
        """
        Используется для определения цвета фона ряда
        :param i_cur_row: Выделенный ряд
        :param i_row: Индекс ряда для перерисовки
        :param rows_flags: Флаги рядов
        :param focus: Флаг таблица в фокусе
        :return: Цвет фона ряда с индексом i_row
        """
        if (i_cur_row == i_row) and (rows_flags[i_row] & Table.ROW_FLAG_SELECTED):
            # Цвет фона в неактивном и активном режимах, в том числе выделенного ряда
            return (colors.TABLE_SEL_INACTIVE, colors.TABLE_SEL_ACTIVE)[focus]
        elif rows_flags[i_row] & Table.ROW_FLAG_SELECTED:
            return colors.TABLE_SEL_INACTIVE
        elif (i_cur_row == i_row) and focus:
            return colors.TABLE_SEL_ACTIVE
        elif (i_cur_row == i_row) and (not focus):
            return colors.TABLE_SEL_INACTIVE
        else:
            # Цвет фона чётных и нечётных строк
            return colors.TABLE_BACK[i_row % len(colors.TABLE_BACK)]

    def set_cursor_to_row(self, i_column, cell_str):
        """
        Устанавливает курсор таблицы на заданную строку
        :param i_column:
        :param cell_str:
        :return:
        """
        self.i_cur_row = 0
        for row in self.get_rows()[1:]:
            if ('%s' % row[i_column]) == ('%s' % cell_str):
                break
            self.i_cur_row += 1

    def __init__(self, pos, rows, view_max=5, font_name=DEFAULT_FONT_FACE,
                 font_size=DEFAULT_FONT_SIZE, column_width_proc=None):
        assert type(rows) is list
        assert len(rows) > 0
        assert len(rows[0]) > 0

        self.ehid1 = None
        self.ehid2 = None
        self.size = None
        self.i_cur_row_prev = None
        self._rows = list()
        self.rows_multi_sel = False
        """ Разрешить множественный выбор рядов """

        self.pos = pos
        self.line_width = 2

        self.i_cur_row = None  # Индекс текущей выбранной строки
        self.view_max = view_max  # Максимальное количество отображаемых строк
        self.view_begin = 0
        self.font = fonts.CairoFont(font_name, font_size)
        if column_width_proc is None:
            self.column_width_proc = Table.column_auto_width_proc  # Процедура определяющая ширину колонки
        else:
            self.column_width_proc = column_width_proc
        self.get_widths = self.get_widths_const
        self.widths = [100] * len(rows[0])
        self.set_rows(rows)
        self.i_cur_column = 0
        self.edit_proc = Table.edit_proc_default  # Процедура проверяющая резрешение редактирования ячейки
        self.entry = entry.Entry(self.pos, '', (100, 20))  # Поле ввода. Используется для редактирования ячеек
        self.entry.hide()
        self.entry.font = self.font
        self.entry.on_edit_done = self._on_edit_done
        self.on_edit_done = None
        self.ehid_kp = None
        # Обработчик кнопки Delete. Должен возвращать False если нужно продолжить обработку
        # события встроенным методами класса. Встроенный метод класса удаляет выбранную строку.
        self.on_delete = None
        self.user_data = None
        self.on_sel_change = None
        """ Обработчик события изменения выбора текущей строки """
        self.on_2button_press = self._on_2button_press_default
        self._rows_flags = [Table.ROW_FLAG_NONE] * len(self._rows)
        """	Флаги рядов таблицы """
        self.focus = False
        self.color_proc = Table.color_proc_horiz  # Процедура определяющая цвет текста для ячейки
        self.bg_color_proc = self.default_bg_color_proc  # Процедура определяющая цвет фона для ячейки
        self.put_to_redraw()

    def _check_rows(self):
        """
        Проверка количества колонок в каждом ряду
        """
        rows_len = len(self._rows[0])
        for i, row in enumerate(self._rows[1:]):
            if rows_len != len(row):
                raise ValueError('Ряд %u имеет отличное количество колонок - %u, вместо %u:\n%s' % (i, len(row), rows_len, self._rows))

    def update_rect(self):
        """
        Возвращает размеры таблицы в пикселях
        :return:
        """
        width, height = 0, 0
        ws = self.get_widths()
        width += self.line_width
        row_height = self.font.get_text_hight()
        height = (row_height + self.line_width) * (len(self._rows[self.view_begin + 1: self.view_begin + 1 + self.view_max]) + 1)
        return self.pos[0], self.pos[1], width, height, ws, row_height

    def get_widths_auto(self):
        cx = len(self._rows[0])
        cy = len(self._rows)
        widths = list()
        j = 0
        while j < cx:
            w = 0
            i = 0
            while i < cy:
                s = self._rows[i][j]
                w0 = self.font.get_text_width(s)
                if w0 > w: w = w0
                i += 1
            widths.append(w + self.line_width * 2)
            j += 1
        return widths
    
    def get_widths_const(self):
        return self.widths

    def show_selected(self):
        """
        Перематывает таблицу к выделенной строке
        :return:
        """
        view_end = self.view_begin + self.view_max
        if not (self.view_begin < self.i_cur_row < view_end):
            self.view_begin = self.i_cur_row
        self.size = self.update_rect()[2:5]
        self.put_to_redraw()

    def set_rows(self, rows, rows_flags=None):
        # type: (Table, list) -> None
        """
        Устанавливает новые ряды таблицы
        :param rows: Ряды таблицы
        :param rows_flags: Флаги рядов таблицы
        :return: Ничего
        """
        assert isinstance(rows, (list, tuple))
        self._rows = rows
        if rows_flags is None:
            self._rows_flags = [Table.ROW_FLAG_NONE] * len(self._rows)
        else:
            self._rows_flags = rows_flags
        self._check_rows()
        self.size = self.update_rect()[2:5]
        self.put_to_redraw()

    def get_rows(self):
        """
        Возвращает ряды таблицы
        :return: Список рядов
        """
        return self._rows

    def get_rows_byflags(self, row_flags):
        """
        Возвращает ряды таблицы с флагами row_flags
        :return: Список рядов
        """
        return [row for row, flags in zip(self._rows, self._rows_flags) if flags == row_flags]

    def get_rows_flags(self):
        """
        Возвращает флаги рядов таблицы
        :return: Флаги рядов таблицы
        """
        return self._rows_flags

    def set_flags(self, rows_flags=None):
        assert (rows_flags is None) or (type(rows_flags) is list)
        if rows_flags is None:
            self._rows_flags = [Table.ROW_FLAG_NONE] * len(self._rows)
        else:
            assert len(rows_flags) == len(self._rows)
            self._rows_flags = rows_flags

    def add_row(self, row, row_flags=ROW_FLAG_NONE):
        # type: (Table, list, int) -> None
        """
        Добавляет новый ряд
        :param row: Новый ряд
        :param row_flags: Флаги нового ряда
        :return: Ничего
        """
        assert type(row) is list
        assert type(row_flags) is int
        self._rows.append(row)
        self._rows_flags.append(row_flags)
        self._check_rows()
        self.size = self.update_rect()[2:5]
        self.put_to_redraw()

    def set_row(self, i_row, row, row_flags=None):
        i_row += 1
        self._rows[i_row] = copy.deepcopy(row)
        self._check_rows()
        if row_flags is not None:
            self._rows_flags = row_flags
        self.put_to_redraw()

    def del_row(self, i_row):
        # type: (Table, int) -> None
        """
        Удаляет заданный ряд
        :param i_row: Индекс ряда
        :return: Ничего
        """
        i_row += 1
        if i_row < len(self._rows):
            del self._rows[i_row]
            del self._rows_flags[i_row]
            if len(self._rows) > 1:
                if (self.i_cur_row + 1) > len(self._rows):
                    self.i_cur_row = len(self._rows) - 1
            else:
                self.i_cur_row = 0
            if self.on_edit_done is not None:
                self.on_edit_done(self, None)
            self.put_to_redraw()

    def _on_edit_done(self, _entry):
        """
        Вызывается после завершения редактирования ячейки таблицы
        :param _entry:
        :return:
        """
        i, j = self.i_cur_row + 1, self.i_cur_column
        prev_val = copy.deepcopy(self._rows[i][j])
        self._rows[i][j] = copy.deepcopy(self.entry.text)
        self.entry.hide()
        self.put_to_redraw()
        self.pc.append(('ehid_kp', safe_connect, 'key-press-event', self._on_key_press))
        if self.on_edit_done is not None:
            self.on_edit_done(self, prev_val)

    def _on_key_press(self, _widget, event, *_args):
        """
        Вызывается при нажатии на кнопку клавиатуры
        :param widget:
        :param event:
        :param args:
        :return:
        """
        prev_i_cur_row = self.i_cur_row
        char_name = gtk.gdk.keyval_name(event.keyval)
        if char_name == 'Delete':
            if self.on_delete is not None:
                if self.on_delete(self):
                    i = self.i_cur_row + 1
                    if i < len(self._rows):
                        del self._rows[i]
                        if len(self._rows) > 1:
                            if (self.i_cur_row + 1) > len(self._rows):
                                self.i_cur_row = len(self._rows) - 1
                        else:
                            self.i_cur_row = 0
                        if self.on_edit_done is not None:
                            self.on_edit_done(self, None)
                        self.put_to_redraw()
        elif char_name == 'Up':
            if not (type(self.i_cur_row) is int):
                return
            self.i_cur_row -= 1
            if self.i_cur_row < 0:
                self.i_cur_row = 0
            if self.view_begin > self.i_cur_row:
                self.view_begin -= 1
        elif char_name == 'Down':
            if not (type(self.i_cur_row) is int):
                return
            self.i_cur_row += 1
            if (self.i_cur_row + 2) > len(self._rows):
                self.i_cur_row = len(self._rows) - 2
            if self.i_cur_row > ((self.view_begin + self.view_max) - 1):
                self.view_begin += 1
            if self.i_cur_row < 0:
                self.i_cur_row = 0
        self.size = self.update_rect()[2:5]
        if prev_i_cur_row != self.i_cur_row:
            if self.on_sel_change is not None:
                self.on_sel_change(self)
        return True

    def _on_mbutton_press(self, *args):
        """
        Вызывается при нажатии кнопки мыши
        :param args:
        :return:
        """
        prev_i_cur_row = self.i_cur_row
        event = args[1]  # type: gtk.gdk.Event
        focus_changed = False
        sel_changed = False
        # noinspection PyProtectedMember
        if event.type == gtk.gdk.BUTTON_PRESS:
            # Поиск строки, которую кликнули
            self.entry.hide()
            x, y, w, h, ws, rh = self.update_rect()
            if not gltools.check_rect(w, h, self.pos, event.x, event.y):
                self.focus = False
                return False
            if not self.focus:
                focus_changed = True
                self.focus = True
            self.pc.append(('ehid_kp', safe_connect, 'key-press-event', self._on_key_press))
            dy = event.y - self.pos[1]
            i_cur_row = int(dy // (self.font.get_text_hight() + self.line_width))
            self.i_cur_row = i_cur_row - 1 + self.view_begin
            if self.i_cur_row < 0:
                self.i_cur_row = 0

            # Отметить текущий ряд
            if event.button == 1:
                for i in range(len(self._rows_flags)):
                    row_flags = self._rows_flags[i]
                    self._rows_flags[i] &= ~Table.ROW_FLAG_SELECTED
                    if row_flags != self._rows_flags[i]:
                        sel_changed = True
                # TODO: Надо как то разобраться, что бы работало без необходимости перебирать все ряды
                row_flags = self._rows_flags[self.i_cur_row + 1]
                self._rows_flags[self.i_cur_row + 1] = tools.set_bits(row_flags, Table.ROW_FLAG_SELECTED, Table.ROW_FLAG_SELECTED)
                if row_flags != self._rows_flags[self.i_cur_row + 1]:
                    sel_changed = True
            # Отметить ещё один выделенный ряд
            elif (event.button == 3) and self.rows_multi_sel:
                row_flags = self._rows_flags[self.i_cur_row + 1]
                self._rows_flags[self.i_cur_row + 1] = tools.set_bits(row_flags, ~row_flags, Table.ROW_FLAG_SELECTED)
                if row_flags != self._rows_flags[self.i_cur_row + 1]:
                    sel_changed = True
            elif (event.button == 3) and (not self.rows_multi_sel):
                for i in range(len(self._rows_flags)):
                    row_flags = self._rows_flags[i]
                    self._rows_flags[i] &= ~Table.ROW_FLAG_SELECTED
                    if row_flags != self._rows_flags[i]:
                        sel_changed = True
            if (self._rows_flags[self.i_cur_row + 1] & Table.ROW_FLAG_SELECTED) == 0:
                self.i_cur_row = None

            self.i_cur_row_prev = self.i_cur_row
            ws = self.size[2]
            x0 = self.pos[0]
            # Поиск колонки, которую кликнули
            for i_column in range(len(self._rows[0])):
                x1 = x0 + ws[i_column]
                if x0 < event.x < x1:
                    self.i_cur_column = i_column
                    break
                x0 += ws[i_column]
        elif event.type == gtk.gdk._2BUTTON_PRESS:
            self.on_2button_press(self, event)
        # Вызвать обработчик перемещения курсора
        if (prev_i_cur_row != self.i_cur_row) or ((self.i_cur_row is not None) and focus_changed) or sel_changed:
            if self.on_sel_change is not None:
                self.on_sel_change(self)
        self.put_to_redraw()
        return False

    def redraw(self):
        glNewList(self.dl, GL_COMPILE)
        # Таблица
        i_cur_row = None
        if self.i_cur_row is not None:
            i_cur_row = self.i_cur_row - self.view_begin
        gltools.draw_table2(self.pos,
                            self._rows[0],
                            self._rows[self.view_begin + 1: self.view_begin + 1 + self.view_max],
                            self.font,
                            self.color_proc,
                            self.bg_color_proc,
                            self._rows_flags[self.view_begin + 1: self.view_begin + 1 + self.view_max],
                            self.size[2],  # Ширины колонок
                            i_cur_row,
                            self.line_width,
                            focus=self.focus)

        # Индикаторы не отображаемых строк таблицы:
        x0 = self.pos[0] + self.line_width - 1  # левая координата x
        y0 = self.pos[1] + self.font.get_text_hight() + self.line_width * 2  # верхняя координата y
        x1 = self.pos[0] - self.line_width + self.size[0] - 1  # правая координата x
        y1 = self.pos[1] + self.size[1] - self.line_width * 2  # нижняя координата y
        # :верхних строк
        if (self.view_begin + 1) > 1:
            gltools.draw_line((x0, y0), (x1, y0), colors.GREEN, self.line_width)
        # :нижних строк
        if (self.view_begin + 1 + self.view_max) < len(self._rows):
            gltools.draw_line((x0, y1), (x1, y1), colors.GREEN, self.line_width)
        glEndList()

    def connect(self):
        if self.ehid1 is None:
            self.pc.append(('ehid1', safe_connect, 'button-press-event', self._on_mbutton_press))

    def disconnect(self):
        self.pc.append(('ehid1', safe_disconnect))
        self.focus = False
        self.pc.append(('ehid2', safe_disconnect))
        self.entry.hide()
        self.pc.append('ehid_kp', safe_disconnect)
