#!/usr/bin/env python
# -*- coding: utf-8 -*-

# gtk + opengl driver

import gtk
import glib
from glwidget import GlWidget
from .glimports import *


class DrawDriver(gtk.Window):
    def __init__(self, argv, title, w, h):
        super(DrawDriver, self).__init__()
        display_mode = gtk.gdkgl.MODE_RGBA | gtk.gdkgl.MODE_MULTISAMPLE  #gtk.gdkgl.MODE_DEPTH | gtk.gdkgl.MODE_DOUBLE
        events_mask = gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.KEY_PRESS_MASK | gtk.gdk.KEY_RELEASE_MASK
        glconfig = gtk.gdkgl.Config(mode=display_mode)
        self.gda = gtk.DrawingArea()
        self.gda.set_double_buffered(False)
        self.gda.glconfig = glconfig
        self.gda.gldrawable = None
        self.gda.glcontext = None
        self.gda.set_size_request(w, h)
        self.gda.add_events(events_mask)
        self.set_reallocate_redraws(True)
        self.connect('delete-event', gtk.main_quit)
        self.set_title(title)
        self.add(self.gda)
        self.ehid0 = None
        self.ehid1 = None
        self.dl = 0
        GlWidget.on_timer = self.on_timer

    def on_init(self):
        self.dl = glGenLists(1)
        assert glIsList(self.dl)

    def __del__(self):
        glDeleteLists(self.dl, 1)

    def start_anim(self, rate):
        if self.ehid0 is None:
            self.ehid0 = glib.timeout_add(rate, self.on_timer)

    def stop_anim(self):
        if self.ehid0 is not None:
            glib.source_remove(self.ehid0)
            self.ehid0 = None

    def on_draw(self, gda, event, scm, redraw_queue):
        if scm.scene_changed:
            glNewList(self.dl, GL_COMPILE)
            map(lambda item: item.draw(), scm.scene)
            glEndList()
            scm.scene_changed = False

        redraw_queue()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glCallList(self.dl)
        scm.process_draw_callbacks()
        glFlush()

    def set_scene(self, scm):
        if self.ehid1 is not None:
            self.gda.disconnect(self.ehid1)
        self.ehid1 = self.gda.connect('expose-event', self.on_draw, scm, GlWidget.redraw_queue)
        self.show_all()

    def set_init(self, on_init, *args):
        self.gda.connect_after('realize', on_init, *args)

    def __del__(self):
        self.stop_anim()

    def on_timer(self):
        # type: (DrawDriver) -> bool
        rect = gtk.gdk.Rectangle(0, 0, self.gda.allocation.width, self.gda.allocation.height)
        self.gda.window.invalidate_rect(rect, True)
        return True
