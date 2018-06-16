#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
- Nombre: gammaencoder.py
- Descripción: permite encode/decode de enteros a/desde Elias Gamma.
- Autor: Agustín González
- Modificado: 17/04/18
'''

import math

try:
    # Relative import.
    from . import bitbytearray as bbarray
    from . import unaryencoder as ue
    from . import bitutils
except:
    # Import para ejecución 'directa' del script.
    import time
    import bitutils
    import unaryencoder as ue
    import bitbytearray as bbarray


def compute_encoded_size(numbers):
    '''Calcula el tamaño de codificación final de la lista dada.

    Args:
        numbers (int list): números a codificar.

    Returns:
        size (int): tamaño de codificación final en bits.
    '''
    size = 0
    for number in numbers:
        number_size = (math.floor((math.log(number, 2))) << 1) + 1  # << 1 = *2
        size += number_size
    return size


def __to_vb(number):
    '''Codifica un entero a Variable Byte (de 8 bits, sin terminadores).

    Args:
        number (int): número a codificar.

    Returns:
        encoded (bytes): número codificado.
        padding (int): bits de relleno del último byte del encoded.
    '''
    # Bits requeridos para la representación original.
    required_bits = int(math.floor(math.log(number, 2))+1)

    # Eliminación de bit más significativo. -1 ya que es exponente (ej.: 2^0).
    number -= (2 ** (required_bits-1))

    # Nuevos bits req. (como se eliminó el bit más representativo, se resta 1).
    new_required_bits = required_bits-1

    # Bytes requeridos en la nueva representación.
    required_bytes = int(math.ceil((new_required_bits)/float(8)))

    # Cálculo de padding del número a codificar.
    padding = 8 - ((new_required_bits) & 7)  # % 8 = & 7
    if padding == 8:
        padding = 0

    # Shift de número según padding.
    number <<= padding

    # Conversión a secuencia de bytes.
    # encoded = number.to_bytes(required_bytes, byteorder="big")
    encoded = bbarray.bitbyteutils.to_bytes(required_bytes, number)
    return encoded, padding


def __merge_encodes(unary_encode, unary_padding, vb_encode, vb_padding):
    '''Unifica codificación unaria y vb.

    Args:
        unary_encode (byte list): codificación unaria de tamaño de número.
        unary_padding (int): bits de relleno del último byte del uencoded.
        vb_encode (byte list): codificación vb de número.
        vb_padding (int): bits de relleno del último byte del vbencoded.

    Returns:
        encoded (byte list): codificación final.
    '''
    encoded = bbarray.BitByteArray()

    encoded.extend(unary_encode, unary_padding)
    padding = encoded.extend(vb_encode, vb_padding)

    return encoded.to_bytearray(), padding


def encode(number):
    '''Codifica un entero a Gamma.

    Args:
        number (int): número a codificar.

    Returns:
        encoded (byte list): número codificado como array de bytes.
    '''
    # 1. Encode de número (vb).
    vbencoded, vbpadding = __to_vb(number)

    # Size de vb.
    size = (len(vbencoded)*8)-vbpadding

    # 2. Encode de size de número (unary).
    uencoded, upadding = ue.encode(size, optimize=False)

    # 3. Merge de encodes.
    encoded, padding = __merge_encodes(uencoded, upadding, vbencoded, vbpadding)
    return encoded, padding


def decode(encoded, nums):
    '''Decodifica una secuencia de bytes codificada en Gamma

    Args:
        encoded (byte list): números codificados.
        nums (int): cantidad de números a decodificar.

    Returns:
        decoded (int list): números decodificados.
    '''
    decoded = []

    offset = 0

    for _ in range(0, nums):
        # 1. Lectura unaria de tamaño de número (vb_size).
        uereturned = ue.decode(encoded, 1, False, offset)
        vb_size = uereturned[0]

        # +1 por 0 (cero) terminador de unary encode.
        offset += vb_size + 1

        # 2. Lectura binaria.
        number = bitutils.read_binary_from_barray(encoded, offset, vb_size)

        # Add de bit más significativo (eliminado en optimización de encode).
        # number += 2**vb_size
        number += (1 << vb_size)

        # 3. Add to decoded
        decoded.append(number)

        # Incremento de offset según bits leídos (vb_size).
        offset += vb_size

    return decoded


def main():
    '''Prueba de funcionamiento de las funciones encode y decode.'''
    # for i in range(1, 9999):
    #    encoded, _ = encode(i)
    #    print("\nOriginal: {0}".format(i))
    #    decoded = decode(encoded, 1)
    #    print("Decoded: {0}".format(decoded[0]))
    #    if i != decoded[0]:
    #        print("ATENCIÓN: number != decoded.")
    #        return

    # Prueba decoded de 1 millón de nros. (7, 3 repetido 500.000 veces).
    multiplier = 500000
    numbers = [7, 3] * multiplier
    encoded = [0b11011101] * multiplier
    print("Prueba de decode de 1 millón de enteros en curso...")
    # Decode
    start = time.time()
    decoded = decode(encoded, len(numbers))
    end = time.time()
    decoded_time = end-start

    if numbers != decoded:
        print(numbers[-5:], decoded[-5:])
        print("ATENCIÓN: numbers != decoded.")
        return

    print("Decoded time: {0}".format(decoded_time))

if __name__ == '__main__':
    main()
