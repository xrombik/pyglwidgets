#!/usr/bin/env python
# -*- coding: utf-8 -*-


from . import colors
from . import glwidget
from gltools import draw_texture_rotate
from gltools import MIRROR_NONE
from gltools import draw_texture
from gltools import draw_texture_scale
from .glimports import *


class Picture(glwidget.GlWidget):
    def __init__(self, pos, texture, scale=(1.0, 1.0, 1.0), color=colors.WHITE, user_data=None):
        assert (type(pos) is tuple) or (type(pos) is list)
        assert len(pos) == 2
        assert type(pos[0]) is int
        assert type(pos[1]) is int
        assert type(scale) in (list, tuple)
        assert len(scale) == 3
        assert (type(scale[0]) is float) and (scale[0] >= 0)
        assert (type(scale[1]) is float) and (scale[1] >= 0)
        assert (type(scale[2]) is float) and (scale[2] >= 0)
        assert len(color) == 4
        for col in color:
            assert type(col) is int
            assert 0 <= col <= 255

        self.pos = list(pos)
        self.scale = list(scale)
        self.color = list(color)
        self.texture = texture
        self.mirror = MIRROR_NONE  # Зеркалирование
        self.user_data = user_data

    def move(self, dx=0, dy=0):
        self.pos[0] += dx
        self.pos[1] += dy
        self.put_to_redraw()

    def get_textures(self):
        return self.texture

    def redraw(self):
        glNewList(self.dl, GL_COMPILE)
        draw_texture_scale(self.texture, self.pos, self.scale, self.color, self.mirror)
        glEndList()


class PictureRotate(Picture):
    def __init__(self, pos, texture, ang=0, color=colors.WHITE):
        super(PictureRotate, self).__init__(pos, texture, scale=[1.0, 1.0, 1.0], color=color)
        self._ang = ang
        self.ang_shift = 0.0

    def redraw(self):
        glNewList(self.dl, GL_COMPILE)
        draw_texture_rotate(self.texture, self.pos, self.ang + self.ang_shift, self.color, self.mirror, self.scale)
        glEndList()

    @property
    def ang(self):
        return self._ang

    @ang.setter
    def ang(self, val):
        if self._ang == val: return
        self._ang = val
        self.put_to_redraw()


class PictureState(Picture):
    def __init__(self, pos, textures, state=0, color=colors.WHITE, user_data=None):
        super(PictureState, self).__init__(pos, textures, color=color)
        self.state = state
        self.user_data = user_data

    def redraw(self):
        assert len(self.texture) > self.state
        glNewList(self.dl, GL_COMPILE)
        draw_texture(self.texture[self.state], self.pos, self.color)
        glEndList()
