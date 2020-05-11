#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .driver import safe_connect
from .driver import safe_disconnect

__all__ = ('Deffered', )


class Deffered(object):
    """
    Отработка отложенных вызовов в момент когда есть gda (gtk.DrawingArea)
    """
    __slots__ = ('dopc', 'pc')

    def __init__(self):
        self.pc = list()

    def dopc(self, gda):
        # type: (gtk.DrawingArea) -> None
        """
        :param gda: gtk.DrawingArea
        :return: None
        """
        dct = self.__dict__
        for val in self.pc:
            key = val[0]
            if len(val) > 2:
                dct[key] = val[1](gda, dct[key], *(val[2:]))
            else:
                dct[key] = val[1](gda, dct[key])
        del self.pc[:]

    def pc_connect(self, pname, event_name, proc):
        assert isinstance(pname, str)
        assert callable(proc)
        assert pname in self.__dict__
        self.pc.append((pname, safe_connect, event_name, proc))

    def pc_disconnect(self, pname):
        assert isinstance(pname, str)
        assert pname in self.__dict__
        self.pc.append((pname, safe_disconnect))
