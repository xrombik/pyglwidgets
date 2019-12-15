#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math


def set_wordi(buf, index, val):
    """
    Устанавливает слово в байтовом массиве
    :param buf: Байтовый массив
    :param index: Индекс младшего байта слова в массиве
    :param val: Значение слова для записи в батовый массив
    :return: None
    """
    buf[index] = val & 0xff
    buf[index + 1] = (val >> 8) & 0xff


def set_bit(bits, index, val, mask=0xffff):
    """
    :param bits: прежние значения
    :param index: индекс бита
    :param val: новое значение бита
    :param mask:
    :return:
    мастер
    """
    bits &= mask
    assert 0 <= index <= 32
    if val:
        bits |= 1 << index
    else:
        bits &= ~(1 << index)
    return int(bits & mask)


def get_bit(bits, index, mask=0xffff):
    # type: (int, int, int) -> int
    bits &= mask
    return ((bits & mask) & (1 << index)) > 0


def set_bytes(b, i, w):
    # type: (bytearray, int, int) -> None
    """
    Записывает слово в байтовый массив
    """
    w = int(w)
    b[i] = w & 0xff
    b[i + 1] = (w & 0xff00) >> 8


def chrs_to_word(s, i):
    return ord(s[i]) | (ord(s[i + 1]) * 256)


def ibytes_to_word(b, i):
    return b[i] | (b[i + 1] * 256)


def delta_tick(tick0, tick1, tick_max=0xffff):
    if tick1 > tick0:
        dtick = tick1 - tick0
    elif tick1 < tick0:
        dtick = tick_max - tick0 + tick1
    else:
        dtick = 0
    return dtick


def pos_to_ang(x0, y0, x, y):
    """
    return angel(degree's) and radius from x,y
    """
    x_ = x - x0
    y_ = y - y0
    ang = (math.atan2(y_, x_) * 180.0) / math.pi
    if ang < 0.0:
        ang += 360.0
    radius = math.hypot(x_, y_)
    return ang, radius


def get_mask32(width, shift=0):
    """
    Возвращает битовую маску заданной ширины непрерывно заполненную еденицами.
    Максимальная ширина - 32 бита.
    :param width: Ширина битовой маски. int
    :param shift: Смещение битовой маски влево, т.е. к старшим разрядам. int
    :return: Битовая маска. int
    """
    assert 0 <= shift <= 32
    assert 0 <= width <= 32
    mask = 0
    for i in range(width):
        mask |= 1 << i
    return mask << shift


def get_lbyte_from_word(data, i):
    """
    Возвращает младший байт массива 16 битных слов.
    :param data: Массив слов
    :param i: Индекс слова в массиве
    :return: Младший байт
    """
    return data[i] & 0xff


def get_hbyte_from_word(data, i):
    """
    Возвращает старший байт из слова
    :param data: Массив слов
    :param i: Индекс слова в массиве
    :return: Старший байт
    """
    return (data[i] & 0xff00) >> 8


def assert_byte(byte):
    # Выкидывает исключение, если byte не в диапазоне
    assert type(byte) is int
    assert 0 <= byte <= 255


def bytes_to_chrs(bytes_buf):
    return ''.join(map(chr, bytes_buf))


def set_bits(v, a, m):
    # type: (int, int, int) -> int
    """
    Устанавливает биты в соответствии с маской
    :param v: Прежние значения бит
    :param a: Новые значения бит
    :param m: Маска изменяемых бит
    :return: Изменённые значения бит
    """
    # TODO: Упростить выражение
    return v & a & (~m) | (~v) & a & m | v & a & m | v & (~a) & (~m)


def print_buffer(data, data_len):
    s = ''
    for i, b in enumerate(data[0:data_len]):
        s += '%u: %02x\n' % (i, b)
    print('%s\n' % s)


def get_bin_str(val, slen=16, rc='0'):
    # type: (int, int, str) -> str
    """
    Возвращает строку с двоичным представлением числа, выравненную по заданному количеству символов
    :param val: Число для представления
    :param slen: Количество символов для выравнивания
    :param rc: Символ для замены незначащих разрядов
    :return: Строка с двоичным представлением числа
    """
    s0 = '%0' + str(slen) + 's'
    return (s0 % (bin(val)[2:])).replace(' ', rc)


def str_cut(s, i):
    """
    Возвращает новую строку полученную отсечением входной строки по заданному индексу символа
    :param s: Отсекаемая строка
    :param i: Индекс символа с которого отсекается строка включительно
    :return: Отсечённая строка
    """
    return ''.join(list(s.decode('utf-8'))[:i])
