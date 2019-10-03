#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
from glib import MainLoop


class ProgramCtl(object):
    saved_exception_hook = None

    def __init__(self, argv):
        ProgramCtl.saved_exception_hook = sys.excepthook
        sys.excepthook = self.exception_hook
        self._main_loop = MainLoop()
        self.run = self._main_loop.run

    @staticmethod
    def exception_hook(etype, evalue, etb):
        ProgramCtl.saved_exception_hook(etype, evalue, etb)  # type: function
        print('%s:\n- Завершается из за возникновения исключения:\n%s\n%s\n%s'
            % (__file__, etype, evalue, etb))
        quit(1)
