#!/usr/bin/env python
# -*- coding: utf-8 -*-


from glwidgets import *
from datetime import datetime


def main():
    app = Candy('pyglwidgets demo', 640, 480, on_init)
    app.run()


def on_init(scm, rcm, _app):
    # type: (SceneCtl, ResourceCtl, Candy) -> None
    """
    :param scm: Scene manager
    :param rcm: Resource manager
    :param _app: Program starter
    :return:
    """

    font = rcm.get_ft_font()
    txt0 = DynamicText(font, (10, 20), u'Push the button!')

    txr_btn = rcm.get_textures('btn%u.png', 2)
    txr_ship = rcm.get_texture('star.png')

    rows = [['Number', 'Color',  'Lenght'],
            ['1',      'red',    '30'],
            ['2',      'blue',   '50'],
            ['3',      'violet', '60']]

    tbl0 = Table((200, 150), rows)
    tbl0._widths[1] = 120

    img0 = Picture((20, 200), txr_ship)
    col0 = (255, 0, 0, 255)
    col1 = (255, 255, 255, 255)
    btn0 = Button((50, 100), 'auto_width', txr_btn, user_proc=btn0_proc, user_data=(img0, col0, col1, txt0, tbl0))

    entry0 = Entry((200, 70), rows[1][0])
    entry0.user_data = tbl0
    entry0.on_edit_done = on_entry_edit_done

    txt_reg = TextRegulator((200, 110))

    scm.add_scene_items(btn0, img0, txt0, entry0, txt_reg, tbl0)


def on_entry_edit_done(entry0):
    # type: (Entry) -> None
    tbl0 = entry0.user_data  # type: Table
    rows = tbl0.get_rows()  # type: list
    rows[1][0] = entry0.text  # type: str
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
    txt0.set_text(u'Button pressed at:\n%s' % datetime.now())


if __name__ == '__main__':
    main()
