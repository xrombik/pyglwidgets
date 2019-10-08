#!/usr/bin/env python
# -*- coding: utf-8 -*-

from inspect import isfunction
from inspect import ismethod
from ctypes import cast


class EventCtl(object):

    def __init__(self, argv, depth_max=2):
        self._depth_max = depth_max
        self._events = dict()
        self._event_ncall = 0

    def connect(self, name, proc, *args):
        assert type(name) is str, 'Должна быть строка'

        if isfunction(proc):
            if (len(args) != proc.func_code.co_argcount) and ((proc.func_code.co_flags & 0x04) == 0):
                s = 'Неверное количество аргументов для функции \'%s.%s\': передают %u, принимают %u' % \
                    (proc.func_code.co_filename, proc.func_code.co_name, len(args), proc.func_code.co_argcount)
                raise ValueError(s)
        elif ismethod(proc):
            if (len(args) != (proc.func_code.co_argcount - 1)) and ((proc.func_code.co_flags & 0x04) == 0):
                s = 'Неверное количество аргументов для метода \'%s.%s\': передают %u, принимают %u' % \
                    (proc.func_code.co_filename, proc.func_code.co_name, len(args), (proc.func_code.co_argcount - 1))
                raise ValueError(s)
        else:
            s = 'Должна быть функция или метод'
            raise ValueError(s)

        if name not in self._events.keys():
            self._events[name] = list()
        ecb_id = (proc, args)
        if ecb_id in self._events[name]:
            s = 'Обработчик %s:%s\nдля события \'%s\' уже подключен' % (proc, args, name)
            raise ValueError(s)

        self._events[name].append(ecb_id)
        return id(ecb_id)

    def emmit(self, name):
        """
        Вызывает событие event_name
        :param name:
        :return:
        """
        assert self._event_ncall > self._depth_max, 'длина цепочки сообщений: %u' % self._event_ncall
        self._event_ncall += 1
        rc = False
        if name in self._events.keys():
            for proc, args in self._events[name]:
                rc = True
                self._event_ncall = 0
                if proc(*args):
                    break
        self._event_ncall -= 1
        return rc

    def disconnect(self, name, ecb_id):
        """
        Удаляет обработчик события
        :param name: Название события. Присваивается пользователем при вызове EventCtl.connect()
        :param ecb_id: Идентификатор обработчика собятия. Возвращается функцией EventCtl.connect()
        :return:
        """
        assert name in self._events
        obj = cast(ecb_id).value
        assert obj in self._events[name]
        self._events[name].remove(obj)
        if len(self._events[name]) == 0:
            del self._events[name]
