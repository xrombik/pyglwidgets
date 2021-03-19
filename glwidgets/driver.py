#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import glib
import inspect
import typing

from . import nevents
from evtctl import EventCtl
from .glimports import *
from gltools import opengl_init
from gltools import check_glerrors

__name__ = 'gtkgl driver'
__all__ = ('DrawDriver', 'safe_disconnect', 'safe_connect')


def map_keyval(keyval):
    # type: (int) -> typing.Tuple[int, str]
    """
    Преобразовывает данные события в распознаваемые константы
    :param keyval:
    :return:
    """
    return gtk.gdk.keyval_to_unicode(keyval), gtk.gdk.keyval_name(keyval)


def safe_disconnect(obj, ehid):
    assert isinstance(obj, gtk.DrawingArea)
    assert isinstance(ehid, (long, int, type(None)))
    if ehid is not None:
        if obj.handler_is_connected(ehid):
            obj.disconnect(ehid)
            return None
        window = obj.get_parent()  # type: gtk.Window
        if window.handler_is_connected(ehid):
            window.disconnect(ehid)
            return None
    return ehid


def safe_connect(obj, ehid, event_name, proc, *args):
    assert isinstance(obj, gtk.DrawingArea)
    assert isinstance(ehid, (long, int, type(None)))
    if ehid is None:
        ehid = obj.connect(event_name, proc, *args)
    return ehid


def aware_gtk_begin1(gda):
    gtk.gdkgl.ext(gda.window)
    gda.gldrawable = gda.window.set_gl_capability(gda.glconfig)
    gda.glcontext = gtk.gdkgl.Context(gda.gldrawable)


def draw_begin(gda):
    gda.gldrawable.wait_gdk()
    gda.gldrawable.gl_begin(gda.glcontext)


def draw_end(gda, s):
    glFlush()
    check_glerrors(s)
    gda.gldrawable.wait_gl()
    gda.gldrawable.gl_end()


class DrawingAreaProxy(gtk.DrawingArea):
    def __init__(self, *args, **kwargs):
        super(DrawingAreaProxy, self).__init__(*args, **kwargs)
        self.ehid = None

    def connect(self, event_name, proc, *args, **kwargs):
        if event_name == 'key-press-event':
            window = self.get_parent()  # type: gtk.Window
            return window.connect('key-press-event', proc, *args, **kwargs)
        return super(DrawingAreaProxy, self).connect(event_name, proc, *args, **kwargs)

    def disconnect(self, ehid):
        if ehid is None:
            return
        if self.ehid == ehid:
            window = self.get_parent()  # type: gtk.Window
            window.disconnect(ehid)
            return
        return super(DrawingAreaProxy, self).disconnect(ehid)


class Timer(object):
    def __init__(self, rate, proc, *args):
        assert callable(proc)
        assert isinstance(rate, int)
        self._proc = proc
        self._args = args
        self._rate = rate
        self._ehid = None

    def __del__(self):
        self.stop()

    @property
    def is_running(self):
        return self._ehid is not None

    def start(self):
        if self._ehid is not None:
            glib.source_remove(self._ehid)
        self._ehid = glib.timeout_add(self._rate, self._proc, self, *self._args)

    def stop(self):
        if self._ehid is not None:
            glib.source_remove(self._ehid)
            self._ehid = None


class DrawDriver(gtk.Window):

    def __init__(self, title, w, h):
        super(DrawDriver, self).__init__()
        display_mode = gtk.gdkgl.MODE_RGBA | gtk.gdkgl.MODE_MULTISAMPLE | gtk.gdkgl.MODE_DEPTH  # gtk.gdkgl.MODE_DOUBLE
        events_mask = gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.KEY_PRESS_MASK | gtk.gdk.KEY_RELEASE_MASK
        gda = DrawingAreaProxy()
        gda.set_double_buffered(False)
        gda.glconfig = gtk.gdkgl.Config(mode=display_mode)
        gda.set_size_request(w, h)
        gda.add_events(events_mask)
        self.add(gda)
        self.set_reallocate_redraws(True)
        self.set_title(title)
        self.ehid0 = None
        self.ehid1 = None
        self.dl = 0
        EventCtl().connect(nevents.EVENT_REDRAW, self.on_timer)

    def set_uninit(self, on_uninit, *args):
        assert inspect.isfunction(on_uninit)
        self.connect('unrealize', self.uninit, on_uninit, *args)

    @staticmethod
    def uninit(self, on_uninit, *args):
        gda = self.get_child()
        self.stop_anim()
        self.ehid1 = safe_disconnect(gda, self.ehid1)
        glDeleteLists(self.dl, 1)
        on_uninit(*args)

    def __del__(self):
        self.stop_anim()
        self.uninit()

    def start_anim(self, rate):
        if self.ehid0 is None:
            self.ehid0 = glib.timeout_add(rate, self.on_timer)

    def stop_anim(self):
        # type: () -> None
        if self.ehid0 is not None:
            glib.source_remove(self.ehid0)
            self.ehid0 = None

    def on_draw(self, gda, event, scm):
        # type: (...) -> None
        if event.type != gtk.gdk.EXPOSE:
            return
        draw_begin(gda)
        EventCtl().emmit(nevents.EVENT_DRAW)
        for item in scm: item.dopc(gda)
        if scm.scene_changed:
            glNewList(self.dl, GL_COMPILE)
            for item in scm: item.draw(item.dl)
            glEndList()
            scm.scene_changed = False
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glCallList(self.dl)
        draw_end(gda, 'on_draw()')

    def set_scene(self, scm):
        gda = self.get_child()
        self.ehid1 = safe_disconnect(gda, self.ehid1)
        self.ehid1 = gda.connect('expose-event', self.on_draw, scm)
        self.show_all()

    def set_init(self, on_init, *args):
        gda = self.get_child()
        gda.connect_after('realize', self.on_init, on_init, *args)

    def on_init(self, gda, on_init, *args):
        gtk.gdkgl.ext(gda.window)
        gda.gldrawable = gda.window.set_gl_capability(gda.glconfig)
        gda.glcontext = gtk.gdkgl.Context(gda.gldrawable)
        draw_begin(gda)
        opengl_init(gda.allocation.width, gda.allocation.height)
        self.dl = glGenLists(1)
        assert glIsList(self.dl)
        EventCtl().emmit(nevents.EVENT_INIT)
        on_init(*args)
        draw_end(gda, 'on_init()')

    def on_timer(self):
        # type: (DrawDriver) -> bool
        gda = self.get_child()  # type: gtk.DrawingArea
        rect = gtk.gdk.Rectangle(0, 0, gda.allocation.width, gda.allocation.height)
        gda.window.invalidate_rect(rect, True)
        return True
