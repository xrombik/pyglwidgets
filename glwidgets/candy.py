#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import ProgramCtl
from . import SceneCtl
from . import ResourceCtl
from . import DrawDriver
from . import gltools

__all__ = ('Candy', )


def _init(*args): pass


class Candy(ProgramCtl):
    def __init__(self, title, width=640, height=480, init=_init, *args):
        super(Candy, self).__init__()
        scm = SceneCtl()
        rcm = ResourceCtl()
        ddr = DrawDriver(title, width, height)
        sa = list()
        sa.append(self)
        for a in args:
            sa.append(a)
        ddr.set_init(init, scm, rcm, *sa)
        ddr.set_uninit(self.on_uninit, self, rcm)
        ddr.set_scene(scm)

    @staticmethod
    def on_uninit(pgm, rcm):
        # type: (ProgramCtl, ResourceCtl) -> None
        rcm.uninit()
        pgm.uninit()
        gltools.check_glerrors()
