#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import glwidgets


def main(argv):
    pgm = glwidgets.ProgramCtl(argv)
    scm = glwidgets.SceneCtl(argv)
    rcm = glwidgets.ResourceCtl(argv)
    ddrv = glwidgets.DrawDriver(argv, 'pyglwidgets', 640, 480)
    ddrv.set_init(on_init, scm, rcm)
    ddrv.set_scene(scm)
    ddrv.start_anim(50)
    pgm.run()


def btn0_proc(btn0):
    print(u'состояние кнопки: %u' % btn0.state)
    img0 = btn0.user_data
    img0.move(10, 0)


def on_init(gda, scm, rcm):
    # type: (gtk.DrawingArea, glwidgets.SceneCtl, glwidgets.ResourceCtl) -> None
    glwidgets.aware_gtk_begin(gda)

    scm.on_init()

    txrs = rcm.get_textures('btn%u.png', 2)
    txr_ship = rcm.get_texture('F5S4.png')

    btn0 = glwidgets.Button(gda, (100, 100), 'Эй, вы!', txrs, user_proc=btn0_proc)
    img0 = glwidgets.Picture((100, 200), txr_ship)
    btn0.user_data = img0

    scm.add_scene_items(btn0, img0)

    # GTK aware end
    glwidgets.aware_gtk_end(gda, 'on_realize()')


if __name__ == "__main__":
    import sys
    main(argv=sys.argv)
