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
    widths_keys = [100, 100]

    rows_opts = [
        ['OPTIONS', 'VALUE'],
        ['SOUND',   'On']]
    widths_opts = [110, 100]

    rows_score = [
        ['DATE',        'SCORE'],
        ['2020-04-01',  '1000'],
        ['2020-05-01',  '2000']]
    widths_score = [120, 100]

    tbl_navi_stack = list()
    rows_menu = list()
    tbl_navi = Table((200, 150), rows_menu)
    tbl_navi.widths = [200]
    tbl_navi.i_cur_row = 0
    tbl_navi.bg_color_proc = bg_color_proc
    tbl_navi.focus = True

    txr_player = rcm.get_texture('player.png')
    txr_bullet = rcm.get_texture('bullet.png')
    pic_player = PictureRotate((320, 400), txr_player)
    pic_bullet = PictureRotate((320, 300), txr_bullet)

    EVENT_MENU, EVENT_GAME, EVENT_KEYS, EVENT_OPTS, EVENT_SCORE, EVENT_EXIT = range(6)
    widths_menu = list()

    items_main = (txt_header,  tbl_navi)
    items_game = (pic_player,  pic_bullet)
    items_keys = (txt_header,  tbl_navi)
    items_opts = (txt_header,  tbl_navi)
    items_score = (txt_header, tbl_navi)

    scene_main = [items_main,  rows_menu,  widths_menu,   EVENT_MENU]
    scene_game = [items_game,  list(),     list(),        EVENT_GAME]
    scene_keys = [items_keys,  rows_keys,  widths_keys,   EVENT_KEYS]
    scene_opts = [items_opts,  rows_opts,  widths_opts,   EVENT_OPTS]
    scene_score =[items_score, rows_score, widths_score,  EVENT_SCORE]
    scene_exit = [tuple(),     list(),     list(),        EVENT_EXIT]

    rows_menu_data = [
        (['MAIN MENU'],      None),
        (['START NEW GAME'], scene_game),
        (['REDEFINE KEYS'],  scene_keys),
        (['OPTIONS'],        scene_opts),
        (['SCORE TABLE'],    scene_score),
        (['EXIT'],           scene_exit)]
    widths_menu[:] = [200]

    rows_menu[:] = map(lambda data_row: data_row[0], rows_menu_data)[:]

    tbl_navi.user_data = tbl_navi_stack, rows_menu_data

    timer = driver.Timer(100, on_bullet_timer, pic_bullet)
    ect = EventCtl()
    tbl_navi.connect(nevents.EVENT_KEY_PRESS, lambda *args: on_key_press(args[1].keyval, ect))
    scm.goto_scene(scene_main[0])
    ect.connect(EVENT_EXIT, app.uninit)
    ect.connect('Escape', on_key_escape, tbl_navi, app)
    ect.connect('Escape', scm.goto_back)
    ect.connect('Return', on_key_return, tbl_navi, scm, ect)
    ect.connect('Left', on_key_move, pic_player, 0, -10)
    ect.connect('Right', on_key_move, pic_player, 0, 10)
    ect.connect('space', on_key_fire, timer, pic_player, pic_bullet)


def on_key_fire(timer, pic_player, pic_bullet):
    if timer.is_running:
        return
    pic_bullet.pos[0] = pic_player.pos[0]
    pic_bullet.pos[1] = 300
    timer.start()


def on_bullet_timer(timer, pic_bullet):
    pic_bullet.pos[1] -= 10
    pic_bullet.put_to_redraw()
    if pic_bullet.pos[1] < 0:
        timer.stop()
    return True


def on_key_move(pic_player, i, val):
    # type: (PictureRotate, int, int) -> None
    pic_player.pos[i] += val
    pic_player.put_to_redraw()


def on_key_press(keyval, ect):
    char_code, char_name = driver.map_keyval(keyval)
    ect.emmit(char_name)


def on_key_escape(tbl_navi, app):
    tbl_navi_stack = tbl_navi.user_data[0]
    if len(tbl_navi_stack):
        rows, widths = tbl_navi_stack.pop()
        tbl_navi.set_rows(rows)
        tbl_navi.widths = widths
    else:
        app.uninit()


def on_key_return(tbl_navi, scm, ect):
    rows = tbl_navi.get_rows()
    widths = tbl_navi.widths
    tbl_navi_stack = tbl_navi.user_data[0]
    rows_menu_data = tbl_navi.user_data[1]
    tbl_navi_stack.insert(0, (rows, widths))
    i_row = tbl_navi.i_cur_row + 1
    scene, rows, widths, event_name = rows_menu_data[i_row][1]
    scm.goto_scene(scene)
    tbl_navi.set_rows(rows)
    tbl_navi.widths = widths
    ect.emmit(event_name)


def bg_color_proc(i_cur_row, i_row, _rows_flags, focus):
    if (i_cur_row == i_row) and focus:
        return colors.TABLE_SEL_ACTIVE if focus else colors.TABLE_SEL_INACTIVE
    else:
        return colors.TABLE_BACK[i_row % len(colors.TABLE_BACK)]


if __name__ == '__main__':
    main()
