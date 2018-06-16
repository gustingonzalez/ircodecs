#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
- Nombre: __init__.py (irencoder)
- Descripción: contiene el enum 'EncodeTypes' (ver docstring).
- Autor: Agustín González
- Modificado: 29/05/18
'''

from enum import Enum


class EncodeTypes(Enum):
    '''Tipos de códecs (métodos de compresión).'''
    ByteBlocks = 1
    VariableByte = 2
    Unary = 3
    Gamma = 4
    EliasFano = 5
    BitPacking = 6
    Simple16 = 7
    PForDelta = 8
