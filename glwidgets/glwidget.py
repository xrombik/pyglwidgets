#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Чужие модули
import cairo

from . import nevents
from evtctl import EventCtl
from .glimports import *

DEFAULT_RATE_MS = 150
TEST_STR0 = u'Южно-эфиопский грач увёл мышь за хобот на съезд ящериц\nBrown fox jumps ower the lazy dog\n0987654321\\(){}-+=.,:;?!'


__all__ = (
    'align_h_center',
    'align_h_left',
    'clear_cairo_surface',
    'DEFAULT_RATE_MS',
    'GlWidget')


def align_h_center(pos, width, xadvance, cpx):
    """
    Возвращает смещение по оси X, для выравнивания
    горизонтального по центру внутри заданной области
    :param pos: Точка верхнего левого угла области
    :param width: Ширина области
    :param xadvance: Ширина текста
    :param cpx: Относительная ширина оставляемого свободного места
    :return:
    """
    width0 = int(width)
    x = int(pos[0] + (width - xadvance) * cpx)
    if x < pos[0]: x = pos[0]
    return width0, x


def align_h_left(pos, width, _xadvance, cpx):
    """
    Возвращает смещение по оси X, для выравнивания горизонтального
    по левому краю внутри заданной области
    :param pos: Точка верхнего левого угла области
    :param width: Ширина области
    :param _xadvance: Ширина текста
    :param cpx: Относительная ширина оставляемого свободного места
    :return:
    """
    width0 = int(width - width * cpx)
    x = int(pos[0] + width * cpx)
    return width0, x


def clear_cairo_surface(cc):
    cc.save()
    cc.set_source_rgba(0, 0, 0, 0)
    cc.set_operator(cairo.OPERATOR_SOURCE)
    cc.paint()
    cc.set_operator(cairo.OPERATOR_OVER)
    cc.restore()


def redraw_queue(items_queue):
    # type: (dict) -> None
    items = items_queue.values()
    for item in items: item.redraw()
    items_queue.clear()


# noinspection PyAttributeOutsideInit
class GlWidget(object):
    items_queue = dict()
    on_redraw = None
    EventCtl().connect(nevents.EVENT_DRAW, redraw_queue, items_queue)

    def __new__(cls, *args, **kwargs):
        cls.draw = glCallList
        cls.z = 0
        """ Глубина на которой оторбражается элемент. Чем больше, тем ближе к наблюдателю """
        cls._color = [255, 255, 255, 255]
        cls._pos = [0, 0]
        obj = super(GlWidget, cls).__new__(cls)
        obj.dl = glGenLists(1)
        obj.pc = list()
        """ Отложенные вызовы подключения и отключения """
        assert glIsList(obj.dl)
        return obj

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, val):
        if self._pos == val: return
        self._pos = val
        self.put_to_redraw()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, val):
        if self._color == val: return
        self._color = val
        self.put_to_redraw()

    def put_to_redraw(self):
        """
        Заносит текущий экземпляр в очередь на перерисовку
        :return: Ничего
        """
        items_queue = GlWidget.items_queue
        l1 = len(items_queue)
        items_queue[id(self)] = self
        if l1 < len(items_queue):
            EventCtl().emmit(nevents.EVENT_REDRAW)

    def hide(self):
        if self.draw == glCallList:
            self.disconnect()
            self.draw = self._draw_none

    # noinspection PyAttributeOutsideInit
    def show(self):
        if self.draw == self._draw_none:
            self.connect()
            self.draw = glCallList

    def dopc(self, gda):
        """
        Отработка отложенных вызовов в момент когда есть gda (gtk.DrawingArea)
        :param gda:
        :return:
        """
        # TODO: in python3 it should be: "for key, proc, *args in self.pc:"
        for val in self.pc:
            key = val[0]
            dct = self.__dict__
            if len(val) > 2:
                dct[key] = val[1](gda, dct[key], *(val[2:]))
            else:
                dct[key] = val[1](gda, dct[key])
        del self.pc[:]

    def __del__(self):
        self.disconnect()
        self_id = id(self)
        try: del GlWidget.items_queue[self_id]
        except KeyError: pass
        glDeleteLists(self.dl, 1)

    @staticmethod
    def _draw_none(dl): pass

    def disconnect(self): pass

    def connect(self): pass
