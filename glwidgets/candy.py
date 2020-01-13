#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import ProgramCtl
from . import SceneCtl
from . import ResourceCtl
from . import DrawDriver

__all__ = ('run', )


def run(title, width, height, init, uninit):
	pgm = ProgramCtl()
	scm = SceneCtl()
	rcm = ResourceCtl()
	ddr = DrawDriver(title, width, height)
	ddr.set_init(init, scm, rcm)
	ddr.set_uninit(uninit, pgm, rcm)
	ddr.set_scene(scm)
	pgm.run()
	