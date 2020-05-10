#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glwidgets import *
from glwidgets import driver


def main():
    app = Candy('pyglwidgets demo', 640, 480, on_init)
    app.run()


def on_init(scm, rcm, app):
    # type: (SceneCtl, ResourceCtl, Candy) -> None
    """
    :param app: Program runner
    :param scm: Scene manager
    :param rcm: Resource manager
    :return:
    """
    font = rcm.get_ft_font()
    txt_header = StaticText((10, 40), 'SPACE INVIDERS', font)

    rows_keys = [
        ['ACTION',  'KEY'],
        ['LEFT',    'Left'],
        ['RIGHT',   'Right'],
        ['UP',      'Up'],
        ['DOWN',    'Down']]

    rows_opts = [
        ['OPTIONS', 'VALUE'],
        ['SOUND',   'On']]

    rows_score = [
        ['DATE',        'SCORE'],
        ['2020-04-01',  '1000'],
        ['2020-05-01',  '2000']]

    tbl_navi_stack = list()
    rows_menu = list()
    tbl_navi = Table((200, 150), rows_menu)
    tbl_navi.user_data = tbl_navi_stack
    tbl_navi.widths = [200]
    tbl_navi.i_cur_row = 0
    tbl_navi.bg_color_proc = bg_color_proc
    tbl_navi.focus = True

    txr_player = rcm.get_texture('player.png')
    pic_player = PictureRotate((320, 400), txr_player)

    EVENT_MENU, EVENT_GAME, EVENT_KEYS, EVENT_OPTS, EVENT_SCORE, EVENT_EXIT = range(6)

    scene_main = [(txt_header,  tbl_navi), rows_menu,  EVENT_MENU]
    scene_game = [(pic_player,),           list(),     EVENT_GAME]
    scene_keys = [(txt_header,  tbl_navi), rows_keys,  EVENT_KEYS]
    scene_opts = [(txt_header,  tbl_navi), rows_opts,  EVENT_OPTS]
    scene_score =[(txt_header,  tbl_navi), rows_score, EVENT_SCORE]
    scene_exit = [tuple(),                 list(),     EVENT_EXIT]

    rows_menu_data = [
        (['MAIN MENU'],      None),
        (['START NEW GAME'], scene_game),
        (['REDEFINE KEYS'],  scene_keys),
        (['OPTIONS'],        scene_opts),
        (['SCORE TABLE'],    scene_score),
        (['EXIT'],           scene_exit)]

    rows_menu[:] = map(lambda data_row: data_row[0], rows_menu_data)[:]

    ect = EventCtl()
    tbl_navi.connect(nevents.EVENT_KEY_PRESS, lambda *args: on_key_press(args[1].keyval, ect))
    scm.goto_scene(scene_main[0])
    ect.connect(EVENT_EXIT, app.uninit)
    ect.connect('Escape', on_key_escape, tbl_navi, app)
    ect.connect('Escape', scm.goto_back)
    ect.connect('Return', on_key_return, tbl_navi, rows_menu_data, scm, ect)
    ect.connect('Left', on_key_move, pic_player, 0, -10)
    ect.connect('Right', on_key_move, pic_player, 0, 10)
    ect.connect(nevents.EVENT_REDRAW, on_draw)

def on_draw(*args):
    print args


def on_key_move(pic_player, i, val):
    # type: (PictureRotate, int, int) -> None
    pic_player.pos[i] += val
    pic_player.put_to_redraw()


def on_key_press(keyval, ect):
    char_code, char_name = driver.map_keyval(keyval)
    ect.emmit(char_name)


def on_key_escape(tbl_navi, app):
    tbl_navi_stack = tbl_navi.user_data
    if len(tbl_navi_stack):
        rows, widths = tbl_navi_stack.pop()
        tbl_navi.set_rows(rows)
        tbl_navi.widths = widths
    else:
        app.uninit()


def on_key_return(tbl_navi, rows_menu_data, scm, ect):
    rows = tbl_navi.get_rows()
    widths = tbl_navi.widths
    tbl_navi_stack = tbl_navi.user_data
    tbl_navi_stack.insert(0, (rows, widths))
    i_row = tbl_navi.i_cur_row + 1
    menu_item = rows_menu_data[i_row]
    scene, rows, event_name = menu_item[1]
    scm.goto_scene(scene)
    tbl_navi.set_rows(rows)
    ect.emmit(event_name)


def bg_color_proc(i_cur_row, i_row, _rows_flags, focus):
    if (i_cur_row == i_row) and focus:
        return colors.TABLE_SEL_ACTIVE if focus else colors.TABLE_SEL_INACTIVE
    else:
        return colors.TABLE_BACK[i_row % len(colors.TABLE_BACK)]


if __name__ == '__main__':
     main()
