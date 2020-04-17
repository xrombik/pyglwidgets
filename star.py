#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glwidgets import *
UPDATE_RATE = 30
WINDOW_WIDTH = 320
WINDOW_HEGHT = 160
ROTATE_SPEED = 1.0 / 30.0

def main():
    app = Candy('pyglwidgets', WINDOW_WIDTH, WINDOW_HEGHT, on_init)
    app.run()


def on_init(scm, rcm):
    # type: (SceneCtl, ResourceCtl) -> None
    """
    :param scm: Scene manager
    :param rcm: Resource manager
    :return:
    """
    txr_pic = rcm.get_texture('star.png')
    pos = WINDOW_WIDTH / 2, WINDOW_HEGHT / 2
    pic_star0 = PictureRotate(pos, txr_pic)
    pic_star1 = PictureRotate(pos, txr_pic)
    scm.add_scene_items(pic_star0, pic_star1)
    glib.timeout_add(UPDATE_RATE, on_timer, pic_star0, pic_star1)


def on_timer(pic_star0, pic_star1):
    pic_star0.ang += UPDATE_RATE * ROTATE_SPEED
    pic_star1.ang -= UPDATE_RATE * ROTATE_SPEED
    return True

if __name__ == '__main__':
    main()
