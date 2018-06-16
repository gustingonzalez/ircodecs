#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
- Nombre: unaryencoder.py
- Descripción: permite encode/decode de enteros a/desde unario.
- Autor: Agustín González
- Modificado: 17/04/18
'''

import time
import math

# Máscaras de lectura de bit más significativo (de un byte).
READ_MSB_MASKS = {0: 128, 1: 64, 2: 32, 3: 16, 4: 8, 5: 4, 6: 2, 7: 1, 8: 0}

# Máscaras para obtención de los bits desde el índice dado (de un byte).
READ_SINCE_MASKS = {0: 255, 1: 127, 2: 63, 3: 31, 4: 15, 5: 7, 6: 3, 7: 1, 8: 0}


def compute_encoded_size(numbers, optimized=True):
    '''Calcula el tamaño de codificación final de la lista dada.

    Args:
        numbers (int list): números a codificar.
        optimized (bool): en True (por omisión), indica que NO se debe tener en
            cuenta el tamaño del bit más significativo de cada número codificado
            (que se supone eliminado en una posterior codificación).

    Returns:
        size (int): tamaño de codificación final en bits.
    '''
    size = 0
    for number in numbers:
        size += number

    if not optimized:
        size += len(numbers)

    return size


def encode(number, optimize=True):
    '''Codifica un número a Unario.

    Args:
        number (int): número a codificar.
        optimize (bool): indica si se debe eliminar el bit más significativo
            del número codificado. Por omisión, en True.

    Returns:
        encoded (byte list): número codificado como array de bytes.
        padding (int): relleno (en bits) del último byte de la codificación.
    '''
    # Bytes necesarios para la compresión (+1 para terminador).
    bytes_required = int(math.ceil((number+1)/float(8)))

    # Padding en último byte (en bits). -1 para tener en cuenta terminador.
    padding = 8 - (number % 8) - 1
    if padding == 8:
        padding = 0

    # Init de encoded
    encoded = bytearray(bytes_required)

    # Establecimiento de todos los bits en 1.
    encoded = [255 for _ in encoded]

    # Desplazamiento según padding (+1 para tener en cuenta terminador).
    encoded[-1] = (encoded[-1] << (padding + 1)) & 0xFF

    # Si es necesario optimizar (correr un bit)...
    if optimize:
        if number == 0:
            ex = "No es posible representar el 0 (cero) en unario optimizado."
            raise Exception(ex)

        # Si pad del últ. byte es 7, significa que sólo contiene terminador.
        if padding == 7:
            encoded.pop()

        # Corrimiento en un bit del último byte.
        encoded[-1] = (encoded[-1] << 1) & 0xFF

        # Se eliminó el bit más significativo, se incrementa padding.
        padding = padding + 1 if padding < 7 else 0

    # Retorno de encoded y padding.
    return encoded, padding


def decode(encoded, nums, is_optimized, offset=0):
    '''Decodifica una secuencia de bytes codificada en unario.

    Args:
        encoded (byte list): números codificados.
        nums (int): cantidad de números a decodificar.
        is_optimized (bool): indica si a los números resultantes se les deberá
            agregar un bit, consecuencia de una optimización en la codificación.
        offset (int): nro. de bit de inicio de lectura dentro del array (visto
            como array de bits).

    Returns:
        decoded (int list): números decodificados.
    '''
    decoded = []

    # Inicialización de número.
    number = int(is_optimized)

    # Byte index en el array. Nota: n >> 3 = n/8
    byte_index = offset >> 3

    # Bit index en el byte index. Nota: n & 7 = n % 8
    bit_index = offset & 7

    for _ in range(nums):
        # Obtención de máscara de lectura según bit index.
        read_mask = READ_SINCE_MASKS[bit_index]

        # Lectura de bits desde el offset dado.
        readed = encoded[byte_index] & read_mask

        # Si todos los bits leídos son 1s...
        if readed == read_mask:
            # Add a number de bits leídos desde el bit index.
            number += 8 - bit_index
            byte_index += 1

            # Optimización para números con más de 8 (ocho) 1s consecutivos.
            while encoded[byte_index] == 255:
                number += 8
                byte_index += 1

            # Último byte a evaluar: contiene 1s y 0s.
            readed = encoded[byte_index]

            # Próxima lectura de readed desde el bit inicial.
            bit_index = 0

        # Verificación de leading 1s de readed: ciclo mientras el valor sea 1.
        while readed & READ_MSB_MASKS[bit_index]:
            number += 1
            bit_index += 1

        # Add de number
        decoded.append(number)

        # Next number.
        number = int(is_optimized)

        # Actualización bit_index y byte_index
        bit_index = (bit_index + 1) & 7
        byte_index += (bit_index == 0)

    return decoded


def main():
    '''Prueba de funcionamiento de las funciones encode y decode.'''
    # 1. Prueba de encode y decode de un único número en un byte.
    # print("Descompresión de un único número en un byte.")
    # optimize = False
    # for i in range(1, 9999):
    #    print("")
    #    encoded, padding = encode(i, optimize=optimize)
    #    decoded = decode(encoded, 1, optimize)[0]
    #    print("Original: {0}".format(i))
    #    print("Decoded: {0} - padding: {1}".format(decoded, padding))
    #    if i != decoded:
    #        print("ATENCIÓN: number != decoded.")
    #        return

    # 2. Prueba de descompresión de 5 números empaquetados en más de un byte
    # (separados entre bytes). Contiene: [1, 1, 3, 4, 0].
    # encoded = [0b10101110, 0b11110000]

    # 3. Prueba de 1000000 de elementos. Contiene: 6 y 8.
    multiplier = 500000
    numbers = [6, 8] * multiplier
    encoded = [0b11111101, 0b11111110] * multiplier
    is_optimized = False
    print("Prueba de decode de 1 millón de enteros en curso...")

    # Decode
    start = time.time()
    decoded = decode(encoded, len(numbers), is_optimized)
    end = time.time()
    decoded_time = end-start

    if numbers != decoded:
        print(numbers[-5:], decoded[-5:])
        print("ATENCIÓN: numbers != decoded.")
        return

    print("Decoded time: {0}".format(decoded_time))

if __name__ == '__main__':
    main()
