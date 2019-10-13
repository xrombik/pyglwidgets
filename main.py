#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glwidgets import *


def main(argv):
    pgm = ProgramCtl(argv)
    scm = SceneCtl(argv)
    rcm = ResourceCtl(argv)
    ddr = DrawDriver(argv, 'pyglwidgets', 640, 480)
    ddr.set_init(on_init, scm, rcm)
    ddr.set_uninit(on_uninit, pgm, rcm)
    ddr.set_scene(scm)
    pgm.run()


def on_uninit(ddr, pgm, rcm):
    # type: (DrawDriver, ProgramCtl, SceneCtl) -> None
    rcm.uninit()
    ddr.uninit()
    pgm.uninit()
    check_glerrors('on_uninit():')


def on_init(gda, scm, rcm):
    # type: (gtk.DrawingArea, SceneCtl, ResourceCtl) -> None

    font = rcm.get_ft_font()
    txt0 = DynamicText(font, (10, 20), u'Кнопки, картинки и текст')

    txr_btn = rcm.get_textures('btn%u.png', 2)
    txr_ship = rcm.get_texture('merhn2.png')

    img0 = Picture((50, 200), txr_ship)
    col0 = (255, 0, 0, 255)
    col1 = (255, 255, 255, 255)
    btn0 = Button(gda, (50, 100), 'КРАСНЫЙ', txr_btn, user_proc=btn0_proc, user_data=(img0, col0, col1))

    scm.add_scene_items(btn0, img0, txt0)


def btn0_proc(btn0):
    # type: (Button) -> None
    img0 = btn0.user_data[0]
    col0 = btn0.user_data[1]
    col1 = btn0.user_data[2]
    if btn0.state:
        img0.color = col0
    else:
        img0.color = col1


if __name__ == '__main__':
    import sys
    main(sys.argv)
