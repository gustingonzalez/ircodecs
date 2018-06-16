#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
- Nombre: simple16encoder.py
- Descripción: permite encode/decode de paquetes de enteros a/desde Simple16.
- Autor: Agustín González
- Modificado: 17/04/18
'''

import time

# Posibles combinaciones de bits a comprimir (ord. de slots de mayor a menor).
# Nota: listado basado en "Performance of Compressed Inverted List Caching
# in Search Engines" de Zhang, Long y Suel y en implementación kamikaze
# expuesta en los repositorios GitHub de @javasoze y @lemire:
# http://bit.ly/2mG6jKG.
S16_FORMATS = {15: [1]*28,                 # 28 slots
               14: [2]*7 + [1]*14,         # 21 slots
               13: [1]*7 + [2]*7 + [1]*7,  # 21 slots
               12: [1]*14 + [2]*7,         # 21 slots.
               11: [2]*14,                 # 14 slots.
               10: [4] + [3]*8,            # 9 slots.
               9: [3] + [4]*4 + [3]*3,     # 8 slots.
               8: [4]*7,                   # 7 slots.
               7: [5]*4 + [4]*2,           # 6 slots.
               6: [4]*2 + [5]*4,           # 6 slots.
               5: [6]*3 + [5]*2,           # 5 slots.
               4: [5]*2 + [6]*3,           # 5 slots.
               3: [7]*4,                   # 4 slots.
               2: [10] + [9]*2,            # 3 slots.
               1: [14]*2,                  # 2 slots.
               0: [28]}                    # 1 slot.

# Keys de diccionario anterior ordenadas de forma decreciente (16, 15, 14...).
S16_FORMAT_KEYS_REVERSED = list(reversed(sorted(S16_FORMATS.keys())))

# Diccionario de posibles máscaras de bits de 0 a 32.
MASKS = {x: (1 << x)-1 for x in range(0, 33)}


def find_optimal_format(numbers, start):
    '''Busca el formato S16 óptimo para una lista de números.

    Args:
        numbers (list int): lista de la que se requiere hayar el formato S16.
        start (int): índice desde el que se evaluará la lista de números.

    Returns:
        format (int): índice de formato (de S16_FORMATS) a utilizar.
        slots_size (int): cantidad de números a codificar con el formato S16,
            desde el índice 0 de 'numbers'.
    '''
    # Verificación de keys en orden descendente.
    for s16f in S16_FORMAT_KEYS_REVERSED:
        # Slots permitidos por el formato s16.
        slots_size = len(S16_FORMATS[s16f])

        # Si la cant. de slots del formato s16 es mayor a la cantidad de nros.
        # a codificar, se establece la cantidad de slots permitidos como el len
        # de nros., para evitar un 'sobre-ajuste'. Ej.: dada una lista de 27
        # nros '1', el formato más 'lógico' es el 16 (que permite 28 1s). Sin
        # embargo, sin esta sentencia, se escogería un formato del 13 al 15 (21
        # slots) y el 9 (4 slots), lo que resultaría, en vez de 32 bits, en una
        # compresión de 64 bits (por 'sobre-ajuste') Nota: los ceros al final
        # del encoded deberían ser eliminados en una 'capa superior.'
        if slots_size > len(numbers)-start:
            slots_size = len(numbers)-start

        # Si la cantidad de slots especificados del formato s16 se ajusta para
        # cada número verificado...
        slots = S16_FORMATS[s16f]
        if all(MASKS[slots[i]] >= numbers[start+i] for i in range(0, slots_size)):
            return s16f, len(slots)

        # Sino: se continúa prueba con el siguiente formato s16.


def encode(numbers):
    '''Codifica una lista de números a S16.

    Args:
        numbers (int list): números a codificar.

    Returns:
        encoded (int list): números codificados.
    '''
    encoded = []
    start = 0  # Índice desde el que se evaluará numbers.
    while start < len(numbers):
        s16format, numbers_to_encode = find_optimal_format(numbers, start)
        to_encode = numbers[start: start+numbers_to_encode]

        # Incremento de índice de start para próxima evaluación.
        start += numbers_to_encode

        # Bits a mover para tener en cuenta header.
        bits_to_move = 28

        # Lote codificado.
        encoded_batch = (s16format) << bits_to_move

        for i in range(0, len(to_encode)):
            bits_to_move -= S16_FORMATS[s16format][i]
            shifted = to_encode[i] << bits_to_move
            encoded_batch += shifted

        encoded.append(encoded_batch)

    return encoded


def decode_batch(batch, s16format):
    '''Decodifica un lote de 32 bits utilizando el formato S16 especificado.

    Args:
        batch (int): lote de 32 bits a decodificar.
        s16format (int): formato s16 a utilizar para la codificación.

    Returns:
        numbers (int list): números decodificados.
    '''
    numbers = []
    offset = 0

    for bits_to_process in S16_FORMATS[s16format]:
        # Incremento de offset según siguiente bit a procesar
        offset += bits_to_process

        # Obtención de número y append.
        # number = (batch >> 28-offset) & MASKS[bits_to_process]
        numbers.append((batch >> 28-offset) & MASKS[bits_to_process])
    return numbers


def decode(encoded, remove_trailing_zeros=True):
    '''Decodifica una secuencia de enteros codificada en S16.

    Args:
        encoded (int list): números codificados.
        remove_trailing_zeros (bool): por defecto en True, especifica si se
            deben eliminar los ceros finales de la lista decodificada.

    Returns:
        numbers (int list): números decodificados.
    '''
    numbers = []

    header_mask = MASKS[5]
    for batch in encoded:
        # s16format = (batch >> 28) & header_mask
        numbers.extend(decode_batch(batch, (batch >> 28) & header_mask))

    # Eliminación de trailing zeros.
    if remove_trailing_zeros:
        while numbers and numbers[-1] is 0:
            # numbers.pop()
            del numbers[-1]

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
    encoded = encode(numbers)
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
