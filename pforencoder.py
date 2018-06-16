#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
- Nombre: pforencoder.py
- Descripción: permite encode/decode de paquetes de enteros a/desde PFor
(NewPFor/OptPFor).
- Autor: Agustín González
- Modificado: 30/05/18

Nota: algoritmo basado en "Performance of Compressed Inverted List Caching
in Search Engines" de Zhang, Long y Suel y en implementación kamikaze de los
repositorios GitHub de @javasoze y @lemire: http://bit.ly/2EMv3YP.

Funcionamiento básico:
Siendo N una lista de números:
1. Se selecciona una cantidad de bits b que cubra el mayor número de nEN (90%).
2. Cada nEN codificado con b bits se almacena en una lista C. Pueden darse dos
   casos:
   1. n puede codificarse con b bits => se codifica n y se procede con n+1.
   2. n no puede codificarse con b bits => se codifican los b bits bajos de n
      y se agrega el elemento calculado a C. A su vez, siendo I una lista de
      índices que referencia a la ubicación de n en N, y dada E la lista de
      excepciones:
      1. Se almacena el índice de n relativo a N en I.
      2. Se almacenan los bits altos restantes de n en la lista E.
      3. Se procede con n+1.
3. Se unifican las listas I y E en IE
4. Se comprime IE utilizando S16.
5. Se almacena el número b y la cantidad de excepciones en H (32 bits).
6. encoded = [H] + C + IE
'''

import math

try:
    # Relative import.
    from . import simple16encoder
    from .bitutils import read_binary_from_iarray
    from .bitutils import write_binary_in_iarray
except:
    # Import para ejecución 'directa' del script.
    import time
    import simple16encoder
    from bitutils import read_binary_from_iarray, write_binary_in_iarray

# Posibles 'b'.
POSSIBLES_B = [x for x in range(1, 33)]

# Máscaras de lectura para vector 'POSSIBLES_B' (nota: es bastante más rápido
# un dict que realizar el cálculo por mask dentro de los encode/decode).
# Ejemplo de máscara para lectura de 4 bits: (1 << 4) es 5 (10000 binario),
# luego 5-1 es 4, 1111, la máscara adecuada.
MASKS = {x: (1 << x)-1 for x in range(0, 33)}

# Tamaño total de cabecera (1 entero para parámetro b y cantidad de exs).
HEADER_SIZE = 32

# Tamaño máximo de B en header (bit).
B_HEADER_SIZE = 5


def estimate_encoded_size(numbers, b):
    '''Estima el tamaño de codificación para la lista y el b dados. Se presupone
    un tamaño de excepción de 32 bits es decir, sin comprimir (lo que implica
    que las excepciones sean altamente 'penalizadas'). Nota: el tamaño de
    codificación es estimado, no final.

    Args:
        numbers (int list): números a codificar.
        b (int): cantidad de bits a utilizar por número.

    Returns:
        size (int): tamaño estimado de compresión.
    '''
    # Máximo número posible con b.
    max_number = MASKS[b]

    # Tamaño de header y slots.
    size = HEADER_SIZE + len(numbers)*b

    exception_count = 0
    for i in range(0, len(numbers)):
        if numbers[i] > max_number:
            exception_count += 1

    # Presunción de utilización de tamaño máximo (32 bits) por excepción.
    size += exception_count*32
    return size


def __find_optimal_b(numbers):
    '''Halla el b óptimo (cantidad de bits a utilizar por slot) en base a la lista
    de números pasada por parámetro.

    Args:
        numbers (int list): números a codificar.

    Returns:
        b (int): cantidad de bits óptima a utilizar para cada elemento de la
            lista de números a codificar.
    '''
    optimal_b = POSSIBLES_B[0]

    # Estimación de tamaño de compresión en base a b.
    optimal_size = estimate_encoded_size(numbers, optimal_b)

    # Selección del mejor b.
    for i in range(1, len(POSSIBLES_B)):
        current_b = POSSIBLES_B[i]

        # Tamaño para b actual.
        current_size = estimate_encoded_size(numbers, current_b)

        # ¿Es el b calculado mejor que el óptimo hasta el momento?
        if current_size < optimal_size:
            optimal_b = current_b
            optimal_size = current_size

    return optimal_b


def encode(numbers):
    '''Codifica una lista de números a PFor (NewPFor).

    Args:
        numbers (int list): números a codificar.

    Returns
        encoded(int list): lista de números codificada.
    '''
    # Parámetro b (máx número de bits por elemento)
    b = __find_optimal_b(numbers)

    # Lista de excepciones.
    exceptions = []

    # Índice de números del bloque catalogados como exceptions.
    exceptions_indexes = []

    # Excepciones.
    exceptions = []

    # Tamaño de encoded calculado como el cociente entre la cantidad de nros. y
    # la cantidad de slots disponibles por entero.
    numbers_per_int = math.floor(32/b)
    encoded_size = int(math.ceil(len(numbers)/numbers_per_int))
    encoded = [0] * encoded_size

    # Offset (en bits) en encoded.
    offset = 0

    for i in range(0, len(numbers)):
        number = numbers[i]

        # Si el número es mayor al máximo permitido...
        if number > MASKS[b]:
            # El número es una excepción...
            # Escritura de índice de la excepción.
            exceptions_indexes.append(i)

            # Escritura de los bits más significativos en lista de excepciones.
            upper = (number >> b)
            exceptions.append(upper)

            # Escritura de b bits menos significativos.
            number = number & MASKS[b]

        # Escritura en encoded.
        write_binary_in_iarray(encoded, offset, number, b)

        # Aumento de offset con paso b.
        offset += b

    # Eliminación de partes redundantes de encoded.
    # float(32), para compatibilidad con Py2
    used_ints = int(math.ceil(offset/float(32)))
    encoded = encoded[:used_ints]

    # Índice de exceptions y b se almacenan juntos.
    # Nota: b-1, ya que si b es 32, no se podría almacenar con 5 bits. Esto es
    # válido, ya que el valor mínimo de b es 1, no 0 (no hay riesgo de b<0).
    encoded.insert(0, (b-1 << (32-B_HEADER_SIZE)) + len(exceptions))
    # encoded.insert(1, len(numbers))

    # Encoded de índices y excepciones en Simple16.
    exception_encode = simple16encoder.encode(exceptions_indexes + exceptions)

    # Encoded final (header + blocks + excepcions)
    encoded += exception_encode

    return encoded


def __get_header(encoded):
    '''Retorna datos de header de la codificación dado.

    Args:
        encoded (int list): números codificados.

    Returns:
        bits (int): cantidad de bits utilizados por slot.
        exceptions_count (int): cantidad de excepciones en la codificación.
    '''
    offset = 32 - B_HEADER_SIZE

    # Param b+1, ya que se resta 1 en encode.
    bits = (encoded[0] >> offset)+1
    exceptions_count = encoded[0] & MASKS[offset]

    return bits, exceptions_count


def __merge_exceptions(decoded, exceptions, b):
    '''Unifica números decodificados con excepciones.

    Args:
        decoded (int list): decodificación sin incluir excepciones.
        exceptions (int list): lista de excepciones (con índices y exs).
        b (int): tamaño de bit slots (utilizado para offset en exceptions).

    Returns:
        decoded (int list): lista unificada (números codificados).
    '''
    # División de lista de excepciones en índices y excepciones.
    # middle = int(len(exceptions)/2)
    middle = len(exceptions) >> 1
    exceptions_indexes = exceptions[0:middle]
    exceptions = exceptions[middle:]

    for i in exceptions_indexes:
        exception = exceptions.pop(0) << b

        # Suma de exception al número indicado por el índice.
        decoded[i] += exception

    return decoded


def decode(encoded, nums):
    '''Decodifica una secuencia de enteros codificada en PFor (NewPFor).

    Args:
        encoded (int list): números codificados.
        nums (int): cantidad de números a decodificar.

    Returns:
        decoded (int list): números decodificados.
    '''
    # Obtención de header.
    header = __get_header(encoded)
    b = header[0]
    exceptions_count = header[1]

    # Eliminación de header.
    encoded = encoded[1:]
    decoded = []

    # > 1° fase de decodificación: batch decode (más rápida).
    offset = 0
    for _ in range(0, nums):
        decoded.append(read_binary_from_iarray(encoded, offset, b))
        offset += b

    # > 2° fase de decodificación (más lenta): excepciones.
    if exceptions_count > 0:
        ints_readed = int(math.ceil(offset/32))
        exceptions = encoded[ints_readed:]
        exceptions = simple16encoder.decode(exceptions)

        # Eliminación de posibles 0s decodificados (x2 ya que se almacenan
        # índices y excepciones). Nota: n*2 = n << 1
        exceptions = exceptions[0:(exceptions_count << 1)]
        decoded = __merge_exceptions(decoded, exceptions, b)

    return decoded


def main():
    '''Prueba de funcionamiento de las funciones encode y decode.'''
    print("Prueba de encode/decode de 1 millón de enteros en curso...")
    # upper = 1000000
    # numbers = sorted(set(list(random.sample(range(2, upper*2), upper))))
    numbers = list(range(1, 1000000))
    # numbers = [1, 2]

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
