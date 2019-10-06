#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Примитивы OpenGL

# Чужие модули
import os
import cairo
import gtk
import gtk.gdkgl
import math
from .glimports import *

# Свои модули
import colors
from .glconst import *

_flash_phase = 0
flash_alpha = 100


def step_flash():
    global _flash_phase, flash_alpha
    _flash_phase += 1
    flash_alpha = (100, 80)[(_flash_phase // 3) % 2]


_glerros = \
    {
        GL_NO_ERROR: "GL_NO_ERROR: No error has been recorded",
        GL_INVALID_ENUM: "GL_INVALID_ENUM: An unacceptable value is specified for an enumerated argument",
        GL_INVALID_VALUE: "GL_INVALID_VALUE: A numeric argument is out of range",
        GL_INVALID_OPERATION: "GL_INVALID_OPERATION: The specified operation is not allowed in the current state",
        # GL_INVALID_FRAMEBUFFER_OPERATION: "GL_INVALID_FRAMEBUFFER_OPERATION: The framebuffer object is not complete",
        GL_OUT_OF_MEMORY: "GL_OUT_OF_MEMORY: There is not enough memory left to execute the command",
        GL_STACK_UNDERFLOW: "GL_STACK_UNDERFLOW: An attempt has been made to perform an operation that would cause an internal stack to underflow",
        GL_STACK_OVERFLOW: "GL_STACK_OVERFLOW: An attempt has been made to perform an operation that would cause an internal stack to overflow"
    }

# TODO: Добавить матрицу вертикального отражения
MIRROR_NONE = (0, 1, 1, 1, 1, 0, 0, 0)  # Матрица без отражения
MIRROR_HORIZ = (1, 1, 0, 1, 0, 0, 1, 0)  # Матрица горизонтального отражения

_dl_gltextparameterf = 0

# TODO: Переделать на использование "Vertex array" вместо "Display list"

pi_2 = 2.0 * math.pi


def aware_gtk_begin(gda):
    gtk.gdkgl.ext(gda.window)
    gda.gldrawable = gda.window.set_gl_capability(gda.glconfig)
    gda.glcontext = gtk.gdkgl.Context(gda.gldrawable)
    gda.gldrawable.wait_gdk()
    gda.gldrawable.gl_begin(gda.glcontext)
    opengl_init(gda)


def aware_gtk_end(gda, s):
    check_glerrors(s)
    gda.gldrawable.wait_gl()
    gda.gldrawable.gl_end()


def check_rect(width, height, pos, x1, y1):
    # type: (int, int, tuple[int, int], int, int) -> bool
    """
    Проверяет попадает ли точка в прямоугольник
    :param width: Ширина прямоугольника
    :param height: Высота прямоугольника
    :param pos: Левый верхний угол прямоугольника
    :param x1: X-координата точки на экране
    :param y1: Y-координата точки на экране
    :return: True - если попадает, False - если не попадает
    """
    if pos[0] < x1 < (pos[0] + width):
        return pos[1] < y1 < (pos[1] + height)
    return False


def check_ring(r1, r2, x, y, ex, ey):
    """
    Проверяет попадает ли точка в кольцо
    :param r1: Внутренний радиус
    :param r2: Внешний радиус
    :param x: Центр кольца по оси X
    :param y: Центр кольца
    :param ex: Проверяемая точка
    :param ey: Проверяемая точка
    :return: True - если попадает, False - если не попадает
    """
    assert r1 < r2, "Внутренний радиус r1:%u должен быть меньше внешнего r2:%u" % (r1, r2)
    return r1 < math.hypot(x - ex, y - ey) < r2


def get_str_width(s, font_name, font_size):
    # type: (str, glwidgets.GlFont, font_size) -> int
    """
    :param s: Строка
    :param font_name: Название шрифта
    :param font_size: Размер шрифта
    :return: Ширина строки в пикселях на экране
    """
    cc = cairo.Context(__cis0__)
    cc.select_font_face(font_name)
    cc.set_font_size(font_size)
    xbearing, ybearing, width, height, xadvance, yadvance = cc.text_extents(s)
    return int(xadvance + 0.5)


def draw_circle(cx, cy, r, color=(255, 255, 255, 255), width=2, num_segments=100):
    """
    Рисует окружность
    :param cx: Центр по оси X
    :param cy: Центр по оси Y
    :param r: Радиус окружности
    :param color: Цвет линии окружности
    :param width: Ширина линии окружности
    :param num_segments: Количество сегментов
    :return:
    """
    glLineWidth(width)
    glColor4ub(*color)
    glEnable(GL_LINE_STIPPLE)
    glLineStipple(1, 0x01)
    glBegin(GL_LINE_LOOP)
    for ii in range(num_segments):
        theta = pi_2 * float(ii) / float(num_segments)  # get the current angle
        x = r * math.cos(theta)  # calculate the x component
        y = r * math.sin(theta)  # calculate the y component
        glVertex2f(x + cx, _parent_height - (y + cy))  # output vertex
    glEnd()
    glDisable(GL_LINE_STIPPLE)


def draw_line(point1, point2, color, width=2):
    """
    Рисует линию между двумя точками
    :return: Ничего
    :param width: Толщина линий
    :param color: Цвет линий
    :param point1: Точка начала линии
    :param point2: Точка конца линии
    """
    glLineWidth(width)
    glColor4ub(*color)
    glBegin(GL_LINE_STRIP)
    glVertex2f(point1[0], _parent_height - point1[1])
    glVertex2f(point2[0], _parent_height - point2[1])
    glEnd()


def draw_lines(points, color, width=2):
    glLineWidth(width)
    glColor4ub(*color)
    glBegin(GL_LINE_STRIP)
    [glVertex2f(p0, _parent_height - p1) for p0, p1 in points]
    glEnd()


def draw_lines_rotated(rotor_point, points, color, width=2, tetha=0):
    glPushMatrix()
    glLineWidth(width)
    glColor4ub(*color)
    glTranslatef(rotor_point[0], _parent_height - rotor_point[1], 0)
    glRotatef(tetha, 0, 0, 1)  # rotating
    glBegin(GL_LINE_STRIP)
    map(lambda p: glVertex2f(*p), points)
    glEnd()
    glPopMatrix()


def draw_table2(pos, head, lines, font, color_proc, bg_color_proc, rows_flags, cws, i_cur=None, line_width=2,
                focus=True):
    """
    Рисует таблицу с горизонтальным заголовком
    :param cws: Ширины колонок
    :param pos: Координаты вехнего левого угла
    :param head: Заголовок
    :param lines: Строки
    :param font: Шрифт
    :param color_proc: Процедура цвета ячейки
    :param i_cur: Положение курсора
    :param line_width: Толщина линий
    :param focus: Флаг. True - таблица в фокусе ввода,
    False - таблица вне фокуса ввода. Меняет цвет кусора
    :return: Ничего
    """
    assert type(focus) is bool
    assert len(cws) == len(head)

    row_height = font.get_text_hight()

    x0, y0 = pos
    x, y = x0, y0
    cx, cy = 0, 0

    # текст заголовков колонок
    for str0, cws_x in zip(head, cws):
        col = color_proc(cx, cy)  # Выбор цвета для ячейки
        text_width = font.get_text_width(str0)  # Горизонтальное выравнивание по центру ячейки
        dx = (cws_x - text_width) >> 1
        if dx < 0: dx = 0
        font.draw_text((x + line_width + dx, y + row_height + line_width), str0, col)
        cx += 1
        x += cws_x

    x_right = x
    j = 0
    cy = 1
    for strs in lines:  # пробег по строкам
        y += row_height + line_width
        i = 0
        pts = (x_right - line_width, y) \
            , (x0 + line_width, y) \
            , (x0 + line_width, y + row_height + line_width) \
            , (x_right - line_width, y + row_height + line_width)
        if j < len(rows_flags):
            col = bg_color_proc(i_cur, j, rows_flags, focus)
        else:
            print('->gltools.py():ошибка: j:%u len(rows_flags):%u' % (j, len(rows_flags)))
        draw_polygon(pts, col)
        j += 1
        cx = 0
        x = x0
        for str0 in strs:  # пробег по столбцам
            # TODO: Добавить отсечение слишком длинного текста
            col = color_proc(cx, cy)  # Выбор цвета для ячейки
            font.draw_text((x + line_width, y + row_height + line_width), str0, col)
            x += cws[i]
            i += 1
            cx += 1
        cy += 1

    n_lines = len(lines) + 1  # + 1 строка на заголовок

    # верхняя граница
    draw_line((x0, y0), (x_right, y0), colors.TABLE_LINES, line_width)

    # граница под заголовком
    y = y0 + row_height + line_width
    draw_line((x0, y), (x_right, y), colors.TABLE_LINES, line_width)

    # нижняя граница
    y = y0 + (row_height + line_width) * n_lines
    draw_line((x0, y), (x_right, y), colors.TABLE_LINES, line_width)

    # вертикальные границы
    x = x0
    for cws_x in cws:
        draw_line((x, y), (x, y0), colors.TABLE_LINES, line_width)
        x += cws_x

    # правая граница
    draw_line((x_right, y), (x_right, y0), colors.TABLE_LINES, line_width)


def draw_table_borders(pos, cws, rh, rn, lw):
    """
    Рисует границы таблицы
    :param pos: Координаты верхнего левого угла
    :param cws: Ширины колонок
    :param rh: Высота строки
    :param rn: Количество строк
    :param lw: Толщина линий
    :return:
    """
    # вертикальные границы
    x = pos[0]
    y = pos[1] + rh * rn + lw * 3
    for cws_x in cws:
        draw_line((x, y), (x, pos[1]), colors.TABLE_LINES, lw)
        x += cws_x
    width = x - pos[0]

    # правая граница
    x = pos[0] + width + lw
    draw_line((x, y), (x, pos[1]), colors.TABLE_LINES, lw)

    # верхняя граница
    draw_line(pos, (x, pos[1]), colors.TABLE_LINES, lw)

    # граница под заголовком
    y = pos[1] + rh + lw
    draw_line((pos[0], y), (x, y), colors.TABLE_LINES, lw)

    # нижняя граница
    y = pos[1] + lw * 2 + (rn + 2) * rh
    draw_line((pos[0], y), (x, y), colors.TABLE_LINES, lw)


def opengl_init(gda):
    global __cis0__, _parent_height, __cairo_texts__, __cairo_texts_len_max__, _dl_gltextparameterf
    __cis0__ = cairo.ImageSurface(cairo.FORMAT_ARGB32, gda.allocation.width, gda.allocation.height)
    _parent_height = gda.allocation.height
    __cairo_texts__ = dict()
    __cairo_texts_len_max__ = 2048

    glEnable(GL_MULTISAMPLE)
    glViewport(0, 0, gda.allocation.width, gda.allocation.height)
    glOrtho(0, gda.allocation.width, 0, gda.allocation.height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_CULL_FACE)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_BLEND)
    glEnable(GL_DITHER)
    glEnable(GL_POLYGON_SMOOTH)
    glEnable(GL_POINT_SMOOTH)
    glCullFace(GL_BACK)
    glShadeModel(GL_SMOOTH)
    glDepthFunc(GL_LESS)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClearDepth(1.0)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    _dl_gltextparameterf = glGenLists(1)
    glNewList(_dl_gltextparameterf, GL_COMPILE)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glEndList()

    val = GL_NICEST  # =GL_FASTEST
    glHint(GL_LINE_SMOOTH_HINT, val)
    glHint(GL_POINT_SMOOTH_HINT, val)
    glHint(GL_POLYGON_SMOOTH_HINT, val)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, val)

    print(u'Версия привязки python OpenGL: %s' % str(OpenGL.__version__))
    print('Производитель: %s' % glGetString(GL_VENDOR))
    print('Версия OpenGL: %s' % glGetString(GL_VERSION))
    print('Версия GLSL: %s' % glGetString(GL_SHADING_LANGUAGE_VERSION))
    print('Отрисовка: %s' % glGetString(GL_RENDERER))


def opengl_uninit():
    # glDeleteTextures(_textures)
    pass


def draw_sector(pointsIn, pointsOut, color):
    N1 = len(pointsOut)
    N2 = len(pointsIn)
    N = N2
    if (N1 < 2) or (N2 < 2):
        return
    if N1 < N2:
        N = N1

    glColor4ub(*color)
    i = 0
    iN = N - 1
    while i < iN:
        i1 = N - i - 1
        i2 = N - i - 2
        glBegin(GL_POLYGON)
        px, py = pointsOut[i]
        glVertex2f(px, _parent_height - py)
        px, py = pointsIn[i1]
        glVertex2f(px, _parent_height - py)
        px, py = pointsIn[i2]
        glVertex2f(px, _parent_height - py)
        glEnd()
        glBegin(GL_POLYGON)
        px, py = pointsIn[i]
        glVertex2f(px, _parent_height - py)
        px, py = pointsOut[i1]
        glVertex2f(px, _parent_height - py)
        px, py = pointsOut[i2]
        glVertex2f(px, _parent_height - py)
        glEnd()
        i += 1


def draw_line(point1, point2, color=colors.WHITE, width=2):
    glLineWidth(width)
    glColor4ub(*color)
    glBegin(GL_LINE_STRIP)
    glVertex2f(point1[0], _parent_height - point1[1])
    glVertex2f(point2[0], _parent_height - point2[1])
    glEnd()


def check_glerrors(title):
    err_cnt = 0
    while True:
        err0 = glGetError()
        if err0 != GL_NO_ERROR:
            print('%s:%s' % (title, _glerros[err0]))
            err_cnt += 1
            continue
        break
    if err_cnt:
        raise Exception()
    return err_cnt


def generate_dls(_size):
    first_dl = glGenLists(_size)
    dls = range(first_dl, first_dl + _size)
    return dls


def data_to_texture(texture_id, data, width, height, _db=''):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    # assert glIsTexture(texture_id)  # You cannot include calls to glIsTexture in display lists.
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, str(data))
    glCallList(_dl_gltextparameterf)
    glDisable(GL_TEXTURE_2D)
    return texture_id, width, height


def texture_from_gtkimage(image):
    assert type(image) is gtk.Image
    pb = image.get_pixbuf()
    image.get_colormap()
    glEnable(GL_TEXTURE_2D)
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, pb.get_width(), pb.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE,
                 pb.get_pixels())
    glCallList(_dl_gltextparameterf)
    glDisable(GL_TEXTURE_2D)
    return texture_id, pb.get_width(), pb.get_height()


def textures_from_files(fmt, count):
    return [texture_from_file(fmt % i) for i in range(count)]


def texture_from_file(file_name):
    assert type(file_name) is str
    image = gtk.Image()
    if not os.path.exists(file_name):
        raise ValueError('File: \'%s\' - not found.' % file_name)
    image.set_from_file(file_name)
    texture = texture_from_gtkimage(image)
    return texture


def draw_texture(texture, pos, col=(255, 255, 255, 255), mirror=MIRROR_NONE):
    """
    Рисует текстуру
    :param texture: Текстура
    :param pos: Коррдинаты на экране
    :param col: Окрашивающий цвет
    :param mirror: Матрица отражения. Смотри MIRROR_*
    :return:
    """
    glEnable(GL_TEXTURE_2D)
    glColor4ub(*col)
    glPushMatrix()
    glTranslatef(pos[0], _parent_height - pos[1] - texture[2], 0)
    glBindTexture(GL_TEXTURE_2D, texture[0])

    glBegin(GL_QUADS)
    glTexCoord2f(mirror[0], mirror[1])
    glVertex2f(0, 0)
    glTexCoord2f(mirror[2], mirror[3])
    glVertex2f(texture[1], 0)
    glTexCoord2f(mirror[4], mirror[5])
    glVertex2f(texture[1], texture[2])
    glTexCoord2f(mirror[6], mirror[7])
    glVertex2f(0, texture[2])
    glEnd()

    glPopMatrix()
    glDisable(GL_TEXTURE_2D)


def draw_texture_rotate(texture, pos, a=0.0, col=(255, 255, 255, 255), mirror=MIRROR_NONE, scale=(1.0, 1.0, 1.0)):
    # type: (tuple, tuple, float, tuple, tuple, tuple) -> None
    glEnable(GL_TEXTURE_2D)
    glColor4ub(*col)
    glPushMatrix()
    glTranslatef(pos[0], _parent_height - pos[1], 0)
    glRotate(a, 0, 0, -1)
    glBindTexture(GL_TEXTURE_2D, texture[0])
    glScalef(*scale)
    glBegin(GL_QUADS)
    sx = texture[1] // 2
    sy = texture[2] // 2
    glTexCoord2f(mirror[0], mirror[1])
    glVertex2f(-sx, -sy)
    glTexCoord2f(mirror[2], mirror[3])
    glVertex2f(sx, -sy)
    glTexCoord2f(mirror[4], mirror[5])
    glVertex2f(sx, sy)
    glTexCoord2f(mirror[6], mirror[7])
    glVertex2f(-sx, sy)
    glEnd()
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)


def draw_texture_scale(texture, pos, scale, col=(255, 255, 255, 255), mirror=MIRROR_NONE):
    glEnable(GL_TEXTURE_2D)
    glColor4ub(*col)
    glPushMatrix()
    glTranslatef(pos[0], _parent_height - pos[1] - texture[2], 0)
    glBindTexture(GL_TEXTURE_2D, texture[0])
    glScalef(scale[0], scale[1], 1.0)

    glBegin(GL_QUADS)
    glTexCoord2f(mirror[0], mirror[1])
    glVertex2f(0, 0)
    glTexCoord2f(mirror[2], mirror[3])
    glVertex2f(texture[1], 0)
    glTexCoord2f(mirror[4], mirror[5])
    glVertex2f(texture[1], texture[2])
    glTexCoord2f(mirror[6], mirror[7])
    glVertex2f(0, texture[2])
    glEnd()

    glPopMatrix()
    glDisable(GL_TEXTURE_2D)


def draw_polygon(points, color):
    glColor4ub(*color)
    glBegin(GL_POLYGON)
    map(lambda p: glVertex2f(p[0], _parent_height - p[1]), points)
    glEnd()
