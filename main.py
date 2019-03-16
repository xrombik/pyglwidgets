#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glwidgets
import gtk
import glib


def btn0_proc(btn):
    print('button state is: %u' % btn.state)


def on_realize(gda, items):
    # GTK aware begin
    glwidgets.aware_gtk_begin(gda)

    # Widgets creation
    txrs = glwidgets.textures_from_files('./data/btn%u.png', 2)
    btn0 = glwidgets.Button(gda, (100, 100), 'Hi, there!', txrs, user_proc=btn0_proc)
    items.append(btn0)

    # GTK aware end
    glwidgets.aware_gtk_end(gda, 'on_realize()')


def on_draw(_gda, _event, items):
    glwidgets.GlWidget.redraw_queue()
    map(lambda item: item.draw(), items)
    glwidgets.glFlush()


def on_timer(gda):
    rect = gtk.gdk.Rectangle(0, 0, gda.allocation.width, gda.allocation.height)
    gda.window.invalidate_rect(rect, True)
    return True


items = list()
gda = glwidgets.create_drawning_area(640, 480, on_realize, on_draw, items)
glib.timeout_add(100, on_timer, gda)
gtk.main()
