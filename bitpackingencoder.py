#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
- Nombre: bitpackingencoder.py
- Descripción: permite encode/decode de enteros a/desde paquetes de bits.
- Autor: Agustín González
- Modificado: 17/04/18
'''

import time
import math

try:
    # Relative import.
    from . import vbencoder
    from . import unaryencoder as ue
    from .bitutils import write_binary_in_barray, read_binary_from_barray
except:
    # Import para ejecución 'directa' del script.
    import vbencoder
    import unaryencoder as ue
    from bitutils import read_binary_from_barray, write_binary_in_barray


def compute_encoded_size(numbers):
    '''Calcula el tamaño de codificación final de la lista dada.

    Args:
        numbers (int list): números a codificar.

    Returns:
        size (int): tamaño de codificación final en bits.
    '''
    # Máximo número.
    max_number = sorted(numbers)[-1]

    # Bits utilizados por número.
    b = math.floor(math.log(max_number, 2))+1

    # Bits requeridos para codificar los núms.
    size = b*len(numbers)

    # Bits requeridos para param b.
    size += vbencoder.compute_encoded_size([b])

    return size


def encode(numbers):
    '''Codifica una lista de números como paquetes de bits.

    Args:
        numbers (int list): números a codificar.

    Returns
        encoded(int list): números codificados.
        padding (int): relleno (en bits) del último byte de la codificación.
    '''
    # Máximo número.
    max_number = sorted(numbers)[-1]

    # Bits utilizados por número.
    b = int(math.floor(math.log(max_number, 2))+1)

    # Bits requeridos para codificar todos los números.
    bits_required = b*len(numbers)

    # Bytes requeridos para codificar todos los números.
    bytes_required = int(math.ceil(bits_required/8.0))

    # Inicialización de array según cantidad de bytes requeridos.
    encoded = [0] * bytes_required

    offset = 0
    for number in numbers:
        write_binary_in_barray(encoded, offset, number, b)
        offset += b

    header = vbencoder.encode(b-1)  # param b.

    encoded = bytearray(header + encoded)

    # Relleno de encoded.
    padding = 8 - (bits_required % 8)

    if padding == 8:
        padding = 0

    return encoded, padding


def decode(encoded, nums):
    '''Decodifica una secuencia de paquetes de bits.

    Args:
        encoded (bytes): números a decodificar.
        nums (int): cantidad de números a decodificar.

    Returns:
        number (int): números decodificados.

    Nota: no es necesario padding, ya que el parámetro 'nums' indica cuántos
    números deben decodificarse.
    '''
    b, offset = vbencoder.decode_number(encoded)

    # Add de 1 eliminado en b.
    b += 1

    # Decoded
    decoded = [read_binary_from_barray(encoded, offset+(i*b), b) for i in range(0, nums)]
    return decoded


def main():
    '''Prueba de funcionamiento de las funciones encode y decode.'''
    print("Prueba de encode/decode de 1 millón de enteros en curso...")
    # upper = 1000000
    # numbers = sorted(set(list(random.sample(range(2, upper*2), upper))))
    numbers = list(range(0, 1000000))

    # Encode
    # gaps = gapsencoder.encode(numbers)
    start = time.time()
    encoded, _ = encode(numbers)
    end = time.time()
    encoded_time = end-start

    # Decode
    start = time.time()
    decoded = decode(encoded, len(numbers))
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
