#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
- Nombre: bitbyteutils.py
- Descripción: contiene funciones de utilidad para manipular un elemento (byte)
de un conjunto de bytes de bits (bitbytearay).
- Autor: Agustín González
- Modificado: 16/04/18
'''


def to_bytes(size, number):
    '''Convierte el número dado a una secuencia de bytes del tamaño especificado.
    Nota: esta función tiene el objetivo de preservar la compatibilidad con Py2.
    Py3 ya ofrece una función de nombre to_bytes().

    Args:
        size (int): tamaño del array de bytes resultante.
        number (int): número a convertir.

    Returns:
        converted (byte list): representación del número como array de bytes.
    '''
    # Corrimiento big-endian. Nota: i << 3 = i * 8
    converted = [(number >> ((i << 3)) & 255) for i in reversed(range(0, size))]
    return bytearray(converted)


def to_byte(number):
    '''Convierte un entero a byte.

    Args:
        number (int): número a convertir.

    Returns
        byte (byte): número convertido.
    '''
    # number.to_bytes(1, byteorder="big")
    return to_bytes(1, number)


def to_left(byte, places):
    '''Desplaza un byte a la izquierda en la cantidad especificada de lugares
    (bits), eliminando los 'excedentes' (es decir, retornando un byte).

    Args:
        byte (byte o int): byte del que se desea realizar el desplazamiento.
        places (int): lugares a desplazar.

    Returns:
        shifted (int): byte resultante.
    '''
    # El AND lógico permite acotar a los 8 bits más significativos (0xFF=255).
    shifted = ((byte) << places) & 0xFF
    return shifted


def to_right(byte, places):
    '''Desplaza un byte a la derecha en la cantidad especificada de lugares
    (bits), eliminando los 'excedentes' (es decir, retornando un byte).

    Args:
        byte (byte o int): byte del que se desea realizar el desplazamiento.
        places (int): lugares a desplazar.

    Returns:
        shifted (int): byte resultante.
    '''
    # El AND lógico permite acotar a los 8 bits más signif. (Nota: 0xFF=255).
    shifted = (byte >> places) & 0xFF
    return shifted


def validate_padding(padding):
    '''Valida que el relleno de bits de un byte no sea negativo ni mayor o igual
    a 8 (ocho).

    Args:
        padding (int): bits de relleno de un byte.

    Returns:
        Exception, si el padding no es válido.
    '''
    if padding >= 0 or padding < 8:
        return

    raise Exception("El padding no puede ser negativo ni mayor o igual que 8.")
