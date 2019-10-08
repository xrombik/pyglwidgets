#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glwidgets import *


def main(argv):
    pgm = ProgramCtl(argv)
    scm = SceneCtl(argv)
    rcm = ResourceCtl(argv)
    ddr = DrawDriver(argv, 'pyglwidgets', 640, 480)
    ddr.set_init(on_init, scm, rcm, ddr)
    ddr.set_uninit(on_uninit, pgm, rcm)
    ddr.set_scene(scm)
    pgm.run()


def on_uninit(ddr, pgm, rcm):
    # type: (DrawDriver, ProgramCtl, SceneCtl) -> None
    rcm.uninit()
    ddr.uninit()
    pgm.uninit()
    check_glerrors('on_uninit():')


def on_init(gda, scm, rcm, ddr):
    # type: (gtk.DrawingArea, SceneCtl, ResourceCtl) -> None
    aware_gtk_begin(gda)

    ddr.init()

    font = rcm.get_ft_font()
    txt0 = DynamicText(font, (10, 20), u'Кнопки, картинки и текст')

    txr_btn = rcm.get_textures('btn%u.png', 2)
    txr_ship = rcm.get_texture('F5S4.png')

    img0 = Picture((100, 200), txr_ship)
    btn0 = Button(gda, (50, 100), 'ВЛЕВО', txr_btn, user_proc=btn0_proc, user_data=(img0, -10))
    btn1 = Button(gda, (450, 100), 'ВПРАВО', txr_btn, user_proc=btn0_proc, user_data=(img0, 10))

    scm.add_scene_items(btn0, img0, txt0, btn1)

    # GTK aware end
    aware_gtk_end(gda, 'on_init()')


def btn0_proc(btn0):
    # type: (Button) -> None
    img0 = btn0.user_data[0]
    step = btn0.user_data[1]
    img0.move(step, 0)


if __name__ == '__main__':
    import sys
    main(sys.argv)
