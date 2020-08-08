#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glwidgets import *


def main():
    app = Candy('pyglwidgets', 320, 160, on_init)
    app.run()


def on_init(scm, _rcm, _app):
    # type: (SceneCtl, ResourceCtl, ProgramCtl) -> None
    """
    :param scm: Scene manager
    :param _rcm: Resource manager
    :return:
    """
    rows = [['Number', 'Color',  'Lenght'],
            ['1',      'red',    '30'],
            ['2',      'blue',   '50'],
            ['3',      'violet', '60']]

    tbl0 = Table((10, 10), rows)
    scm.add_scene_items(tbl0)


if __name__ == '__main__':
    main()
