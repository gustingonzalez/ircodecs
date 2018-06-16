#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
- Nombre: decodespeedtest.py
- Descripción: mide el tiempo de decodificación (en ints/sec) de los métodos de
compresión BPacking, EF, Gamma, PFD, S16, Unario y VB. Para ello, con cada
codificación, se comprime una secuencia de gaps correspondiente a una lista
creciente de 1 millón de enteros y luego se mide el tiempo de descompresión de
c/u. Dado que EF comprime la lista original usando delta encode internamente,
para equiparar, el tiempo de decodificación de gaps se añade en las restantes
mediciones. Esta operación se realiza 5 veces, aunque también se realiza una
inicial (a modo de 'warm-up'), que no se toma en cuenta para el promedio final.
Además, por cada repetición, la distancia entre números se duplica. Es decir,
en la 1era iteración (pertinente a la medición), se prueba la secuencia
S=[1, 2, 3], en la 2da S=[1, 3, 5], en la 3era S=[1, 5, 9] y así sucesivamente.
- Autor: Agustín González
- Modificado: 02/06/17
'''

import sys
import time

import vbencoder as vbenc
import gammaencoder as gaenc
import unaryencoder as unenc
import pforencoder as pfdenc
import gapsencoder as gapsenc
import eliasfanoencoder as efenc
import simple16encoder as s16enc
import bitpackingencoder as bpenc
from bitbytearray import BitByteArray


NUMBERS_COUNT = 1000000
NUMBERS_DISTANCE = 1


def main():
    # Cantidad de pruebas (sin tener en cuenta 'warm-up')
    iterations = 5

    # Tiempos totales de decodificación de c/método.
    bptotaltime = 0
    eftotaltime = 0
    pfdtotaltime = 0
    s16totaltime = 0
    vbtotaltime = 0
    unarytotaltime = 0
    gammatotaltime = 0

    numbers_distance = NUMBERS_DISTANCE
    for i in range(0, iterations+1):
        numbers = range(1, (NUMBERS_COUNT*numbers_distance)+1, numbers_distance)
        print("Iteración nro. {0} en curso...".format(i))

        # EF test.
        encode = efenc.encode(numbers)[0]
        start = time.time()
        efenc.decode(encode, NUMBERS_COUNT)
        end = time.time()
        eftime = end - start

        # Codificación gaps para restantes codificaciones.
        numbers = gapsenc.encode(numbers)

        # Bit packing test.
        encode = bpenc.encode(numbers)[0]
        start = time.time()
        gapsenc.decode(bpenc.decode(encode, NUMBERS_COUNT))
        end = time.time()
        bptime = end - start

        # PFD test.
        encode = pfdenc.encode(numbers)
        start = time.time()
        gapsenc.decode(pfdenc.decode(encode, NUMBERS_COUNT))
        end = time.time()
        pfdtime = end - start

        # S16 test.
        encode = s16enc.encode(numbers)
        start = time.time()
        gapsenc.decode(s16enc.decode(encode, NUMBERS_COUNT))
        end = time.time()
        s16time = end - start

        # VB test.
        for n in numbers:
            encode.extend(vbenc.encode(n))
        start = time.time()
        gapsenc.decode(vbenc.decode(encode))
        end = time.time()
        vbtime = end - start

        # Unary test.
        encode = BitByteArray()
        for n in numbers:
            encode.extend(unenc.encode(n, optimize=True)[0])
        start = time.time()
        gapsenc.decode(unenc.decode(encode, NUMBERS_COUNT, is_optimized=True))
        end = time.time()
        unarytime = end - start

        # Gamma test.
        encode = BitByteArray()
        for n in numbers:
            encode.extend(gaenc.encode(n)[0])
        start = time.time()
        gapsenc.decode(gaenc.decode(encode, NUMBERS_COUNT))
        end = time.time()
        gammatime = end - start

        # Warm-up
        if i == 0:
            continue

        # Incremento de distancia.
        numbers_distance *= 2

        bptotaltime += bptime
        eftotaltime += eftime
        pfdtotaltime += pfdtime
        s16totaltime += s16time
        vbtotaltime += vbtime
        unarytotaltime += unarytime
        gammatotaltime += gammatime

    # Tiempo promedio de decodificación.
    bpavgtime = bptotaltime/iterations
    efavgtime = eftotaltime/iterations
    pfdavgtime = pfdtotaltime/iterations
    s16avgtime = s16totaltime/iterations
    vbavgtime = vbtotaltime/iterations
    unaryavgtime = unarytotaltime/iterations
    gammaavgtime = gammatotaltime/iterations

    # Velocidades de decodificación.
    bpdecspeed = round(NUMBERS_COUNT/bpavgtime, 2)
    efdecspeed = round(NUMBERS_COUNT/efavgtime, 2)
    pfdecspeed = round(NUMBERS_COUNT/pfdavgtime, 2)
    s16decpeed = round(NUMBERS_COUNT/s16avgtime, 2)
    vbdecspeed = round(NUMBERS_COUNT/vbavgtime, 2)
    unarydecspeed = round(NUMBERS_COUNT/unaryavgtime, 2)
    gammadecspeed = round(NUMBERS_COUNT/gammaavgtime, 2)

    # Results.
    print("")
    print("Versión de Python: {0}".format(sys.version.split(' ')[0]))
    print("Resultados {0}".format(time.strftime("%d/%m/%y %X")))
    print("")
    print("Bit packing (ints/sec): {0}".format(bpdecspeed))
    print("Elias Fano (ints/sec): {0}".format(efdecspeed))
    print("PForDelta (ints/sec): {0}".format(pfdecspeed))
    print("Simple 16 (ints/sec): {0}".format(s16decpeed))
    print("Variable Byte (ints/sec): {0}".format(vbdecspeed))
    print("Unary (ints/sec): {0}".format(unarydecspeed))
    print("Gamma (ints/sec): {0}".format(gammadecspeed))

if __name__ == '__main__':
    main()
