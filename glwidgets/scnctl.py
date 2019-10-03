#!/usr/bin/env python
# -*- coding: utf-8 -*-


from datetime import datetime
import inspect

# Свои модули
from . import glwidget
from .glimports import *


class SceneCtl(object):
    def __init__(self, argv):
        self.dl = 0
        self.scene = list()
        self.mode = None
        self._prev_mode = None
        self.fps = 25
        self.modules = list()
        self.mode_change_callbacks = list()
        self.draw_callbacks = list()
        self.time_now = datetime.now()
        self.tick = 0
        self.update_tick()
        self._events = dict()
        self._event_ncall = 0
        self.scene_changed = True

    def on_init(self):
        self.dl = glGenLists(1)
        assert glIsList(self.dl)

    def __del__(self):
        glDeleteLists(self.dl, 1)

    def update_tick(self):
        """
        Обновляет текущее значение тик-времени в мс
        """
        self.tick = (self.time_now.second << 10) | (self.time_now.microsecond >> 10) % 65535

    def check(self):
        """
        Выпоняет санитарную проверку списка элемнтов сцены
        :return:
        """
        len_set = len(set(self.scene))
        len_list = len(self.scene)
        if len_set != len_list:
            self.scene.sort()
            for item in self.scene:
                if self.scene.count(item) == 1:
                    continue
                print type(item),
                keys = dir(item)
                for k in keys:
                    if k not in ('text', 'pos'):
                        continue
                    print k, item.__getattribute__(k)
            raise ArgumentError('ошибка: обнаружено повторение элементов, всего %u\n' % (len_list - len_set))
        self.scene.sort(key=lambda item: item.z)

    def hide_show(self, mode, mode_items):
        # type (SceneManager, str, dict) -> None
        """
        Прячет все элементы из списка items. Показывает элементы из
        словаря mode_items ключ которых равен mode. Ипользуется для
        изменения отображения элементов в разных режимах программы.
        :param items: Список элементов для прятанья
        :param mode: Режим программы. Используется как ключ в словаре mode_items.
        :param mode_items: Словарь элементов для показа. Формат одной записи
        словаря {режим: (элемент0, элемент1, ...)}
        :return:
        """
        # Спрятать все
        map(lambda item: item.hide(), self.scene)

        # Показать только те, что нужны в режиме mode
        for key in mode_items:
            if type(key) is tuple:
                if mode not in key:
                    continue
            elif key != mode:
                continue
            # TODO: Избавиться от использования этого поля
            if 'enable' in item.__dict__:
                for item in mode_items[key] and item.enable:
                    item.show()
            else:
                for item in mode_items[key]:
                    item.show()

    def add_scene_items(self, *items):
        """
        Добавляет элементы в сцену
        :param item:
        :return:
        """
        len_scene = len(self.scene)
        items = filter(lambda item: item not in self.scene, items)
        map(lambda item: self.scene.append(item), items)
        self.scene_changed = True
        return len(self.scene) > len_scene

    def del_scene_item(self, *items):
        """
        Удаляет элементы из сцены
        :param item:
        :return:
        """
        len_scene = len(self.scene)
        items = filter(lambda item: item in self.scene, items)
        map(lambda item: self.scene.remove(item), items)
        self.scene_changed = True
        return len(self.scene) < len_scene

    def add_mode_change_callback(self, callback, *args):
        """
        Добавляет пользовательский обработчик смены режима программы
        :param callback: Процедура которая будет вызвана при смене режима
        :param args: Аргументы передаваемые в процедуру
        :return: Идентификатор обработчика
        """
        assert inspect.isfunction(callback)
        if (len(args) != (callback.func_code.co_argcount - 2)) and ((callback.func_code.co_flags & 0x04) == 0):
            print(
            'Неверное количество аргументов для функции \'%s.%s\': передают %u, принимают %u (2 по умолчанию всегда есть)'
            % (callback.func_code.co_filename, callback.func_code.co_name, len(args), callback.func_code.co_argcount))
            raise ValueError
        mcc_id = callback, args
        if mcc_id not in self.mode_change_callbacks:
            self.mode_change_callbacks.append(mcc_id)
        return mcc_id

    def del_mode_change_callback(self, mcc_id):
        """
        Удаляет пользовательский обработчик смены режима программы
        :param mcc_id: Идентификатор обработчика возвращаемый P16GuiData.add_mode_change_callback
        :return:
        """
        len_dc = len(self.draw_callbacks)
        if mcc_id in self.mode_change_callbacks:
            self.mode_change_callbacks.remove(mcc_id)
        return len_dc > len(self.mode_change_callbacks)

    def add_draw_callback(self, callback, *args):
        """
        Добавляет пользовательский обработчик перерисовки
        :param callback: Процедура которая будет вызвана для перерисовки
        :param args: Аргументы передаваемые в процедуру
        :return: Идентификатор в обработчика в списке
        """
        assert inspect.isfunction(callback)  # callback - должно быть функцией
        cb_id = callback, args
        if cb_id not in self.draw_callbacks:
            self.draw_callbacks.append(cb_id)
        return cb_id

    def del_draw_callback(self, cb_id):
        """
        Удаляет пользовательскую процедуру рисования.
        :param cb_id: Идентификатор пользовательской процедуры рисования,
        возвращаемый P16GuiData.add_draw_callback
        :return:
        """
        l0 = len(self.draw_callbacks)
        if cb_id in self.draw_callbacks:
            self.draw_callbacks.remove(cb_id)
        return l0 > len(self.draw_callbacks)

    def process_draw_callbacks(self):
        for item in self.draw_callbacks:
            item[0](self, *item[1])
        return len(self.draw_callbacks)

    def set_mode(self, mode):
        if self.mode != mode:
            for callback in self.mode_change_callbacks:
                callback[0](self, mode, *callback[1])
            self._prev_mode = self.mode
            self.mode = mode

    def set_prev_mode(self):
        self.set_mode(self._prev_mode)
