#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glwidgets import *
from datetime import datetime


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


def on_init(scm, rcm):
    # type: (SceneCtl, ResourceCtl) -> None

    font = rcm.get_ft_font()
    txt0 = DynamicText(font, (10, 20), u'Жми кнопку!')

    txr_btn = rcm.get_textures('btn%u.png', 2)
    txr_ship = rcm.get_texture('merhn2.png')

    rows = [['Номер', 'Цвет',         'Длина', 'Ширина'],
            ['1',     'Красный',      '30',    '180'],
            ['2',     'Синий',        '50',    '100'],
            ['3',     'Фиолетовый',   '60',    '200']]

    tbl0 = Table((200, 150), rows)
    tbl0.widths[1] = 120

    img0 = Picture((20, 200), txr_ship)
    col0 = (255, 0, 0, 255)
    col1 = (255, 255, 255, 255)
    btn0 = Button((50, 100), 'auto_width', txr_btn, user_proc=btn0_proc, user_data=(img0, col0, col1, txt0, tbl0))

    entry0 = Entry((200, 100), rows[1][0])
    entry0.user_data = tbl0
    entry0.on_edit_done = on_entry_edit_done
    
    scm.add_scene_items(btn0, img0, txt0, entry0, tbl0)


def on_entry_edit_done(entry0):
    tbl0 = entry0.user_data
    rows = tbl0.get_rows()
    rows[1][0] = entry0.text
    tbl0.set_rows(rows)
    

def btn0_proc(btn0):
    # type: (Button) -> None
    img0 = btn0.user_data[0]  # type: Picture
    col0 = btn0.user_data[1]  # type: tuple
    col1 = btn0.user_data[2]  # type: tuple
    txt0 = btn0.user_data[3]  # type: DynamicText
    tbl0 = btn0.user_data[4]  # type: Table
    tbl0.auto_widths = btn0.state
    img0.color = (col1, col0)[btn0.state]
    txt0.set_text(u'Кнопка нажата в:\n%s' % datetime.now())

if __name__ == '__main__':
    import sys
    main(sys.argv)
