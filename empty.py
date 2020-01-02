#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glwidgets import *


def main():
    pgm = ProgramCtl()
    scm = SceneCtl()
    ddr = DrawDriver('pyglwidgets', 640, 480)
    ddr.set_init(ddr.init)
    ddr.set_uninit(on_uninit, pgm)
    ddr.set_scene(scm)
    pgm.run()


def on_uninit(pgm):
    pgm.uninit()


if __name__ == '__main__':
    main()
