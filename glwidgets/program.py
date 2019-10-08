#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
from glib import MainLoop


class ProgramCtl(object):

    def __init__(self, argv):
        self.saved_exception_hook = sys.excepthook
        sys.excepthook = self.exception_hook
        self._main_loop = MainLoop()
        self.run = self._main_loop.run

    def uninit(self):
        print('Завершается нормально')
        self._main_loop.quit()

    def exception_hook(self, etype, evalue, etb):
        self.saved_exception_hook(etype, evalue, etb)  # type: function
        print('%s:\n- Завершается из за возникновения исключения:'
            '\n%s\n%s\n%s' % (__file__, etype, evalue, etb))
        quit(1)
