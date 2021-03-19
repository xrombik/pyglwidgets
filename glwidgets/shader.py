#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import glwidget
from .glimports import *
from gltools import *

"""
// Выходные встроенные переменные вершинного
gl_PointSize = 0.1;  // не влияет ни на что
gl_Position = ftransform(); // обязательно иначе не собирается шейдер

// Входные встроенные переменные фрагментного
gl_FragCoord = ; //
gl_FrontFacing = ; // содержит информацию о том, является ли текущий фрагмент частью фронтальной или тыльной грани
 
"""

TXT_VSP = """
    #version 130
    void main(void)
    {
         gl_Position = ftransform();
    } """

TXT_FSP = """ 
    #version 130
    uniform sampler2D sampler;
    void main(void)
    {   
        vec4 c = texture2D(sampler, gl_TexCoord[0].xy);
        float a = c[3];
        float bw = (c.r + c.g + c.b) / 3.0f; 
        gl_FragColor = vec4(bw, bw, bw, a) * gl_Color;
    } """


class Shader(glwidget.GlWidget):
    def __init__(self):
        self.program = glCreateProgram()
        attach_shader(self.program, TXT_VSP, GL_VERTEX_SHADER)
        attach_shader(self.program, TXT_FSP, GL_FRAGMENT_SHADER)
        glUseProgram(self.program)

    def __del__(self):
        glDeleteProgram(self.program)
