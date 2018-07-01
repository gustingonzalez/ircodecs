# ircodecs: compresión de enteros aplicada a IR (para Python)
**ircodecs** es un repositorio que permite la compresión de listas de enteros. Es compatible con las versiones 2 y 3 de **Python**, siendo útil para prototipos o pruebas, o para quien ya posea conocimientos en este lenguaje y desee incursionar en el área de compresión contextualizada en el ámbito de la _Recuperación de Información_ (_Information Retrieval_). 

# Motivación
Este repositorio surgió a partir de la realización de un trabajo titulado _Esquema Multicompresión para Índices Invertidos de Motores de Búsqueda_ (https://github.com/gustingonzalez/irmulticompression) en el contexto de la materia _Recuperación de Información_, de la carrera Licenciatura en Sistemas de Información, dictada en la **Universidad Nacional de Luján**.

# Descripción
Los distintos módulos aquí implementados permiten la codificación y decodificación de listas de enteros con una serie de métodos _estado del arte_, en concreto: **Unario**, **Gamma**, **Variable Byte**, **Empaquetado Binario**, **Elias Fano** (ver notas en el siguiente subapartado), **Simple16** y **PFor** (NewPFD/OptPFD). También contiene un módulo que permite realizar **Delta Gaps** ([gapsencoder.py](/gapsencoder.py)) y otro que permite tratar secuencias de bytes como arrays de bits de bytes ([bitbytearray](/bitbytearray)). A su vez, estas implementaciones se basan en la bibliografía expuesta en la sección de _Referencias_ y en desarrollos ya conocidos para lograr cierto grado de eficiencia (teniendo en cuenta las limitaciones que un lenguaje interpretado supone). Por ejemplo, los desarrollos de Simple16 y PFor, están fuertemente basados en la implementación _kamikaze_ expuesta en el repositorio de [@lemire](https://github.com/lemire/) (basada, a su vez, en el repositorio de [@javasoze](https://github.com/javasoze/)) mientras que, tanto la decodificación de Unario, como de Elias Fano, se fundamentan en la implementación de [@catenamatteo](https://github.com/catenamatteo/). 

## Acerca de la implementación de Elias Fano: EF Local
Con el fin de mejorar el ratio de compresión de Elias Fano (nativo), la versión aquí implementada tiene una premisa similar a la variación Multinivel presentada en el paper _Partitioned Elias Fano Indexes_ de Ottaviano y Venturini. Sin embargo, dado que esta versión Multinivel descomprime cada partición (_chunk_) de lista teniendo en cuenta el máximo número de la ![ith-1](http://latex.codecogs.com/gif.latex?ith-1) partición, es incompatible con la propuesta del esquema múltiple de compresión en la que originalmente se gestó este repositorio. En efecto, para suplir lo mencionado, dada una secuencia de chunks ![C](http://latex.codecogs.com/gif.latex?C) pertenecientes a una lista, para cada ![ci∈C](http://latex.codecogs.com/gif.latex?c_{i}\epsilon&C) se definen ![y=ci,1](http://latex.codecogs.com/gif.latex?y=c_{i,1}) como el menor elemento del ![ith](http://latex.codecogs.com/gif.latex?ith) _chunk_, y ![F](http://latex.codecogs.com/gif.latex?F=[z,&space;(c_{i,2}-y-1),$...$,(c_{i,n}-y-1)) con ![z=min(F2, y)-1](http://latex.codecogs.com/gif.latex?z=min(F_{2},y)-1), una secuencia creciente que se comprime utilizando Elias Fano. Si se analiza el algoritmo utilizado para computar ![F](http://latex.codecogs.com/gif.latex?F), el establecer ![z](http://latex.codecogs.com/gif.latex?z) como su primer número permite que su codificación no pierda un posible alineamiento en caso de haber definido un tamaño de _chunk_ múltiplo de 8. En adición, el valor de ![F1](http://latex.codecogs.com/gif.latex?F_{1}) será siempre lo más cercano posible a ![F2](http://latex.codecogs.com/gif.latex?F_{2}), lo cual tiene sentido si se tiene en cuenta que el ratio de compresión de Elias Fano depende únicamente del mayor elemento de la lista. Finalmente, se define ![x=y-z](http://latex.codecogs.com/gif.latex?x=y-z), que se comprime utilizando Variable Byte: a esta codificación se concatena ![F](http://latex.codecogs.com/gif.latex?F). Por otra parte, VByte también se utiliza en caso de que la lista a comprimir sea de tamaño 1 ya que, para definir ![F](http://latex.codecogs.com/gif.latex?F), se requieren como mínimo 2 elementos. En el caso de que ![y=0](http://latex.codecogs.com/gif.latex?y=0), ![F](http://latex.codecogs.com/gif.latex?F) se define como ![F=C](http://latex.codecogs.com/gif.latex?F=C) y ![x](http://latex.codecogs.com/gif.latex?x) como ![x=y](http://latex.codecogs.com/gif.latex?x=y), de otro modo el valor de ![z](http://latex.codecogs.com/gif.latex?z) resultaría negativo. Para salvar ineficiencias en la compresión, cuando la secuencia ![F](http://latex.codecogs.com/gif.latex?F) es densa, esta se comprime utilizando vectores de bits siempre que ![|F|>u/4](http://latex.codecogs.com/gif.latex?|F|>u/4) con ![u=max(F)](http://latex.codecogs.com/gif.latex?u=max(F)). Para rearmar la lista original, luego de la descompresión de ![x](http://latex.codecogs.com/gif.latex?x) y de ![F](http://latex.codecogs.com/gif.latex?F), simplemente se redefine ![F1=x+F1](http://latex.codecogs.com/gif.latex?F_{1}=x+F_{1})  y se adiciona este valor a cada ![f∈F:f>F1](http://latex.codecogs.com/gif.latex?f\epsilon&F:f>F_{1}). La ventaja de la variante propuesta, es que cada partición de lista es independiente de las demás.

## ¿Python v2 o Python v3?
Si bien esta librería es compatible con las versiones 2 y 3 de Python, la primera brinda mejores resultados en términos de eficiencia. Esto se debe a la forma en que se implementa el tipo _entero_ en cada versión del lenguaje. En concreto, mientras que la versión 2 diferencia entre un tipo _entero_ de 64 bits y un _long_ (de tamaño arbitrario), la versión 3 presupone toda variable numérica como _long_ (arbitraria): en efecto las operaciones a nivel bit sobre este último tipo de variables, son más costosas que sobre las primeras. Referencias a este hecho, se pueden encontrar en https://docs.python.org/2/c-api/long.html y https://docs.python.org/3/c-api/long.html.

El siguiente cuadro expone una comparativa de los tiempos de decodificación, especificados en _enteros por segundo_, en relación a cada versión del lenguaje:

Códec             | Py2 (2.7.9) |   Py3 (3.4.2) |  Δ%     |
:---------------- | :---------: | :-----------: | :-----: |
PFD (NewPFD)      | 1367019,0   | 1167724,5     | -14,6%  |
Bit Packing       | 1019746,3   | 867998,7      | -14,9%  |
EF Local          | 617343,7    | 561147,9      | -9,1%   |
Gamma             | 354815,1    | 318848,3      | -10,1%  |
Vbyte             | 3050411,3   | 2436618,0     | -20,1%  |
Simple16          | 3044125,2   | 2328077,2     | -23,5%  |
Unario            | 658449,6    | 612273,8      | -7,0%   |

Para las mediciones se ha utilizado el script [decodingspeedtest.py](/decodingspeedtest.py), cuya metodología consiste en comprimir, con cada códec, una secuencia de gaps derivada de una lista creciente de 1 millón de enteros, para finalmente obtener el tiempo de cada decodificación. Tener en cuenta que, dado que Elias Fano comprime la lista original utilizando _dgaps_ internamente, para equiparar, el tiempo de decodificación delta se añade a los resultados de los restantes métodos. Esta operación se lleva a cabo 5 veces, aunque también se realiza una inicial (a modo de _warm-up_), que no se toma en cuenta para el promedio final. Además, por cada repetición, la distancia entre números se duplica. Es decir, en la primera (pertinente a la medición), se prueba la secuencia S=[1, 2, 3], en la segunda S=[1, 3, 5], en la tercera S=[1, 5, 9] y así sucesivamente. El entorno de pruebas utilizado ha sido un Intel® Xeon® X5650 @ 2.67Ghz de 24 núcleos con 32 GB de memoria RAM.

# ¿Cómo usar? ¡Muy simple!
Suponiendo que se requiere codificar una lista de 128 números...

## PFor (NewPFD/OptPFD)
```python
from irencoder import pforencoder

numbers = list(range(1, 129))
encoded = pforencoder.encode(numbers)
decoded = pforencoder.decode(encoded, 128)
```
Tener en cuenta que el resultado de la codificación es una secuencia enteros.

## Simple16
```python
from irencoder import simple16encoder

numbers = list(range(1, 129))
encoded = simple16encoder.encode(numbers)
decoded = simple16encoder.decode(encoded, 128)
```
Tener en cuenta que el resultado de la codificación es una secuencia enteros.

## Empaquetado binario (Bit Packing)
```python
from irencoder import bitpackingencoder

numbers = list(range(1, 129))
encoded, padding = bitpackingencoder.encode(numbers)
decoded = bitpackingencoder.decode(encoded, 128)
```
Tener en cuenta que el resultado de la codificación es una secuencia bytes.

## Elias Fano (Local)
```python
from irencoder import eliasfanoencoder

numbers = list(range(1, 129))
encoded, padding = eliasfanoencoder.encode(numbers)
decoded = eliasfanoencoder.decode(encoded, 128)
```
Tener en cuenta que el resultado de la codificación es una secuencia bytes.

## Unario
*Nota preliminar*: aunque la implementación ha sido diseñada para comprimir un único número por vez, la codificación de una lista tan sólo requiere la importación de la clase _BitByteArray_ del módulo [bitbytearray](/bitbytearray). Esta funcionalidad no ha sido desarrollada debido a que, en la propuesta del esquema de compresión múltiple en la que se gestó esta librería, esta tarea se lleva a cabo en una capa superior. De todas formas, sería útil su implementación. Tener en cuenta que, alternativamente, se podría utilizar la función _write_binary_in_barray(array, offset, number, bits)_ de bitutils.py: aun así, la clase _BitByteArray_ abstrae la complejidad inherente a las escrituras de secuencias de bits como, por ejemplo, el control de _offset_ (puntero de bit relativo al array de bytes). Por su parte, el uso de _write_binary_in_barray(array, offset, number, bits)_, se recomienda en los casos en los que se utilicen cantidades fijas de bits o en los que se requiera mayor eficiencia en la codificación: por ejemplo, el módulo [bitpackingencoder.py](/bitpackingencoder.py) utiliza esta función de forma interna tanto para el proceso de codificación, como para el de decodificación.

```python
from irencoder import unaryencoder
from irencoder.bitbytearray import BitByteArray

numbers = list(range(1, 129))
optimized = True  # Unario optimizado

# Encode
encoded = BitByteArray()
for number in numbers:
    e, padding = unaryencoder.encode(number)
    encoded.extend(e, padding)

# Decode
decoded = unaryencoder.decode(encoded, 128, optimized)
```

También es posible especificar el inicio de la lectura, desde un bit arbitrario. Por ejemplo, en la siguiente sentencia, se leen los 127 números restantes desde el _offset_ 1:
```python
decoded = unaryencoder.decode(encoded, 127, True, offset=1)
```
Tener en cuenta que no es estrictamente necesario que la función *decode* reciba un _BitByteArray_: bien pudiera recibir un array de bytes (_bytearray_) o de enteros.

## Gamma
_Nota preliminar_: para este códec aplican las mismas observaciones señaladas para Unario.
```python
from irencoder import gammaencoder
from irencoder.bitbytearray import BitByteArray

numbers = list(range(1, 129))

# Encode
encoded = BitByteArray()
for number in numbers:
    e, padding = gammaencoder.encode(number)
    encoded.extend(e, padding)

# Decode
decoded = gammaencoder.decode(encoded, 128)
```

Tener en cuenta que el resultado de la codificación es una secuencia bytes.

## Variable Byte
_Nota preliminar_: para la decodificación con este método no se requiere el parámetro de la cantidad de números a descomprimir, puesto que se lee la totalidad de los bytes pasados por parámetro. Quizás, a modo de aunar criterios, sería útil la futura implementación de lo descrito.
```python
from irencoder import vbencoder

numbers = list(range(1, 129))

# Encode
encoded = bytearray()
for n in numbers:
    encoded.extend(vbencoder.encode(n))

# Decode
decoded = vbencoder.decode(encoded)
```

También es posible realizar la lectura de un único número desde un bit especifico. Por ejemplo, en la siguiente sentencia, el valor de _number_, leído desde el bit 8, es 2 y el nuevo _offset_, 16:
```python
number, offset = vbencoder.decode_number(encoded, 8)
```
_Nota_: como Variable Byte realiza la lectura en grupos de octetos, si el _offset_ no es múltiplo de 8, esta se inicia desde el byte relativo.


## Sólo necesito un único códec ¿qué debo tener en cuenta?
En caso de requerir utilizar algún módulo en concreto y de que querer evitar la descarga completa del repositorio, hay que tener en las dependencias internas de cada uno:
- [bitpackingencoder.py](/bitpackingencoder.py): [vbencoder.py](/vbencoder.py), [bitutils.py](/bitutils.py).
- [eliasfanoencoder.py](/eliasfanoencoder.py): [bitutils.py](/bitutils.py), [gapsencoder.py](/gapsencoder.py), [unaryencoder.py](/unaryencoder.py), [vbencoder.py](/vbencoder.py), [/bitbytearray](/bitbytearray).
- [gammaencoder.py](/gammaencoder.py): [bitutils.py](/bitutils.py), [unaryencoder.py](/unaryencoder.py), [bitbytearray](/bitbytearray).
- [gapsencoder.py](/gapsencoder.py): sin dependencias.
- [pforencoder.py](/pforencoder.py): [simple16encoder.py](/simple16encoder.py), [bitutils.py](/bitutils.py).
- [simple16encoder.py](/simple16encoder.py): sin dependencias.
- [vbencoder.py](/vbencoder.py): sin dependencias.

# Referencias
Este repositorio está basado en diversas lecturas:
- C. D. Manning, P. Raghavan, H. Schütze. Introduction to Information Retrieval. Cambridge University Press, 2008.
- M. Catena, C. MacDonald, and I. Ounis. On inverted index compression for search engine efficiency. Lect. Notes Comput. Sci. (including Subser. Lect. Notes Artif. Intell. Lect. Notes Bioinformatics), vol. 8416 LNCS, pp. 359–371, 2014.
- J. Zhang, X. Long, y T. Suel. Performance of Compressed Inverted List Caching in Search Engine. Proceedings of the 17th international conference on World Wide Web, WWW '08, pp. 387–396, 2008.
- D. Lemire, L. Boytsov. Decoding billions of integers per second through vectorization. Software: Practice & Experience, Vol. 45 (1), pp. 1-29, 2015.
- M. Zukowski, S. Heman, N. Nes y P. Boncz. Super-Scalar RAM-CPU Cache Compression. 22nd International Conference on Data Engineering (ICDE'06), pp. 59-59, 2006.
- G. Ottaviano, R. Venturini. Partitioned Elias-Fano Indexes. Proceedings of the 37th International ACM SIGIR Conference on Research & Development in Information Retrieval, SIGIR ‘14, pp. 273-282, 2014.

También se han utilizado (y se recomiendan) las siguientes implementaciones como referencia:
- DocId set compression and set operation library - https://github.com/javasoze/kamikaze
- JavaFastPFOR: A java integer compression library - https://github.com/lemire/JavaFastPFOR
- Elias Fano: A simpl(istic) Java implementation of the Elias-Fano compression schema - https://github.com/catenamatteo/eliasfano
- Partitioned Elias-Fano Indexes - https://github.com/ot/partitioned_elias_fano
- Data Structures for Inverted Indexes (ds2i) -  https://github.com/ot/ds2i
- Terrier IR Platform - http://terrier.org

# Requerimientos
Python v2 o Python v3

# Autor
Agustín González
