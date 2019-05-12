#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import glib
import gtk
import glwidgets

saved_exception_hook = function()


def main(argv):
    global saved_exception_hook
    saved_exception_hook = sys.excepthook
    sys.excepthook = exception_hook
    scm = glwidgets.SceneCtl()
    rcm = glwidgets.ResourceCtl()
    gda = glwidgets.create_drawning_area(640, 480, on_realize, on_draw, scm, rcm)
    glib.timeout_add(1000 / scm.fps, on_timer, gda, scm)
    gtk.main()


def btn0_proc(btn0):
    print('button state is: %u' % btn0.state)
    img0 = btn0.user_data
    img0.move(10, 0)


def on_realize(gda, scm, rcm):
    # type: (gtk.DrawingArea, glwidgets.SceneCtl, glwidgets.ResourceCtl) -> None
    glwidgets.aware_gtk_begin(gda)

    scm.on_realize()

    txrs = rcm.get_textures('btn%u.png', 2)
    btn0 = glwidgets.Button(gda, (100, 100), 'Hi, there!', txrs, user_proc=btn0_proc)

    txr_ship = rcm.get_texture('F5S4.png')
    img0 = glwidgets.Picture((100, 200), txr_ship)
    btn0.user_data = img0

    scm.add_scene_items(btn0, img0)

    # GTK aware end
    glwidgets.aware_gtk_end(gda, 'on_realize()')


def on_draw(_gda, _event, scm, rcm):
    # type: (gtk.DrawingArea, glwidgets.SceneCtl, glwidgets.ResourceCtl) -> None
    scm.on_draw()


def on_timer(gda, sm):
    # type: (gtk.DrawingArea, glwidgets.SceneCtl, glwidgets.ResourceCtl) -> bool
    rect = gtk.gdk.Rectangle(0, 0, gda.allocation.width, gda.allocation.height)
    gda.window.invalidate_rect(rect, True)
    sm.update_tick()
    return True


def exception_hook(etype, evalue, etb):
    saved_exception_hook(etype, evalue, etb)  # type: function
    print('%s:\n- Завершается из за возникновения исключения.' % __file__)
    quit(1)


if __name__ == "__main__":
    main(argv=sys.argv)
