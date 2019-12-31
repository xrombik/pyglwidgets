#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Чужие модули
import glib
import gtk
import inspect
import cairo

# Свои модули
from . import gltools
from . import fonts
from .glwidget import *
from .glimports import *
from .driver import safe_connect
from .driver import safe_disconnect

__all__ = ('Button', 'ButtonRing', 'ButtonAnimated')


class Button(GlWidget):
    pressed = False

    def __init__(self, pos, text, textures, text_color=gltools.colors.BUTTON_TEXT, auto=1, user_proc=None,
                 user_data=None, check_part=((1.0 / 6.0), 0.5)):
        assert type(text_color) is tuple, "Цвет должен состоять из четырёх компонент в кортеже"
        assert len(text_color) == 4, "Цвет должен состоять из четырёх компонент в кортеже"
        for c in text_color:
            assert type(c) is int, "Значение цвета должно быть целым"
            assert 0 <= c <= 255, "Значение цвета должно быть от 0 до 255 включительно"
        assert len(check_part) == 2, "Параметр выравнивания состоит из двух элементов типа float"
        assert type(check_part[0]) is float, "Параметр выравнивания состоит из двух элемнтов типа float"
        assert type(check_part[1]) is float, "Параметр выравнивания состоит из двух элемнтов типа float"
        if user_proc is not None:
            assert inspect.isfunction(user_proc), "Должна быть функция"
        if text is not None:
            assert type(text) is str, "Должна быть строка"
        assert type(pos) is tuple
        assert len(pos) == 2
        assert type(pos[0]) is int
        assert type(pos[1]) is int
        assert type(auto) is int

        self.pos = pos

        # Относительное положение надписи.
        # check_part[0]: 0.5 - посередине, меньше 0.5 - левее
        # check_part[1]: 0.5 - посередине, меньше 0.5 - выше
        self.check_part = check_part

        # Надпись
        if text is not None:
            self._text = text.encode('utf-8')
        else:
            self._text = None
        self.text_color = text_color

        # Display list
        self.texture_id = glGenTextures(1)

        # Состояние кнопки и текстура
        self._state = 0
        self.pressed = False
        if type(textures[0]) is tuple:
            self.textures = textures
        else:
            self.textures = (textures,)
        for item in self.textures:
            assert glIsTexture(item[0]), "Должен быть дейсвительный идентификатор текстуры. Формат: (идентификатор текстуры openGL, ширина int, высота int), (,,))"
            assert type(item[1]) is int, "Должна быть ширина, целое. Формат: (идентификатор текстуры openGL, ширина int, высота int), (,,))"
            assert type(item[2]) is int, "Должна быть высота, целое. Формат: (идентификатор текстуры openGL, ширина int, высота int), (,,))"

        # Наведение мыши
        self.cover = 0
        self.alphas = (200, 250)  # Прозрачность при наведённой и ненаведённой мыши
        self.color = [255, 255, 255, 255]

        # События
        self.ehid0, self.ehid1, self.ehid2 = None, None, None
        self.connect()

        # Пользовательская процедура и данные
        self.user_proc = user_proc
        self.user_data = user_data

        # Группа, если будет радиокнопкой
        self.group = None

        # Можно ли отжать кнопку радиогруппы
        self.unfixed = False

        # Режим отработки нажатий
        assert type(auto) is int  # Режим работы кнопки должен быть целым числом
        assert auto in (0, 1, 2)  # Режим работы кнопки может принимать только эти значения
        self.auto = auto  # 0 - не управляется(не меняется при нажатии), 1 - фиксируемая (меняется после нажатия), 2 - без фиксации (мигает при нажатии)
        self.idts = None  # Таймер для режима self.auto:2

        self.click_count = 0
        self.outlines = None
        self.align = align_h_left  # Процедура выравнивания текста

        self.mirror = gltools.MIRROR_NONE

        self.texture2 = None
        self.text_height = fonts.DEFAULT_FONT_SIZE

        self.on_mouse_over = self.on_mouse_over_def  # Обработка наведения мыши
        self.put_to_redraw()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, val):
        if self._state == val: return
        self._state = val
        self.put_to_redraw()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, val):
        if self._text == val: return
        self._text = val
        self.put_to_redraw()

    def connect(self):
        self.pc.append(('ehid0', safe_connect, 'motion-notify-event', self._motion_notify))
        self.pc.append(('ehid1', safe_connect, 'button-release-event', self.button_release))
        self.pc.append(('ehid2', safe_connect, 'button-press-event', self.button_press))

    def button_press(self, widget, event):
        if event.button != 1:  # 1 - левая кнопка мыши, 2 - средняя, 3 - правая.
            return
        self.pressed = self.cover
        Button.pressed = True

    def disconnect(self):
        self.pc.append(('ehid0', safe_disconnect))
        self.pc.append(('ehid1', safe_disconnect))
        self.pc.append(('ehid2', safe_disconnect))

        if self.idts is not None:
            glib.source_remove(self.idts)
            self.idts = None

    def __del__(self):
        super(Button, self).__del__()
        glDeleteTextures(self.texture_id)

    def _on_timeout_state(self):
        self.state = 0
        self.idts = None
        return False

    def button_release(self, widget, event):
        if event.button != 1:  # 1 - левая кнопка мыши, 2 - средняя, 3 - правая.
            return
        Button.pressed = False
        if not (self.cover and self.pressed):
            self.pressed = False
            return False
        if self.group is None:
            if self.auto == 1:
                self.state = (self.state + 1) % len(self.textures)
            elif self.auto == 2:
                if self.idts is None:
                    self.idts = glib.timeout_add(100, self._on_timeout_state)
                    self.state = 1
            if self.user_proc is not None:
                self.user_proc(self)
                assert 0 <= self.state < len(self.textures)  # Количество состояний должно быть не больше количества текстур
                return self.cover
        else:
            assert len(self.textures) == 2  # Количество текстур радиокнопки должно быть равно двум
            if not self.unfixed:
                for btn in self.group:
                    state = btn.state
                    btn.state = int(id(btn) == id(self))  # Этот экземпляр кнопки включить, а другие выключить
                    if btn.state != state:
                        if btn.user_proc is not None:
                            btn.user_proc(btn)
                            assert 0 <= btn.state < len(self.textures)  # Количество состояний должно быть не больше количества текстур
            else:
                if self.auto != 0:
                    for btn in self.group:
                        state = btn.state
                        if id(btn) == id(self):  # Этому экземпляру кнопки сменить состояние, а другие выключить
                            btn.state += 1
                            btn.state %= 2
                        else:
                            btn.state = 0
                        if btn.state != state:
                            if btn.user_proc is not None:
                                btn.user_proc(btn)
                                assert 0 <= btn.state < len(self.textures)  # Количество состояний должно быть не больше количества текстур

    @staticmethod
    def on_mouse_over_def(btn, *args):
        pass

    def _motion_notify(self, *args):
        event = args[1]
        width = self.textures[self.state][1]
        height = self.textures[self.state][2]
        cover = gltools.check_rect(width, height, self.pos, event.x, event.y)
        # Чтобы лишний раз не добавилось в очередь перерисовки
        if self.cover != cover:
            self.cover = cover
            self.on_mouse_over(self, *args)
            self.put_to_redraw()
            if cover:
                self.pc.append(('ehid1', safe_connect, 'button-release-event', self.button_release))
                self.pc.append(('ehid2', safe_connect, 'button-press-event', self.button_press))
            else:
                self.pc.append(('ehid1', safe_disconnect))
                self.pc.append(('ehid2', safe_disconnect))
        return False  # Returns: True to stop other handlers from being invoked for the connect. False to propagate the connect further.

    def redraw(self):
        if len(self.textures) < self._state:
            raise ValueError('%s:%s, state:%u, len(textures):%u' % (self, self.text, self.state, len(self.textures)))
        texture1 = self.textures[self._state][0]
        width = self.textures[self._state][1]
        height = self.textures[self._state][2]
        # изображение кнопки
        alpha = self.alphas[self.cover and (not Button.pressed)]
        color = self.color[0], self.color[1], self.color[2], alpha

        if self.text and (self.texture2 is None):
            # Вычислить размер в пикселях который будет занимать текст
            xbearing, ybearing, text_width, text_height, xadvance, yadvance = fonts.CairoFont.cairo_context.text_extents(self._text)
            fascent, fdescent, fheight, fxadvance, fyadvance = fonts.CairoFont.cairo_context.font_extents()

            # Выравнивание
            width_a, x_a = self.align(self.pos, width, xadvance, self.check_part[0])

            # Нарисовать текcт в текстуру:
            # 1) создать изображение текста в буфере
            cis = cairo.ImageSurface(cairo.FORMAT_ARGB32, width_a, height)
            cc = cairo.Context(cis)
            cc.select_font_face(fonts.DEFAULT_FONT_FACE)
            cc.set_font_size(self.text_height)

            # тень
            cc_draw_text_shadow(cc, self._text, ybearing)

            # центр
            cc.set_source_rgba(1.0, 1.0, 1.0, 0.8)
            cc.move_to(1, - ybearing + 1)
            cc.show_text(self._text)

            # 2) Назначить буфер с текстом в текстуру
            texture2 = gltools.data_to_texture(self.texture_id, cis.get_data(), width_a, height)
            cis.finish()

            y = int(self.pos[1] + (height - fheight + fdescent) * self.check_part[1] + 0.5)

        # Сборка потока команд в display list
        glNewList(self.dl, GL_COMPILE)
        # 3) Нарисовать фон кнопки
        gltools.draw_texture((texture1, width, height), self.pos, color, self.mirror)
        # 4) Нарисовать текстуру с текстом
        if self._text:
            gltools.draw_texture(texture2, (x_a, y), self.text_color)
        if self.outlines:
            gltools.draw_lines(self.outlines, self.outline_colors[self.outline_colori])
        glEndList()


class ButtonRing(Button):
    """
    Кнопка в форме кольца
    """

    def __init__(self, gda, pos, textures, r1, r2, state_colors=(gltools.colors.ALPHA0, gltools.colors.RED1),
                 user_proc=None, user_data=None):
        """
        :param gda: Контекст opengl-gtk
        :param pos: Координаты верхнего левого угла на экране в пикселях
        :param textures: Текстуры
        :param r1: Внутренний радиус в пикселях
        :param r2: Внешний радиус в пикселях
        :param state_colors: Цвета состояний
        :param user_proc: Пользовательская процедура
        :param user_data: Пользовательские данные
        """
        super(ButtonRing, self).__init__(gda, pos, None, textures, (255, 255, 255, 255), 0, user_proc, user_data)
        # Формальная проверка фходных данных
        assert (type(r1) is int) and (r1 > 0)  # r1 - внутренний радиус
        assert (type(r2) is int) and (r2 > 0)  # r2 - внешний радиус
        assert r2 > r1  # Внешний радиус должен быть больше внутреннего
        self.state_colors = state_colors
        self.auto = 0
        self.r1 = r1
        self.r2 = r2

    def _motion_notify(self, *args):
        event = args[1]
        x = self.pos[0] + (self.textures[0][1] >> 1)
        y = self.pos[1] + (self.textures[0][2] >> 1)
        cover = gltools.check_ring(self.r1, self.r2, x, y, event.x, event.y)
        # Чтобы лишний раз не добавилось в очередь перерисовки
        if self.cover != cover:
            self.cover = cover
        return False  # Returns: True to stop other handlers from being invoked for the connect. False to propagate the connect further.

    def redraw(self):
        assert len(self.textures) > self._state
        alpha = self.alphas[self.cover and (not Button.pressed)]
        r, g, b, a = self.state_colors[self._state]
        color = r, g, b, alpha
        glNewList(self.dl, GL_COMPILE)
        gltools.draw_texture(self.textures[0], self.pos, color)
        glEndList()


class ButtonAnimated(Button):
    def __init__(self, gda, pos, textures, outline_colors, user_proc=None, user_data=None):
        self._is_playing = False
        self._timer_id = None
        super(ButtonAnimated, self).__init__(gda, pos, None, textures, (255, 255, 255, 255), False, user_proc, user_data)
        self._on_timer()
        self.outline_colors = outline_colors
        self.outline_colori = 0
        self._rate_ms = DEFAULT_RATE_MS

    def play(self, rate_ms=DEFAULT_RATE_MS):
        if self._timer_id is None:
            self._timer_id = glib.timeout_add(rate_ms, self._on_timer)
            self._is_playing = True
            self._rate_ms = rate_ms

    def stop(self):
        if self._timer_id is not None:
            self._timer_id = None
            self._is_playing = False

    def _on_timer(self):
        self.state = (self.state + 1) % len(self.textures)
        width = self.textures[self.state][1]
        height = self.textures[self.state][2]
        self.outlines = self.pos \
            , (self.pos[0] + width, self.pos[1]) \
            , (self.pos[0] + width, self.pos[1] + height) \
            , (self.pos[0], self.pos[1] + height) \
            , self.pos
        return self._is_playing

    def connect(self):
        super(ButtonAnimated, self).connect()
        if self._is_playing:
            if self._timer_id is None:
                self._timer_id = glib.timeout_add(self._rate_ms, self._on_timer)

    def disconnect(self):
        super(ButtonAnimated, self).disconnect()
        if self._timer_id:
            if self._timer_id is not None:
                glib.timeout_remove(self._timer_id)
                self._timer_id = None
