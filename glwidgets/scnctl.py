#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime


class SceneCtl(list):

    def __init__(self, argv=None):
        super(SceneCtl, self).__init__()
        self.mode = None
        self._prev_mode = None
        self.fps = 25
        self.time_now = datetime.now()
        self.scene_changed = False
        self.dl = 0
        self.stack = list()

    @property
    def tick(self):
        time_now = self.time_now
        return (time_now.second * 1000) + (time_now.microsecond // 1000)

    def check(self):
        """
        Выпоняет санитарную проверку списка элемнтов сцены
        :return:
        """
        len_set = len(set(self))
        len_list = len(self)
        if len_set != len_list:
            self.sort()
            for item in self:
                if self.count(item) == 1:
                    continue
                print type(item),
                keys = dir(item)
                for k in keys:
                    if k not in ('text', 'pos'):
                        continue
                    print k, item.__getattribute__(k)
            raise ValueError('ошибка: обнаружено повторение элементов, всего %u\n' % (len_list - len_set))
        self.sort(key=lambda item: item.z)

    def hide_show(self, mode, mode_items):
        # type (SceneManager, str, dict) -> None
        """
        Прячет все элементы из списка items. Показывает элементы из
        словаря mode_items ключ которых равен mode. Ипользуется для
        изменения отображения элементов в заданных режимах программы.
        :param mode: Режим программы. Используется как ключ в словаре mode_items.
        :param mode_items: Словарь элементов для показа. Формат одной записи
        словаря {режим: (элемент0, элемент1, ...)}
        :return:
        """
        # Спрятать все
        for item in self:
            item.hide()

        # Показать только те, что нужны в режиме mode
        for key in mode_items:
            if type(key) is tuple:
                if mode not in key:
                    continue
            elif key != mode:
                continue
            for item in mode_items[key]:
                item.show()

    def add_scene_items(self, *items):
        """
        Добавляет элементы в сцену
        :param items: Список добавляемых элементов
        :return:
        """
        len_scene = len(self)
        for item in items:
            if item not in self:
                self.append(item)
        self.scene_changed = len(self) > len_scene
        return self.scene_changed

    def del_scene_item(self, *items):
        """
        Удаляет элементы из сцены
        :param items: Список удаляемых элементов
        :return:
        """
        len_scene = len(self)
        for item in self:
            if item in items:
                self.remove(item)
        self.scene_changed = len(self) < len_scene
        return self.scene_changed

    def goto_scene(self, items):
        self.stack.insert(0, list(self))
        self[:] = items[:]
        self.scene_changed = True

    def goto_back(self):
        self[:] = self.stack.pop(0)[:]
        self.scene_changed = True
