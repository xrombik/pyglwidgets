#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Чужие модули
import cairo
import inspect

from .glimports import *

DEFAULT_FONT_FACE = 'Liberation Sans'
DEFAULT_FONT_SIZE = 18
DEFAULT_RATE_MS = 150
DEFAULT_DPI = 96

_ehid = None


def _empty_key_handler_proc(_window, _event, *_key_handler_args):
    """
    Пустая процедура ввода с клавиатуры
    :param window:
    :param event:
    :param key_handler_args:
    :return:
    """
    pass


key_handler_proc = _empty_key_handler_proc
key_handler_args = list()
TEST_STR0 = u'Южно-эфиопский грач увёл мышь за хобот на съезд ящериц\nBrown fox jumps ower the lazy dog\n0987654321\\(){}-+=.,:;?!'


def init(wdgt):
    global _ehid
    _ehid = wdgt.connect('key-press-event', key_dispatcher)


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
    width0 = int(width + 0.5)
    x = int(pos[0] + (width - xadvance) * cpx + 0.5)
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
    width0 = int(width - width * cpx + 0.5)
    x = int(pos[0] + width * cpx + 0.5)
    return width0, x


def key_dispatcher(window, event):
    if key_handler_args is None:
        key_handler_proc(window, event)
        return False
    key_handler_proc(window, event, *key_handler_args)
    return False


# Реализация декоратора "@private" для встроенных в класс функций
# http://blog.sujeet.me/2012/10/python-tinkering-a-decorator-to-implement-private-methods-I.html
def private(method):
    class_name = inspect.stack()[1][3]

    def privatized_method(*args, **kwargs):
        call_frame = inspect.stack()[1][0]
        # Only methods of same class should be able to call
        # private methods of the class, and no one else.
        if call_frame.f_locals.has_key('self'):
            caller_class_name = call_frame.f_locals['self'].__class__.__name__
            if caller_class_name == class_name:
                return method(*args, **kwargs)
        raise Exception("can't call private method")

    return privatized_method


def connect_key_handler(handler_proc, *args):
    """
    :param handler_proc: процедура для обработки нажатия клавиши
    :param args: аргументы передаваемые в процедуру handler_proc
    """
    global key_handler_proc, key_handler_args
    key_handler_proc = handler_proc
    key_handler_args = args


def disconnect_key_handler():
    global key_handler_proc, key_handler_args
    key_handler_proc = _empty_key_handler_proc
    key_handler_args = None


def get_key_handler():
    return key_handler_proc, key_handler_args


def cc_draw_text_shadow(cc, text, ybearing):
    shadow_col = (0.0, 0.0, 0.0, 1.0)
    # тень справо
    cc.set_source_rgba(*shadow_col)
    cc.move_to(2, -ybearing + 1)
    cc.show_text(text)
    # тень внизу
    cc.set_source_rgba(*shadow_col)
    cc.move_to(1, -ybearing + 2)
    cc.show_text(text)
    # тень слево
    cc.set_source_rgba(*shadow_col)
    cc.move_to(0, -ybearing + 1)
    cc.show_text(text)
    # тень сверху
    cc.set_source_rgba(*shadow_col)
    cc.move_to(1, -ybearing)
    cc.show_text(text)
    return 1, 1


def clear_cairo_surface(cc):
    cc.save()
    cc.set_source_rgba(0, 0, 0, 0)
    cc.set_operator(cairo.OPERATOR_SOURCE)
    cc.paint()
    cc.set_operator(cairo.OPERATOR_OVER)
    cc.restore()


# noinspection PyAttributeOutsideInit
class GlWidget(object):
    image_surface0 = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)
    cairo_context = cairo.Context(image_surface0)
    cairo_context.select_font_face(DEFAULT_FONT_FACE)
    cairo_context.set_font_size(DEFAULT_FONT_SIZE)
    items_queue = dict()
    on_timer = None

    __slots__ = ('pos', 'color', 'z', 'dl', 'draw', '_pos', '_color', 'pc')

    @staticmethod
    def redraw_queue():
        items = GlWidget.items_queue.values()
        for item in items:
            item.redraw()
        GlWidget.items_queue.clear()

    def __new__(cls, *args, **kwargs):
        cls.draw = cls._draw_list
        cls.z = 0
        """ Глубина на которой оторбражается элемент. Чем больше, тем ближе к наблюдателю """
        cls._color = [255, 255, 255, 255]
        cls._pos = [0, 0]
        obj = super(GlWidget, cls).__new__(cls)
        obj.dl = glGenLists(1)
        obj.pc = list()
        """ Отложенные вызовы подключения/отключения """
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
        GlWidget.items_queue[id(self)] = self
        GlWidget.on_timer()

    def _draw_list(self):
        glCallList(self.dl)

    def hide(self):
        if self.draw == self._draw_list:
            self.disconnect()
            self.draw = self._draw_none

    # noinspection PyAttributeOutsideInit
    def show(self):
        """
        Элемент для которого show() был вызван последним, находится в фокусе,
        если использует key_handler_...
        :return:
        """
        if self.draw == self._draw_none:
            self.connect()
            self.draw = self._draw_list

    def dopc(self, gda):
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
        if self_id in GlWidget.items_queue:
            del GlWidget.items_queue[self_id]
        glDeleteLists(self.dl, 1)

    def _draw_none(self): pass

    def disconnect(self): pass

    def connect(self): pass

