#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
- Nombre: bitutils.py
- Descripción: contiene funciones que permiten la escritura/lectura a/desde
array de bytes o de enteros (ver docstrings). Nota: en esencia, las funciones
que permiten la escritura y lectura de ambos arrays son las mismas: no se ha
desarrollado una 'única' función (parametrizada, según se trate de escribir o
leer un byte o un entero), ya que esto implicaría añadir complejidad a una
sección 'crítica' de código y, con ello, pérdida de rendimiento.
- Autor: Agustín González
- Modificado: 26/04/18
'''


def write_binary_in_iarray(array, offset, number, bits):
    '''Permite la escritura binaria en un array de ints desde el offset dado.

    Args:
        array (int list): array sobre el que se realizará la escritura. Nota:
            debe haber suficiente espacio reservado para la cant. de bits
            a escribir.
        offset (int): nro. de bit de inicio de escritura en el array (visto
            como array de bits).
        bits (int): cant. de bits a escribir. Si el nro. se puede representar
            con menos de la cantidad especificada, se rellenará con ceros.

    Returns
        offset (int): nuevo offset en el array.
    '''
    # Si no hay nada que escribir...
    # if number == 0:
    #     return

    # Mientras la cantidad de bits a escribir sea mayor a 0.
    while bits > 0:
        # Index en el array.
        # array_index = int(offset / 32)
        array_index = offset >> 5

        # Bit index en el array index.
        # bit_index = int(offset % 32)
        bit_index = offset & 31

        # Espacio escribible.
        writable = 32 - bit_index

        # Bits a escribir en la ACTUAL iteración en el array index.
        to_write = bits if (bits < writable) else writable

        # Shift a realizar, según los bits a escribir y el espacio escribible.
        # Ej: si se requieren escribir 11 bits y si el espacio escribible es 8,
        # se deberá realizar 3 corrimientos para escribir los primeros 8 bits.
        # Se utiliza abs(), ya que puede darse el caso en el que la cantidad de
        # bits a escribir sea menor al espacio escribible.
        shift = int(abs(bits - writable))

        # Si el espacio escribible es menor a la cantidad de bits a escribir...
        if writable < bits:
            # Suma en el array
            array[array_index] += number >> shift
        else:
            # Add de últimos bits (corrimiento a la izquierda).
            array[array_index] += number << shift

        # Eliminación de números escritos.
        number &= (0xFFFFFFFF >> (32 - shift))

        # Incremento de offset y reducción de bits a escribir.
        offset += to_write
        bits -= to_write
    return offset


def read_binary_from_iarray(array, offset, bits):
    '''Permite la lectura binaria en un array de ints desde el offset dado.

    Args:
        array (int list): array sobre el que se realizará la lectura.
        offset (int): nro. de bit de inicio de lectura dentro del array (visto
            como array de bits).
        bits (int): cantidad de bits a leer.

    Returns
        number (int): número leído.
    '''
    # Nota: en el read desde un array de enteros no es necesaria una estructura
    # cíclica (como sí en el del array de bytes), puesto que un entero a leer
    # estará distribuido en, como máximo, dos enteros.

    # Index en el array.
    # array_index = int(offset / 32)
    array_index = offset >> 5

    # Bit index en el array index.
    # bit_index = int(offset % 32)
    bit_index = offset & 31

    # Bits leíbles en el byte.
    readable = 32 - bit_index

    # Extracción de todos los bits a la derecha del bit_index.
    # mask = (0xFFFFFFFF >> bit_index). Nota: 0xFFFFFFFF = 4294967295
    extracted = (array[array_index] & (0xFFFFFFFF >> bit_index))

    # Shift del número extraído como el máximo entre 0 y la diferencia de
    # bits leíbles y el offset: to_shift = max(0, readable - bits).
    to_shift = readable - bits
    to_shift = to_shift * (to_shift > 0)  # Predicado de max(0, y)
    number = extracted >> to_shift

    # Reducción de cantidad de bits a leer.
    bits -= readable

    # Si quedan bits por leer...
    if bits > 0:
        # Extracción de los bits restantes (del siguiente index).
        extracted = array[array_index+1] >> (32 - bits)

        # Corrimiento de bits más significativos del número leído al momento y
        # add de bits extraídos anteriormente.
        number = (number << bits) + extracted

    return number


def write_binary_in_barray(array, offset, number, bits):
    '''Permite la escritura binaria en un array de bytes desde el offset dado.

    Args:
        array (byte list): array sobre el que se realizará la escritura. Nota:
            debe haber suficiente espacio reservado para la cant. de bits a
            escribir.
        offset (int): nro. de bit de inicio de escritura en el array (visto
            como array de bits).
        bits (int): cant. de bits a escribir. Si el nro. se puede representar
            con menos de la cantidad especificada, se rellenará con ceros.

    Returns
        offset (int): nuevo offset en el array.
    '''
    # Si no hay nada que escribir...
    # if number == 0:
    #     return

    # Mientras la cantidad de bits a escribir sea mayor a 0.
    while bits > 0:
        # Index en el array.
        # array_index = int(offset / 8)
        array_index = offset >> 3

        # Bit index en el array index.
        # bit_index = int(offset % 8)
        bit_index = offset & 7

        # Espacio escribible.
        writable = 8 - bit_index

        # Bits a escribir en la ACTUAL iteración en el array index.
        # to_write = min(bits, writable)
        to_write = bits if (bits < writable) else writable

        # Shift a realizar, según los bits a escribir y el espacio escribible.
        # Ej: si se requieren escribir 11 bits y si el espacio escribible es 8,
        # se deberá realizar 3 corrimientos para escribir los primeros 8 bits.
        # Se utiliza abs(), ya que puede darse el caso en el que la cantidad de
        # bits a escribir sea menor al espacio escribible.
        shift = int(abs(bits - writable))

        # Si el espacio escribible es menor a la cantidad de bits a escribir...
        if writable < bits:
            # Suma en el array
            array[array_index] += number >> shift
        else:
            # Add de últimos bits (corrimiento a la izquierda).
            array[array_index] += number << shift

        # Eliminación de números escritos.
        number &= (0xFFFFFFFF >> (32 - shift))

        # Incremento de offset y reducción de bits a escribir.
        offset += to_write
        bits -= to_write
    return offset


def read_binary_from_barray(array, offset, bits):
    '''Permite la lectura binaria en un array de bytes desde el offset dado.

    Args:
        array (byte list): array sobre el que se realizará la lectura.
        offset (int): nro. de bit de inicio de lectura dentro del array (visto
            como array de bits).
        bits (int): cantidad de bits a leer.

    Returns
        number (int): número leído.
    '''
    number = 0

    while bits > 0:
        # Index en el array.
        # array_index = int(offset / 8)
        array_index = offset >> 3

        # Bit index en el byte index.
        # bit_index = int(offset % 8)
        bit_index = offset & 7

        # Bits leíbles en el byte.
        readable = 8 - bit_index

        # Cantidad de datos a leer como el mínimo entre la cantidad de bits
        # restantes a leer y lo leible. 'bits' será menor a 'readable' sólo
        # en la última iteración.
        # to_read = min(bits, readable)
        to_read = bits if (bits < readable) else readable

        # Extracción de todos los bits a la derecha del bit_index.
        # mask = (0xFF >> bit_index). Nota: 0xFF = 255
        extracted = (array[array_index] & (0xFF >> bit_index))
        # extracted = (array[array_index] & BIT_MASKS_8[bit_index])

        # Shift del número extraído como el máximo entre 0 y la diferencia de
        # bits leíbles y el offset. Cuando to_shift sea 0, se leerá el byte
        # entero. 'to_shift' será mayor a 0 sólo en la última iteración.
        # to_shift = max(0, readable - bits).
        to_shift = readable - bits
        to_shift = to_shift * (to_shift > 0)  # Predicado de max(0, y)
        shifted = extracted >> to_shift

        # Corrimiento de bits más significativos del número leído al momento y
        # add de shift calculado anteriormente.
        # Nota: si el nro. es 0, 'number << to_read' no tiene efecto.
        number = (number << to_read) + shifted

        # Add de shift al número.
        # number += shifted

        # Incremento de offset, según bits leídos.
        offset += to_read

        # Reducción de cantidad de bits a leer.
        bits -= to_read

    return number
