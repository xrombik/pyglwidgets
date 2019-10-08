#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glwidgets import *


def main(argv):
    pgm = ProgramCtl(argv)
    scm = SceneCtl(argv)
    rcm = ResourceCtl(argv)
    drd = DrawDriver(argv, 'pyglwidgets', 640, 480)
    drd.set_init(on_init, scm, rcm, drd)
    drd.set_uninit(on_uninit, pgm, rcm)
    drd.set_scene(scm)
    pgm.run()


def on_uninit(drd, pgm, rcm):
    # type: (DrawDriver, ProgramCtl, SceneCtl) -> None
    rcm.uninit()
    drd.uninit()
    pgm.uninit()
    check_glerrors('on_uninit():')


def on_init(gda, scm, rcm, drd):
    # type: (gtk.DrawingArea, SceneCtl, ResourceCtl) -> None
    aware_gtk_begin(gda)

    drd.init()

    font = rcm.get_ft_font()
    txt0 = DynamicText(font, (10, 20), u'Твари сраные')

    txr_btn = rcm.get_textures('btn%u.png', 2)
    txr_ship = rcm.get_texture('F5S4.png')

    btn0 = Button(gda, (100, 100), 'Эй, вы!', txr_btn, user_proc=btn0_proc)
    img0 = Picture((100, 200), txr_ship)
    btn0.user_data = img0

    scm.add_scene_items(btn0, img0, txt0)

    # GTK aware end
    aware_gtk_end(gda, 'on_init()')


def btn0_proc(btn0):
    # type: (Button) -> None
    print(u'состояние кнопки: %u' % btn0.state)
    img0 = btn0.user_data
    img0.move(10, 0)


if __name__ == "__main__":
    import sys
    main(sys.argv)
