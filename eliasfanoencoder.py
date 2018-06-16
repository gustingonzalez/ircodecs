#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
- Nombre: eliasfanoencoder.py
- Descripción: permite encode/decode de enteros a/desde Elias Fano.
- Autor: Agustín González
- Modificado: 22/04/18

Breve reseña sobre Elias Fano (EF): dada N una lista creciente de números y
siendo u=max(N), N se subdivide en otras dos listas: U y L. Mientras que, en
la primera lista, se almacenan los gaps unarios de los ceil(log2(u))-l bits
altos de cada nEN con l=ceil(log2(u/m)) y m=|N|, en la segunda se almacenan los
l bits bajos. En efecto, la codificación EF de N se define como L + U. Nota:
aunque la especificación original sugiere almacenar U + L, esta implementación
se basa en la del repositorio Github de @catenamatteo (https://bit.ly/2EZh9ST)
dado que, como los bits bajos se codifican en bloques fijos, es posible conocer
de antemano el inicio de la sección superior, lo cual permite la decodificación
utilizando una única estructura cíclica: de otro modo, primero se debería
decodificar la totalidad de bits superiores y, en otro ciclo, los inferiores.

EF Multinivel: en el paper "Partitioned Elias-Fano Indexes" de Ottaviano
y Venturini (https://bit.ly/2qNiFDg), se propone una versión de Elias Fano
de dos niveles para lograr un mejor rate de compresión.

EF Local, una alternativa a EF Multinivel: dado que la implementación aquí
presente se ha utilizado en la propuesta de un esquema de compresión múltiple,
se requería una versión donde cada partición de lista pueda decodificarse
por sí misma (sin depender de una representación superior). De este modo, esta
implementación se presenta como una alternativa a EF Multinivel (aunque con un
fuerte basamento en esta).

Otras cuestiones:
- Cuando |N|>u/4, se utilizan vectores característicos (al igual que se sugiere
 en https://bit.ly/2qNiFDg).
- Las listas de tamaño 1, se comprimen utilizando VByte (esto tiene sentido
si se tiene en cuenta que, en el EF local propuesto, el primer número siempre
se comprime con esta codificación).
'''

import math

try:
    # Relative import.
    from . import bitutils
    from . import gapsencoder
    from . import unaryencoder
    from . import vbencoder as vbenc
    from .bitbytearray import BitByteArray, bitbyteutils as bbutils
except:
    # Import para ejecución 'directa' del script.
    import time
    import bitutils
    import gapsencoder
    import unaryencoder
    import vbencoder as vbenc
    from bitbytearray import BitByteArray, bitbyteutils as bbutils

# Diccionario de posibles máscaras de bits de 0 a 32.
MASKS = {x: (1 << x)-1 for x in range(0, 33)}

# Máscaras de lectura para bit vectors.
BV_MASKS = {0: 128, 1: 64, 2: 32, 3: 16, 4: 8, 5: 4, 6: 2, 7: 1}


def __delta_encode_since_min(numbers):
    '''Siendo 'y' el 1er número del listado pasado por parámetro, decrementa
    este valor a todos los restantes. A su vez, posterior a esta operación,
    reconstruye 'y' de la forma y=[x, z], con z=min(numbers[1], y)-1 y x=y-z.

    Args:
        numbers (int list): números a codificar.

    Returns
        encoded (int list): números codificados.
    '''
    # 1. Encoded a partir del segundo número.
    encoded = [number - numbers[0] for number in numbers[1:]]

    # 2. Recálculo del primer número.
    num1 = numbers[0]

    # Si el primer número es 0, no tiene sentido realizar el proceso, puesto
    # que en el siguiente paso, 0-1=-1, el cual no es admisible por en encodeo
    # unario. Se retorna [0] añadido al listado, para 'preservar' la posterior
    # lectura.
    if num1 == 0:
        return [0] + numbers

    # Mínimo entre el 1er número del encoded y el 1er número original, lo que
    # permite obtener el máximo primer número que luego se codificará en EF.
    # Se substrae un 1 adicional lo cual evita la posibilidad de que el EF
    # 1st number sea igual al (del hasta el momento) primer número del encoded.
    # Este nro. luego será el segundo del encoded.
    fano_1st_number = min(encoded[0]-1, num1-1)

    # 1er número del encoded calculado como num1 - Fano 1st number.
    vb_number = num1 - fano_1st_number

    # Add de números anteriores al encoded.
    encoded = [vb_number, fano_1st_number] + encoded
    return encoded


def __delta_decode_since_min(encoded):
    '''Añade, a todos los números del listado, la suma del 1er y 2do número de
    la codificación.

    Args:
        encoded (int list): números a decodificar.

    Returns
        decoded (int list): números decodificados.
    '''
    num1 = encoded[0] + encoded[1]
    decoded = [num1]
    decoded += [(num1 + number) for number in encoded[2:]]
    return decoded


def bv_encode(numbers):
    '''Codifica una lista de números utilizando un vector característico.

    Args:
        numbers (int list): números a codificar.

    Returns:
        encoded (byte list): lista codificada.
        padding (int): relleno (en bits) del último byte de la codificación.
    '''
    max_number = numbers[-1]
    encoded = bytearray(int(math.ceil(float(max_number+1)/8)))

    for number in numbers:
        array_index = number >> 3  # int(number/8)
        bit_index = number & 7     # number % 8

        # Establecimiento en 1 del índice correspondiente al número.
        encoded[array_index] = encoded[array_index] | BV_MASKS[bit_index]

    padding = 8 - ((max_number+1) & 7)
    padding = padding * (padding < 8)

    return encoded, padding


def bv_decode(encoded, nums, offset):
    '''Decodifica un vector característico de números.

    Args:
        encoded (int list): números codificados.
        nums (int): cantidad de números a decodificar.
        offset (int): nro. de bit de inicio de lectura.

    Returns:
        decoded (int list): números decodificados.
    '''
    decoded = []

    # Índice de array.
    array_index = (offset >> 3)

    # Bit index en el byte especificado por el array index.
    bit_index = (offset) & 7

    number = 0

    # Max number según bits...
    max_number = len(encoded[array_index:]) << 3  # << 3 = * 8

    # '<' y no '<='ya que number comienza desde 0 (cero)
    while number < max_number:
        if encoded[array_index] == 255:
            decoded.extend(range(number, number+8))
            number += 8

            # Incremento de array index. Lecturas de bytes restantes desde 0.
            array_index += 1
            bit_index = 0
            continue

        # Comprobación bit a bit.
        for readed_bit in range(bit_index, 8):
            # Si el bit está activo...
            if encoded[array_index] & BV_MASKS[readed_bit]:
                decoded.append(number)
            number += 1

        # Incremento de array index. Lecturas de bytes restantes desde 0.
        array_index += 1
        bit_index = 0

    # Return y eliminación de padding.
    return decoded[:nums]


def __encode_upper(upper_numbers):
    '''Codifica y realiza gaps de una lista de números, que representan los
    números superiores (upper numbers) de una codificación EF.

    Args:
        upper_numbers (int list): lista de upper numbers.

    Returns:
        upper_bits (BitByteArray): representación binaria de upper numbers.
    '''
    # Gaps.
    upper_gaps = gapsencoder.encode(upper_numbers)

    # Encode de gaps.
    upper_bbarray = BitByteArray()
    for number in upper_gaps:
        uencode, padding = unaryencoder.encode(number, optimize=False)
        upper_bbarray.extend(uencode, padding)

    return upper_bbarray


def __encode_lower(lower_numbers, l):
    '''Codifica una lista de números, que representan los números bajos (lower
    numbers) de una codificación EF.

    Args:
        lower_numbers (int list): lista de lower numbers.
        l (int): cantidad de bits utilizados por número en la parte baja.

    Returns:
        lower_bits (BitByteArray): representación binaria de lower numbers.
    '''
    # Padding necesario del último byte en la representación del número como
    # una secuencia de bytes.
    padding = (8 - (l % 8))
    if padding == 8:
        padding = 0

    lower_bbarray = BitByteArray()
    for number in lower_numbers:
        # Corrimiento según padding.
        number = number << padding
        number = bbutils.to_bytes(int(math.ceil(l/float(8))), number)
        lower_bbarray.extend(number, padding)

    return lower_bbarray


def __merge_encodes(l, lower_encode, upper_encode):
    '''Unifica las codificaciones lower y upper, agregando header.

    Args:
        l (int): cantidad de bits utilizados por número en la parte baja.
        lower_encode (int list): codificación de lower numbers.
        upper_encode (int list): codificación de upper numbers.

    Returns:
        encoded (byte list): codificación final.
        padding (int): cantidad de bits de relleno del último byte.
    '''
    lower_encode.extend(upper_encode, upper_encode.padding())

    lheader = bbutils.to_byte(l)

    padding = lower_encode.padding()

    encoded = bytearray(lheader + lower_encode.to_bytearray())
    return encoded, padding


def encode(numbers):
    '''Codifica una lista de números a Elias Fano.

    Args:
        numbers (int list): números a codificar.

    Returns:
        encoded (byte list): números codificados.
    '''
    if len(numbers) == 1:
        return vbenc.encode(numbers[0]), 0

    numbers = __delta_encode_since_min(sorted(numbers))
    first_number = numbers.pop(0)
    max_number = numbers[-1]

    # Parámetro 'u'.
    list_size = len(numbers)

    # 1. Uso de bit vector su la secuencia es 'densa' (ver paper Ottaviano).
    if list_size > (max_number >> 2):  # >> 2 = /4
        encoded = vbenc.encode(first_number)
        # Add de header indicador de bit vector encode.
        encoded.append(255)

        # bv encode.
        bvencode, padding = bv_encode(numbers)
        encoded += bvencode
        return encoded, padding

    # 2. Elias Fano encoding.
    delta = max_number/list_size

    # Parámetro l.
    l = int(math.ceil(math.log(delta, 2)))
    upper_numbers = []
    lower_numbers = []

    mask = MASKS[l]
    for number in numbers:
        lower = number & mask
        upper = (number - lower) >> l

        upper_numbers.append(upper)
        lower_numbers.append(lower)

    # 1. Encode unary de upper bits.
    upper_encode = __encode_upper(upper_numbers)

    # 2. Encode l bits de lower bits.
    lower_encode = __encode_lower(lower_numbers, l)

    # 3. Merge
    encoded = []
    encoded = bytearray(vbenc.encode(first_number))
    merged, padding = __merge_encodes(l, lower_encode, upper_encode)
    encoded += merged

    return encoded, padding


def decode(encoded, nums):
    '''Decodifica una lista codificada en Elias Fano.

    Args:
        encoded (int list): números codificados.
        nums (int): cantidad de números a decodificar.

    Returns:
        decoded (int list): números decodificados.
    '''
    # Lectura de primer número vb.
    decoded = []
    if nums == 1:
        return vbenc.decode(encoded)

    first_number, offset = vbenc.decode_number(encoded)
    decoded = [first_number]

    # Lectura de header. Nota: >> 3 = /8
    l = encoded[(offset >> 3)]
    offset += 8
    lower_offset = offset
    upper_offset = offset + ((l * nums))

    # 1. Si l es 11111111, entonces se ha utilizado un bit vector.
    if l == 255:
        decoded += bv_decode(encoded, nums, offset)
        return __delta_decode_since_min(decoded)

    # Elias Fano decode.
    delta = 0
    for _ in range(nums):
        # Decode de lower y upper
        lower = bitutils.read_binary_from_barray(encoded, lower_offset, l)
        upper = unaryencoder.decode(encoded, 1, False, upper_offset)[0]

        # Incremento para próxima lectura.
        delta += upper

        decoded.append((delta << l) + lower)

        # Incremento lower offset.
        lower_offset += l

        # Incremento upper offset: +1 por terminador.
        upper_offset += upper + 1

    return __delta_decode_since_min(decoded)


def main():
    '''Prueba de funcionamiento de las funciones encode y decode.'''
    print("Prueba de encode/decode de 1 millón de enteros en curso...")
    # numbers = [17, 19, 22, 25]
    numbers = list(range(0, 5000000, 5))
    # upper = 1000000
    # numbers = sorted(set(list(random.sample(range(2, upper*2), upper))))

    # Encode
    # gaps = gapsencoder.encode(numbers)
    start = time.time()
    encoded = encode(numbers)[0]
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
