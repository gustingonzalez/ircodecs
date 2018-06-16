#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
- Nombre: gapsencoder.py
- Descripción: permite encode/decode de enteros a/desde gaps, siendo un gap la
diferencia de c/elemento del listado con su antecesor (exceptuando al primero).
- Autor: Agustín González
- Modificado: 08/04/18
'''


def encode(numbers):
    '''Codifica una lista de números utilizando gaps.

    Args:
        numbers (int list): números a codificar.

    Returns:
        gaps (int list): números codificados.
    '''
    gaps = []

    gaps.append(numbers[0])

    for i in range(1, len(numbers)):
        gaps.append(numbers[i] - numbers[i-1])

    return gaps


def decode(gaps):
    '''Decodifica una lista de gaps.

    Args:
        gaps (int list): números codificados.

    Returns:
        numbers (int list): números decodificados.
    '''
    numbers = [gaps.pop(0)]

    for gap in gaps:
        numbers.append(gap + numbers[-1])

    return numbers


def main():
    '''Prueba de funcionamiento de las funciones encode y decode.'''

    numbers = [1000, 1001, 1009, 2000, 2009]

    encoded = encode(numbers)
    print(encoded)

    decoded = decode(encoded)
    print(decoded)


if __name__ == '__main__':
    main()
