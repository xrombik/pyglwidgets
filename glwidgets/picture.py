#!/usr/bin/env python
# -*- coding: utf-8 -*-


from . import colors
from . import gltools
from . import glwidget
from .glimports import *


class Picture(glwidget.GlWidget):
	def __init__(self, pos, texture, scale=[1.0, 1.0, 1.0], color=colors.WHITE, user_data=None):
		assert (type(pos) is tuple) or (type(pos) is list)
		assert len(pos) == 2
		assert type(pos[0]) is int
		assert type(pos[1]) is int
		assert type(scale) is list
		assert len(scale) == 3
		assert (type(scale[0]) is float) and (scale[0] >= 0)
		assert (type(scale[1]) is float) and (scale[1] >= 0)
		assert (type(scale[2]) is float) and (scale[2] >= 0)
		assert len(color) == 4
		for col in color:
			assert type(col) is int
			assert 0 <= col <= 255
		
		self.pos = list(pos)
		self.dl = glGenLists(1)
		assert glIsList(self.dl)
		self.scale = scale
		self.color = list(color)
		self.texture = texture
		self.mirror = gltools.MIRROR_NONE  # Зеркалирование
		self.user_data = user_data

	def move(self, dx=0, dy=0):
		self.pos[0] += dx
		self.pos[1] += dy
		self.put_to_redraw()

	def get_textures(self):
		return self.texture

	def __del__(self):
		super(Picture, self).__del__()
		glDeleteLists(self.dl, 1)

	def redraw(self):
		glNewList(self.dl, GL_COMPILE)
		gltools.draw_texture_scale(self.texture, self.pos, self.scale, self.color, self.mirror)
		glEndList()


class PictureRotate(Picture):
	def __init__(self, pos, texture, ang=0, color=colors.WHITE):
		super(PictureRotate, self).__init__(pos, texture, scale=[1.0, 1.0, 1.0], color=color)
		self.ang = ang
		self.ang_shift = 0.0
	
	def redraw(self):
		glNewList(self.dl, GL_COMPILE)
		gltools.draw_texture_rotate(self.texture, self.pos, self.ang + self.ang_shift, self.color, self.mirror, self.scale)
		glEndList()


class PictureState(Picture):
	def __init__(self, pos, textures, state=0, color=colors.WHITE, user_data=None):
		super(PictureState, self).__init__(pos, textures, color=color)
		self.state = state
		self.user_data = user_data
	
	def redraw(self):
		assert len(self.texture) > self.state
		glNewList(self.dl, GL_COMPILE)
		gltools.draw_texture(self.texture[self.state], self.pos, self.color)
		glEndList()