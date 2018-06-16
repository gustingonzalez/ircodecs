#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
- Nombre: __init__.py (bitbytearray)
- Descripción: contiene la clase 'BitByteArray' (ver docstring).
- Autor: Agustín González
- Modificado: 16/04/18
'''
from . import bitbyteutils as bbutils


class BitByteArray(object):
    '''Permite trabajar secuencias de bits en base a un array de bytes (bbarray),
    lo cual es útil puesto que 'byte' es el tamaño mínimo de lectura/escritura
    impuesto por los sistemas operativos y lenguajes.'''

    def __init__(self, elements=None):
        '''Inicializa clase.

        Args:
            elements (byte list): bytes con los que inicializará el array.
        '''
        # Array. Nota: no se utiliza 'bytes()' ya que no es mutable.
        self.__stream = bytearray()

        # Pointer de bit en byte.
        self.__bit_pointer = 0

        if elements:
            self.append(elements)

    def __getitem__(self, key):
        '''Implementa invocación del tipo array[key].

        Args:
            key (int): índice del array a accesar.

        Returns:
            value (byte): valor especificado dentro del array.
        '''
        return self.__stream[key]

    def __setitem__(self, key, value):
        '''Permite establecer el valor de un elemento del array de la forma
        'array[key] = value'.

        Args:
            key (int): índice del valor a modificar.
            value (byte): nuevo valor del elemento especificado.
        '''
        self.__stream[key] = value

    def __str__(self):
        '''Retorna representación imprimible del bytearray interno al invocar
        la función str(array).

        Returns:
            array (str): representación imprimible del array interno.
        '''
        return str(self.__stream)

    def __iadd__(self, element):
        '''Permite agregar un elemento de la forma array += value.

        Args:
            element (byte): elemento a agregar a la secuencia.
        '''
        self.append(element)

    def __len__(self):
        '''Retorna la cantidad de bytes del array.

        Returns:
            len (int): cantidad de bytes del array.
        '''
        return len(self.__stream)

    def clear(self):
        '''Elimina todos los elementos del array.'''
        self.__stream.clear()

    def to_bytearray(self):
        '''Convierte el bit byte array a un array de bytes.

        Returns:
            array (byte list): representación del objeto como array de bytes.
        '''
        return self.__stream

    def has_data(self):
        '''Retorna verdadero si el array contiene datos.

        Returns:
            True, si el array tiene datos, False en caso contrario.
        '''
        return True if self.__stream else False

    def close_byte(self):
        '''Cierra el último byte del array estableciendo el puntero de bit en 0.

        Returns:
            old_bit_pointer (int): posición del bit pointer previo al cierre
                del último byte.
        '''
        old_bit_pointer = self.__bit_pointer

        # Seteo en 0 de bit pointer (lo que indica que luego deberá ser escrito
        # otro byte desde 'append()': por ello no se incrementea el bpointer
        # desde aquí).
        self.__bit_pointer = 0

        return old_bit_pointer

    def padding(self):
        '''Retorna el tamaño de relleno del último byte del array.

        Returns:
            padding (int): bits de relleno del último byte.
        '''
        padding = 8 - self.__bit_pointer

        if padding == 8:
            padding = 0

        return padding

    def __recompute_bit_pointer(self, padding):
        '''Recomputa el puntero del bit array, según el padding del (se supone)
        último byte agregado.

        Args:
            padding (int): bits de relleno del último byte agregado.
        '''
        bbutils.validate_padding(padding)

        # Si padding es cero, el pointer se mantiene sin cambios.
        if padding == 0:
            return

        # Cálculo de offset como la dif. entre el tamaño de byte y el padding.
        offset = (8 - padding)

        # Add de offset a bitpointer (se calcula resto en caso de pasarse). Si
        # no hay padding (porque se agregaron bloques completos de 8 bits), el
        # bpointer se mantiene (ya que se calcula según MOD 8). Ej: si bpointer
        # es 2 y se agrega 1 bloque de 8 bits sin padding, bpointer estaría
        # dado por (bit pointer + 0) % 8 lo que es igual a bit pointer % 8.
        # self.__bit_pointer = (self.__bit_pointer + offset) % 8
        self.__bit_pointer = (self.__bit_pointer + offset) & 7

    def __has_to_write_carried(self, byte_padding, bytearray_offset):
        '''Verifica si debe escribirse la sección acarreada de un byte agregado
        a un bytearray, en función al padding del byte y offset del bytearray.

        Ejemplo: suponiendo que se tiene el bytearray 10000000 con bpointer=3 y
        que se le debe agregar el octeto 11100000 con padding 4, el carried
        (parte del padding) NO debería ser agregado al bytearray. En cambio, si
        se necesita agregar el byte 00000000 con padding 0, el carried si se
        debería agregar. Nota: en ambos casos, el carried es 0, por lo que no
        sería correcto agregarlo sólo en caso de que este NO sea 0 (cero).

        Args:
            byte_padding (int): bits de relleno del byte a agregar.
            bytearray_offset (int): pointer (offset) del array a escribir.

        Returns:
            True, si se debe escribir la sección acarrada del byte, False en
            caso contrario.
        '''
        # Como primero se escriben 8 - offset bits, la cantidad restante a es-
        # cribir estará dada por:
        # > to_write = 8 - (8 - offset) - padding
        # Donde: el 8 inicial es el tamaño de un byte y el padding es el relle-
        # no aplicado al último bit. Simplificando lo anterior:
        # > to_write = 8 - 8 + offset - padding
        # Simplificando nuevamente:
        # > to_write = offset - padding
        to_write = bytearray_offset - byte_padding

        return to_write > 0

    def append(self, element, padding=0):
        '''Agrega un byte al array.

        Args:
            element (byte): byte a agregar.
            padding (int): padding (int): bits de relleno del byte a agregar.

        Returns:
            padding (int): nuevo relleno (en bits) del último byte del array.
        '''

        bbutils.validate_padding(padding)

        # Obtención de offset (bit pointer).
        offset = self.__bit_pointer

        # 1. Si bitpointer (offset) es 0 (cero): add de nuevo byte.
        if offset == 0:
            # Creación de nuevo byte.
            self.__stream += bbutils.to_byte(element)
            # self.__byte_pointer += 1
            self.__recompute_bit_pointer(padding)
            return

        # 2. Si offset no es 0 (cero): add a byte actual.
        # Bits a agregar a último byte (right offset s/bitpointer).
        to_last_byte = element >> offset

        # Add a last byte.
        self.__stream[-1] += to_last_byte

        # Corrimiento a la izquierda 1 byte - offset (para obtener bits no
        # incluidos en la operación anterior).
        carried = bbutils.to_left(element, 8 - offset)

        # Si se debe escribir el carried...
        if self.__has_to_write_carried(padding, offset):
            # Add de carried al stream.
            self.__stream += bbutils.to_byte(carried)

        # Cálculo de nuevo bit pointer en base a padding.
        self.__recompute_bit_pointer(padding)

        return self.padding()

    def extend(self, elements, padding=0):
        '''Extiende el array con la lista de elementos especificados.

        Args:
            elements (byte list): elementos a agregar.
            padding (int): bits de relleno del último byte de la lista.

        Returns:
            padding (int): nuevo relleno (en bits) del último byte del array.
        '''
        # Validación de padding.
        bbutils.validate_padding(padding)

        # Add de elementos.
        for i in range(0, len(elements)):
            last_byte = i == len(elements)-1

            # El padding pasado por parámetro sólo se tiene en cuenta para el
            # último byte, en cualquier otro se considera 0 (cero).
            padding_to_append = padding if last_byte else 0

            # Append
            self.append(elements[i], padding_to_append)

        return self.padding()

    def to_left(self, places):
        '''Realiza un corrimiento a la izquierda del array, según la cantidad
        de lugares especificada. Nota: los bits desplazados son eliminados.

        Args:
            places (int): lugares (bits) a mover.

        Returns:
            padding (int): nuevo relleno (en bits) del último byte del array.
        '''
        # Cálculo de nuevo start de stream. Ej: si se requiere realizar un
        # shift de 17 lugares, en realidad se deben eliminar los dos primeros
        # bytes iniciales, y realizar un left shift de 1 bit.
        new_start_index = places >> 3  # int(places/8)
        self.__stream = self.__stream[new_start_index:]

        # Cálculo de shift.
        to_move = places & 7  # places % 8
        to_move = 0

        # Si no se deben realizar corrimientos...
        if to_move == 0:
            return

        for i in range(0, len(self.__stream)):
            # Byte evaluado.
            byte = self.__stream[i]

            # Byte evaluado corrido a la izquierda.
            shifted = bbutils.to_left(byte, to_move)

            # Reemplazo de byte evaluado.
            self.__stream[i] = shifted

            # Si el byte evaluado es el primero, se continua con el siguiente.
            if i == 0:
                continue

            # Right shift de 1 byte - to_move (para obtener bits no incluidos
            # en la sentencia anterior).
            carried = bbutils.to_right(byte, 8-to_move)

            # Add de carried.
            self.__stream[i-1] += carried

        # Si en el fin de la iteración, el padding + el desplazamiento es mayor
        # a 8 (como se ha realizado un left shift, se supone que hay menos bits
        # en el array)...
        if self.padding() + to_move >= 8:
            # Se elimina el último elemento del array (no contiene datos).
            self.__stream.pop()

        # Recómputo de bit pointer como la diferencia de 8 menos el padding
        # del último byte.
        new_padding = (self.padding() + to_move) & 7  # % 8
        self.__bit_pointer = 8 - new_padding

        return self.padding()
