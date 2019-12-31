#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import glib
from glwidget import GlWidget
from glwidgets import glwidget
from .glimports import *
from gltools import opengl_init
from gltools import check_glerrors


__name__ = 'gtkgl driver'
__all__ = ('DrawDriver', 'safe_connect', 'safe_disconnect')


def safe_disconnect(obj, ehid):
    assert isinstance(obj, gtk.DrawingArea)
    assert isinstance(ehid, (long, int, type(None)))
    if ehid is not None:
        if obj.handler_is_connected(ehid):
            obj.disconnect(ehid)
            ehid = None
    return ehid


def safe_connect(obj, ehid, name, proc, *args):
    assert isinstance(obj, gtk.DrawingArea)
    assert isinstance(ehid, (long, int, type(None)))
    if ehid is None:
        ehid = obj.connect(name, proc, *args)
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


class DrawDriver(gtk.Window):
    def __init__(self, title, w, h, argv=None):
        super(DrawDriver, self).__init__()
        display_mode = gtk.gdkgl.MODE_RGBA | gtk.gdkgl.MODE_MULTISAMPLE  # gtk.gdkgl.MODE_DEPTH | gtk.gdkgl.MODE_DOUBLE
        events_mask = gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.KEY_PRESS_MASK | gtk.gdk.KEY_RELEASE_MASK
        gda = gtk.DrawingArea()
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
        GlWidget.on_redraw = self.on_timer

    def set_uninit(self, on_uninit, *args):
        self.connect('unrealize', lambda gda: on_uninit(self, *args))

    def uninit(self):
        self.stop_anim()
        gda = self.get_child()  # type: gtk.DrawingArea
        self.ehid1 = safe_disconnect(gda, self.ehid1)
        glDeleteLists(self.dl, 1)

    def init(self):
        gda = self.get_child()
        glwidget.init(self)
        opengl_init(gda)
        self.dl = glGenLists(1)
        assert glIsList(self.dl)

    def __del__(self):
        self.uninit()

    def start_anim(self, rate):
        if self.ehid0 is None:
            self.ehid0 = glib.timeout_add(rate, self.on_timer)

    def stop_anim(self):
        # type: () -> None
        if self.ehid0 is not None:
            glib.source_remove(self.ehid0)
            self.ehid0 = None

    def on_draw(self, gda, event, scm, redraw_queue):
        # type: (...) -> None
        if event.type != gtk.gdk.EXPOSE:
            return
        draw_begin(gda)
        for item in scm:
            item.dopc(gda)
        if scm.scene_changed:
            glNewList(self.dl, GL_COMPILE)
            for item in scm:
                item.draw()
            glEndList()
            scm.scene_changed = False

        redraw_queue()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glCallList(self.dl)
        scm.process_draw_callbacks()
        draw_end(gda, 'on_draw()')

    def set_scene(self, scm):
        gda = self.get_child()
        self.ehid1 = safe_disconnect(gda, self.ehid1)
        self.ehid1 = gda.connect('expose-event', self.on_draw, scm, GlWidget.redraw_queue)
        self.show_all()

    def set_init(self, on_init, *args):
        gda = self.get_child()
        gda.connect_after('realize', self.on_init, on_init, *args)

    def on_init(self, gda, on_init, *args):
        gtk.gdkgl.ext(gda.window)
        gda.gldrawable = gda.window.set_gl_capability(gda.glconfig)
        gda.glcontext = gtk.gdkgl.Context(gda.gldrawable)
        draw_begin(gda)
        self.init()
        on_init(*args)
        draw_end(gda, 'on_init()')

    def on_timer(self):
        # type: (DrawDriver) -> bool
        gda = self.get_child()
        rect = gtk.gdk.Rectangle(0, 0, gda.allocation.width, gda.allocation.height)
        gda.window.invalidate_rect(rect, True)
        return True
