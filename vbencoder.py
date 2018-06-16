#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
- Nombre: vbencoder.py
- Descripción: permite encode/decode de enteros a/desde Variable Byte.
- Autor: Agustín González
- Modificado: 18/04/18
'''

import time
import math


def compute_encoded_size(numbers):
    '''Calcula el tamaño de codificación final de la lista dada.

    Args:
        numbers (int list): números a codificar.

    Returns:
        size (int): tamaño de codificación final en bits.
    '''
    size = 0
    for number in numbers:
        # Bits requeridos para representar el número.
        required_bits = math.floor(math.log(number, 2))+1

        # Agregación de bits de overhead (1 por cada byte).
        required_bits += math.ceil(required_bits/8)

        # Utilización de bytes 'completos'.
        number_size = math.ceil(required_bits/8) << 3  # *8 = << 3

        size += number_size

    return size


def encode(number):
    '''Codifica un número a Variable Byte.

    Args:
        number (int): número a codificar.

    Returns:
        encoded (byte list): número codificado como array de bytes.
    '''
    encoded = []
    while True:
        # Add de byte al principio de la lista.
        encoded = [number & 127] + encoded  # n & 127 = n % 128
        if number < 128:
            break
        else:
            number = number >> 7  # n >> 7 = int(n / 128)

    # Add de 128 para activar el bit 8 del último byte (indica terminador).
    encoded[-1] += 128
    return encoded


def decode_number(encoded, offset=0):
    '''Decodifica un número codificado en Variable Byte desde el offset de la
    secuencia de bytes dada.

    Args:
        encoded (byte list): número/s codificado/s.
        offset (int): nro. de bit de inicio de lectura.

    Returns:
        number (int): número decodificado.
        offset (int): nuevo offset.
    '''
    number = 0

    byte_index = offset >> 3  # n >> 3 = int(n / 8)
    for i in range(byte_index, len(encoded)):
        byte = encoded[i]
        # number = 128 * number + byte
        number = (number << 7) + byte

        # Si bit 128 está activo...
        if byte > 127:
            # Eliminación de 128 correspondiente a bit más significativo.
            number = number - 128
            return number, (i+1)*8

    return 0, offset


def decode(encoded):
    '''Decodifica una secuencia de bytes codificada en Variable Byte.

    Args:
        encoded (byte list): números codificados.

    Returns:
        numbers (int list): números decodificados.
    '''
    numbers = []
    number = 0

    for byte in encoded:
        # number = 128 * number + byte
        number = (number << 7) + byte

        # Si bit 128 está activo...
        if byte > 127:
            # Eliminación de 128 correspondiente a bit más significativo.
            numbers.append(number-128)

            # Finalización de decode para número actual.
            number = 0

    return numbers


def main():
    '''Prueba de funcionamiento de las funciones encode y decode.'''
    print("Prueba de encode/decode de 1 millón de enteros en curso...")
    # upper = 1000000
    # numbers = sorted(set(list(random.sample(range(2, upper*2), upper))))
    numbers = list(range(0, 1000000))

    # Encode
    # gaps = gapsencoder.encode(numbers)
    start = time.time()
    encoded = []
    for number in numbers:
        encoded += encode(number)
    end = time.time()
    encoded_time = end-start

    # Decode
    start = time.time()
    decoded = decode(encoded)
    end = time.time()
    decoded_time = end-start

    if numbers != decoded:
        print(numbers[-5:], decoded[-5:])
        print("ATENCIÓN: numbers != decoded.")
        return

    print("Encoded time: {0}".format(encoded_time))
    print("Decoded time: {0}".format(decoded_time))

if __name__ == '__main__':
    main()
