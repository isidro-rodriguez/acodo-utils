# API de irg_utils

Referencia de uso del paquete. Se genera a partir de los docstrings con
`scripts/gen_api.py`: no editar a mano.

```python
from irg_utils import to_bool, valid_email
```

## Convenciones

- `to_*`: nunca lanzan excepciones por valores inválidos; devuelven `None`.
- `has_*` y `valid_*`: devuelven `bool`.
- `parse_*`: devuelven `str`, salvo `parse_duration`, que devuelve `timedelta | None`.
- `get_*`: producen valores del entorno (variables de entorno, hashes,
  credenciales aleatorias seguras); no transforman ni verifican.
- `ValueError` solo se lanza ante argumentos de configuración incorrectos
  (código de lenguaje, rango de longitud...), nunca por el dato evaluado.
- Dentro de cada categoría, las funciones están en orden alfabético.

## Índice

**Conversores**

- [`to_bool`](#to_bool): Convierte textos habituales (`"sí"`, `"off"`, `"1"`...) a bool.
- [`to_bytes`](#to_bytes): Convierte un texto de tamaño (`"1,5 GiB"`) a bytes.
- [`to_date`](#to_date): Convierte un string con fechas habituales a date.
- [`to_datetime`](#to_datetime): Convierte un string con fechas habituales a datetime.
- [`to_decimal`](#to_decimal): Convierte strings numéricos a Decimal (apto para importes).
- [`to_dict`](#to_dict): Convierte un valor a dict, convirtiendo también los anidados.
- [`to_float`](#to_float): Convierte strings numéricos a float.
- [`to_int`](#to_int): Convierte strings numéricos a int.
- [`to_list`](#to_list): Convierte un valor a lista, aplanando las anidadas.
- [`to_path`](#to_path): Convierte un texto o ruta a Path, expandiendo `~`.
- [`to_port`](#to_port): Convierte un texto o entero a número de puerto TCP/UDP (1-65535).
- [`to_str`](#to_str): Devuelve el valor si es un texto con contenido.
- [`to_timedelta`](#to_timedelta): Convierte una cantidad numérica de segundos a timedelta.

**Comprobaciones**

- [`has_required_attrs`](#has_required_attrs): Comprueba que el objeto tiene todos los atributos requeridos.
- [`has_required_fields`](#has_required_fields): Comprueba que la colección tiene todos los campos requeridos.
- [`has_required_keys`](#has_required_keys): Comprueba que el diccionario tiene todas las llaves requeridas.

**Parsers**

- [`parse_amount`](#parse_amount): Parsea un tipo numérico a string numérico de legibilidad cómoda.
- [`parse_bool`](#parse_bool): Parsea un booleano a string legible (`"Sí"`/`"No"`).
- [`parse_datetime`](#parse_datetime): Parsea una fecha o fecha-hora a string legible.
- [`parse_duration`](#parse_duration): Parsea un texto de duración (`"1h 30m"`) a timedelta.
- [`parse_percent`](#parse_percent): Parsea un número o fracción (`0.256`, `Fraction(1, 4)`) a porcentaje.
- [`parse_size`](#parse_size): Parsea el tamaño de fichero a su unidad ISO/IEC 80000-13 correspondiente.
- [`parse_slug`](#parse_slug): Parsea un texto a slug: minúsculas, sin acentos y separado por guiones.
- [`parse_timedelta`](#parse_timedelta): Formatea un timedelta a una cadena con formato `H:MM:SS` o `M:SS`.

**Validaciones**

- [`valid_bic`](#valid_bic): Comprueba si el string es un BIC/SWIFT con formato válido (ISO 9362).
- [`valid_bool`](#valid_bool): Comprueba si el string lo aceptaría `to_bool`.
- [`valid_date`](#valid_date): Comprueba si el string lo aceptaría `to_date`.
- [`valid_datetime`](#valid_datetime): Comprueba si el string lo aceptaría `to_datetime`.
- [`valid_dni`](#valid_dni): Comprueba si el string es un DNI español válido (8 dígitos y letra).
- [`valid_domain`](#valid_domain): Comprueba si el string es un nombre de dominio (DNS) bien formado.
- [`valid_duration`](#valid_duration): Comprueba si el string es aceptado por `parse_duration`.
- [`valid_email`](#valid_email): Comprueba si el string presenta un formato de email válido.
- [`valid_filename`](#valid_filename): Comprueba si el string es un nombre de fichero válido en cualquier SO.
- [`valid_hex_color`](#valid_hex_color): Comprueba si el string es un color hexadecimal (`#rgb`, `#rrggbb`...).
- [`valid_iban`](#valid_iban): Comprueba si el string es un IBAN con dígitos de control correctos.
- [`valid_ip`](#valid_ip): Comprueba si el string es una dirección IPv4 o IPv6 válida.
- [`valid_json`](#valid_json): Comprueba si el string es JSON bien formado (RFC 8259).
- [`valid_mac`](#valid_mac): Comprueba si el string es una dirección MAC de 48 bits válida.
- [`valid_nie`](#valid_nie): Comprueba si el string es un NIE español válido (X/Y/Z, 7 dígitos, letra).
- [`valid_passport`](#valid_passport): Comprueba si el string tiene formato de pasaporte genérico.
- [`valid_password`](#valid_password): Comprueba si el string presenta el formato de contraseña requerido.
- [`valid_phone`](#valid_phone): Comprueba si el string es un teléfono en formato internacional básico.
- [`valid_port`](#valid_port): Comprueba si el string lo aceptaría `to_port`.
- [`valid_slug`](#valid_slug): Comprueba si el string es un slug: minúsculas, dígitos y guiones simples.
- [`valid_url`](#valid_url): Comprueba si el string presenta formato de URL http/https.
- [`valid_uuid`](#valid_uuid): Comprueba si el string es un UUID en forma canónica (8-4-4-4-12).

**Getters**

- [`get_env`](#get_env): Lee una variable de entorno y la convierte con un conversor `to_*`.
- [`get_hash`](#get_hash): Calcula el hash hexadecimal de un texto, bytes o fichero.
- [`get_hmac`](#get_hmac): Calcula el HMAC hexadecimal de un mensaje con una clave secreta.
- [`get_now`](#get_now): Devuelve la fecha y hora actual en UTC, con zona horaria.
- [`get_random_password`](#get_random_password): Genera una contraseña aleatoria que cumple los criterios de `valid_password`.
- [`get_random_token`](#get_random_token): Genera un token aleatorio criptográficamente seguro con `secrets`.

## Conversores

Transforman tipos de datos.

### `to_bool`

```python
to_bool(raw: str | int | None) -> bool | None
```

Convierte textos habituales (`"sí"`, `"off"`, `"1"`...) a bool.

**Parámetros**

- `raw`: Valor a convertir. Los enteros solo pueden ser 0 o 1.

**Devuelve:** El booleano, o `None` si el valor no es reconocible.

**Ejemplos**

```pycon
>>> to_bool("Sí")
True
>>> to_bool(" OFF ")
False
>>> to_bool("quizá") is None
True
>>> to_bool(2) is None
True
```

### `to_bytes`

```python
to_bytes(raw: str | None) -> int | None
```

Convierte un texto de tamaño (`"1,5 GiB"`) a bytes.

Unidades binarias (KiB, MiB...) en base 1024 y decimales (kB, MB...) en
base 1000. Admite coma o punto decimal. Sin unidad se asumen bytes. Es el
camino inverso, aproximado, de `parse_size`.

**Parámetros**

- `raw`: Texto a convertir.

**Devuelve:** Cantidad de bytes, o `None` si el texto no es válido.

**Ejemplos**

```pycon
>>> to_bytes("1,5 GiB")
1610612736
>>> to_bytes("2 kB")
2000
>>> to_bytes("512")
512
>>> to_bytes("1 furlong") is None
True
```

### `to_date`

```python
to_date(raw: str) -> date | None
```

Convierte un string con fechas habituales a date.

Acepta los mismos formatos que `to_datetime`.

**Parámetros**

- `raw`: String a ser parseado como fecha.

**Devuelve:** La fecha, o `None` si la conversión falla.

**Ejemplos**

```pycon
>>> to_date("31/01/2024")
datetime.date(2024, 1, 31)
```

### `to_datetime`

```python
to_datetime(raw: str) -> datetime | None
```

Convierte un string con fechas habituales a datetime.

Solo se conserva la fecha: el resultado es siempre medianoche y sin zona
horaria. En los formatos con día y mes numéricos se asume día primero.

**Parámetros**

- `raw`: String a ser parseado como fecha.

**Devuelve:** El datetime a medianoche, o `None` si la conversión falla.

**Ejemplos**

```pycon
>>> to_datetime("2024-01-31")
datetime.datetime(2024, 1, 31, 0, 0)
>>> to_datetime("31/01/2024")
datetime.datetime(2024, 1, 31, 0, 0)
>>> to_datetime("1700000000")
datetime.datetime(2023, 11, 14, 0, 0)
>>> to_datetime("basura") is None
True
```

### `to_decimal`

```python
to_decimal(raw: str | float | None) -> Decimal | None
```

Convierte strings numéricos a Decimal (apto para importes).

Los `float` se convierten a través de su representación en texto
(`0.1` -> `Decimal("0.1")`). Se rechazan `bool`, `nan`, `inf` y los
guiones bajos (`"1_000"`).

**Parámetros**

- `raw`: Valor a convertir (texto numérico, entero o flotante).

**Devuelve:** El número convertido, o `None` si la conversión falla.

**Ejemplos**

```pycon
>>> to_decimal("0.10")
Decimal('0.10')
>>> to_decimal(0.1)
Decimal('0.1')
>>> to_decimal("nan") is None
True
```

### `to_dict`

```python
to_dict(raw: object) -> dict[Any, Any]
```

Convierte un valor a dict, convirtiendo también los anidados.

`None` produce `{}`. Se aceptan mappings, dataclasses y pares
`("k", v)`; los valores anidados que sean mappings o dataclasses se
convierten recursivamente. Cualquier otro valor produce `{}`.

**Parámetros**

- `raw`: Valor a convertir.

**Devuelve:** El dict resultante; `{}` si el valor no es convertible.

**Ejemplos**

```pycon
>>> to_dict({"a": 1})
{'a': 1}
>>> to_dict([("a", 1), ("b", 2)])
{'a': 1, 'b': 2}
>>> to_dict(None)
{}
```

### `to_float`

```python
to_float(raw: str | float | None) -> float | None
```

Convierte strings numéricos a float.

Se rechazan `bool`, `nan`, `inf` y los guiones bajos (`"1_000"`).

**Parámetros**

- `raw`: Valor a convertir (texto numérico o flotante).

**Devuelve:** El número convertido, o `None` si la conversión falla.

**Ejemplos**

```pycon
>>> to_float("1.5")
1.5
>>> to_float("nan") is None
True
```

### `to_int`

```python
to_int(raw: str | float | int | None) -> int | None
```

Convierte strings numéricos a int.

Un `float` solo se convierte si es entero exacto (`3.0` sí, `3.7` no).
Se rechazan `bool` y los guiones bajos (`"1_000"`).

**Parámetros**

- `raw`: Valor a convertir (texto numérico o entero).

**Devuelve:** El número convertido, o `None` si la conversión falla.

**Ejemplos**

```pycon
>>> to_int("42")
42
>>> to_int(3.7) is None
True
>>> to_int(float("inf")) is None
True
```

### `to_list`

```python
to_list(raw: object) -> list[Any]
```

Convierte un valor a lista, aplanando las anidadas.

`None` produce `[]`; un escalar (o un `str`/`bytes`) produce una lista
de un elemento; un iterable se aplanan recursivamente.

**Parámetros**

- `raw`: Valor a convertir.

**Devuelve:** La lista aplanada.

**Ejemplos**

```pycon
>>> to_list([1, [2, 3]])
[1, 2, 3]
>>> to_list("abc")
['abc']
>>> to_list(None)
[]
```

### `to_path`

```python
to_path(raw: str | PathLike[str] | None) -> Path | None
```

Convierte un texto o ruta a Path, expandiendo `~`.

**Parámetros**

- `raw`: Texto o ruta a convertir.

**Devuelve:** La ruta, o `None` si el valor falta, está en blanco o no es válido.

**Ejemplos**

```pycon
>>> to_path("carpeta/fichero.txt").name
'fichero.txt'
>>> to_path("   ") is None
True
```

### `to_port`

```python
to_port(raw: str | int | None) -> int | None
```

Convierte un texto o entero a número de puerto TCP/UDP (1-65535).

**Parámetros**

- `raw`: Valor a convertir (texto numérico o entero).

**Devuelve:** El puerto, o `None` si el valor falta o está fuera del rango 1-65535.

**Ejemplos**

```pycon
>>> to_port("8080")
8080
>>> to_port(80)
80
>>> to_port("0") is None
True
>>> to_port(70000) is None
True
```

### `to_str`

```python
to_str(raw: object) -> str | None
```

Devuelve el valor si es un texto con contenido.

**Parámetros**

- `raw`: Valor a comprobar.

**Devuelve:** El propio `raw` si es un `str` que no está vacío ni es solo espacios; `None` en otro caso.

### `to_timedelta`

```python
to_timedelta(raw: float | None) -> timedelta | None
```

Convierte una cantidad numérica de segundos a timedelta.

**Parámetros**

- `raw`: Cantidad de segundos a convertir.

**Devuelve:** La duración, o `None` si el valor falta, no es finito o es desmesurado.

**Ejemplos**

```pycon
>>> to_timedelta(90)
datetime.timedelta(seconds=90)
```

## Comprobaciones

Verifican que los objetos cumplan los requisitos.

### `has_required_attrs`

```python
has_required_attrs(raw: object, required_attrs: Iterable[str]) -> bool
```

Comprueba que el objeto tiene todos los atributos requeridos.

**Parámetros**

- `raw`: Objeto a verificar.
- `required_attrs`: Nombres de los atributos requeridos.

**Devuelve:** `True` si el objeto tiene todos los atributos requeridos.

**Ejemplos**

```pycon
>>> has_required_attrs("texto", ["upper", "lower"])
True
>>> has_required_attrs("texto", ["append"])
False
```

### `has_required_fields`

```python
has_required_fields(
    raw: Collection[Any],
    required_fields: Iterable[Any],
) -> bool
```

Comprueba que la colección tiene todos los campos requeridos.

**Parámetros**

- `raw`: Colección a verificar.
- `required_fields`: Campos requeridos.

**Devuelve:** `True` si la colección tiene todos los campos requeridos.

### `has_required_keys`

```python
has_required_keys(
    raw: Mapping[Hashable, Any],
    required_keys: Iterable[Hashable],
) -> bool
```

Comprueba que el diccionario tiene todas las llaves requeridas.

**Parámetros**

- `raw`: Diccionario a verificar.
- `required_keys`: Llaves requeridas.

**Devuelve:** `True` si el diccionario tiene todas las llaves requeridas.

## Parsers

Transforman tipos de datos a strings legibles.

### `parse_amount`

```python
parse_amount(
    raw: int | float | Fraction,
    lang: str | None = None,
    decimals: int = 2,
) -> str
```

Parsea un tipo numérico a string numérico de legibilidad cómoda.

Los enteros (y las fracciones de denominador 1) se muestran sin decimales.
Con `lang` `en`/`eng` se usa `1,234.50`; en cualquier otro caso
(incluido `None`), `1.234,50`.

**Parámetros**

- `raw`: Número a parsear.
- `lang`: Código del lenguaje al que se va a formatear el número.
- `decimals`: Cantidad de dígitos decimales a mostrar.

**Devuelve:** String numérico de legibilidad cómoda.

**Lanza**

- `ValueError`: Si se ha indicado código de lenguaje inválido.

**Ejemplos**

```pycon
>>> parse_amount(1234.5)
'1.234,50'
>>> parse_amount(1234.5, "en")
'1,234.50'
>>> parse_amount(1234)
'1.234'
```

### `parse_bool`

```python
parse_bool(raw: bool, lang: str | None = None) -> str
```

Parsea un booleano a string legible (`"Sí"`/`"No"`).

Es el camino inverso a `to_bool`. Con `lang` `en`/`eng` se usa
`"Yes"`/`"No"`; en cualquier otro caso (incluido `None`), `"Sí"`/`"No"`.

**Parámetros**

- `raw`: Booleano a parsear.
- `lang`: Código del lenguaje al que se va a formatear el booleano.

**Devuelve:** String legible del booleano.

**Lanza**

- `ValueError`: Si se ha indicado código de lenguaje inválido.

**Ejemplos**

```pycon
>>> parse_bool(True)
'Sí'
>>> parse_bool(False)
'No'
>>> parse_bool(True, "en")
'Yes'
```

### `parse_datetime`

```python
parse_datetime(raw: date | datetime, lang: str | None = None) -> str
```

Parsea una fecha o fecha-hora a string legible.

La hora solo se muestra si no es medianoche, y los segundos solo si no
son cero. La zona horaria se ignora. Con `lang` `en`/`eng` se usa
`2024-01-31`; en cualquier otro caso (incluido `None`), `31/01/2024`.

**Parámetros**

- `raw`: Fecha o fecha-hora a parsear.
- `lang`: Código del lenguaje al que se va a formatear la fecha.

**Devuelve:** String de fecha de legibilidad cómoda.

**Lanza**

- `ValueError`: Si se ha indicado código de lenguaje inválido.

**Ejemplos**

```pycon
>>> parse_datetime(datetime(2024, 1, 31))
'31/01/2024'
>>> parse_datetime(datetime(2024, 1, 31, 10, 30))
'31/01/2024 10:30'
>>> parse_datetime(datetime(2024, 1, 31, 10, 30), "en")
'2024-01-31 10:30'
```

### `parse_duration`

```python
parse_duration(raw: str) -> timedelta | None
```

Parsea un texto de duración (`"1h 30m"`) a timedelta.

Es el camino inverso a `parse_timedelta`, y la única función de esta
sección que devuelve un valor en lugar de un texto. Unidades admitidas:
`d`, `h`, `min`/`m` y `s`; admite decimales (`"1,5h"`).

**Parámetros**

- `raw`: Texto a parsear.

**Devuelve:** La duración, o `None` si el texto no es válido.

**Ejemplos**

```pycon
>>> parse_duration("1h 30m")
datetime.timedelta(seconds=5400)
>>> parse_duration("2d")
datetime.timedelta(days=2)
>>> parse_duration("1h30x") is None
True
```

### `parse_percent`

```python
parse_percent(
    raw: int | float | Fraction,
    lang: str | None = None,
    decimals: int = 1,
) -> str
```

Parsea un número o fracción (`0.256`, `Fraction(1, 4)`) a porcentaje.

Se eliminan los ceros decimales sobrantes. Con `lang` `en`/`eng` se usa
`25.6%`; en cualquier otro caso (incluido `None`), `25,6 %`.

**Parámetros**

- `raw`: Proporción a parsear (`1` equivale a 100 %).
- `lang`: Código del lenguaje al que se va a formatear el número.
- `decimals`: Máximo de dígitos decimales a mostrar.

**Devuelve:** String de porcentaje de legibilidad cómoda.

**Lanza**

- `ValueError`: Si se ha indicado código de lenguaje inválido.

**Ejemplos**

```pycon
>>> from fractions import Fraction
>>> parse_percent(0.256)
'25,6 %'
>>> parse_percent(Fraction(1, 4))
'25 %'
>>> parse_percent(0.5, "en")
'50%'
>>> parse_percent(1 / 3, decimals=2)
'33,33 %'
```

### `parse_size`

```python
parse_size(raw: int) -> str
```

Parsea el tamaño de fichero a su unidad ISO/IEC 80000-13 correspondiente.

**Parámetros**

- `raw`: Tamaño de fichero, en bytes, a parsear.

**Devuelve:** String de tamaño de fichero con legibilidad cómoda.

**Ejemplos**

```pycon
>>> parse_size(1)
'1 byte'
>>> parse_size(1536)
'1,500 KiB'
>>> parse_size(1048575)
'1023,999 KiB'
```

### `parse_slug`

```python
parse_slug(raw: str) -> str
```

Parsea un texto a slug: minúsculas, sin acentos y separado por guiones.

Los caracteres sin equivalente ASCII (`ß`, `€`, emojis...) se descartan.

**Parámetros**

- `raw`: Texto a parsear.

**Devuelve:** El slug; cadena vacía si no queda ningún carácter válido.

**Ejemplos**

```pycon
>>> parse_slug("¡Hola, Mundo! Ñandú")
'hola-mundo-nandu'
```

### `parse_timedelta`

```python
parse_timedelta(duration: timedelta) -> str
```

Formatea un timedelta a una cadena con formato `H:MM:SS` o `M:SS`.

**Parámetros**

- `duration`: Duración a formatear.

**Devuelve:** Texto en formato `H:MM:SS` o `M:SS` (con `-` delante si es negativa).

**Ejemplos**

```pycon
>>> parse_timedelta(timedelta(seconds=3725))
'1:02:05'
>>> parse_timedelta(timedelta(seconds=65))
'1:05'
>>> parse_timedelta(timedelta(seconds=-65))
'-1:05'
```

## Validaciones

Verifican que un string tenga el formato requerido.

### `valid_bic`

```python
valid_bic(raw: str) -> bool
```

Comprueba si el string es un BIC/SWIFT con formato válido (ISO 9362).

Acepta 8 (BIC8) u 11 (BIC11) caracteres: seis letras del banco, dos del
código de país y dos o cinco alfanuméricos. No valida que el país esté
asignado realmente ni el dígito de control.

**Parámetros**

- `raw`: String a validar.

**Devuelve:** `True` si el BIC presenta un formato válido.

**Ejemplos**

```pycon
>>> valid_bic("ESPCESMMXXX")
True
>>> valid_bic("ESPCESMM")
True
>>> valid_bic("ESPCESMMX")
False
```

### `valid_bool`

```python
valid_bool(raw: str) -> bool
```

Comprueba si el string lo aceptaría `to_bool`.

**Parámetros**

- `raw`: String a validar.

**Devuelve:** `True` si el string representa un booleano reconocible.

**Ejemplos**

```pycon
>>> valid_bool("Sí")
True
>>> valid_bool("off")
True
>>> valid_bool("basura")
False
```

### `valid_date`

```python
valid_date(raw: str) -> bool
```

Comprueba si el string lo aceptaría `to_date`.

**Parámetros**

- `raw`: String a validar.

**Devuelve:** `True` si el string representa una fecha habitual.

**Ejemplos**

```pycon
>>> valid_date("31/01/2024")
True
>>> valid_date("basura")
False
```

### `valid_datetime`

```python
valid_datetime(raw: str) -> bool
```

Comprueba si el string lo aceptaría `to_datetime`.

**Parámetros**

- `raw`: String a validar.

**Devuelve:** `True` si el string representa una fecha habitual.

**Ejemplos**

```pycon
>>> valid_datetime("2024-01-31")
True
>>> valid_datetime("basura")
False
```

### `valid_dni`

```python
valid_dni(raw: str) -> bool
```

Comprueba si el string es un DNI español válido (8 dígitos y letra).

**Parámetros**

- `raw`: String a validar.

**Devuelve:** `True` si el formato y la letra de control son correctos.

**Ejemplos**

```pycon
>>> valid_dni("12345678Z")
True
>>> valid_dni("12345678A")
False
```

### `valid_domain`

```python
valid_domain(raw: str) -> bool
```

Comprueba si el string es un nombre de dominio (DNS) bien formado.

Exige al menos dos etiquetas separadas por puntos, cada una de 1-63
caracteres que empiece y termine en alfanumérico (guiones solo en el
interior), un TLD final solo de letras de longitud ≥ 2 y una longitud
total ≤ 253. No se admiten espacios ni puntos finales; no valida IDN.

**Parámetros**

- `raw`: String a validar.

**Devuelve:** `True` si el string es un dominio válido.

**Ejemplos**

```pycon
>>> valid_domain("example.com")
True
>>> valid_domain("sub.dominio.example.com")
True
>>> valid_domain("example")
False
>>> valid_domain("example.123")
False
>>> valid_domain("-example.com")
False
```

### `valid_duration`

```python
valid_duration(raw: str) -> bool
```

Comprueba si el string es aceptado por `parse_duration`.

**Parámetros**

- `raw`: String a validar.

**Devuelve:** `True` si el string representa una duración (`"1h 30m"`, `"2d"`...).

**Ejemplos**

```pycon
>>> valid_duration("1h 30m")
True
>>> valid_duration("abc")
False
```

### `valid_email`

```python
valid_email(raw: str) -> bool
```

Comprueba si el string presenta un formato de email válido.

**Parámetros**

- `raw`: String a validar.

**Devuelve:** `True` si el string presenta formato de email válido.

**Ejemplos**

```pycon
>>> valid_email("a@b.com")
True
>>> valid_email("hola")
False
```

### `valid_filename`

```python
valid_filename(raw: str) -> bool
```

Comprueba si el string es un nombre de fichero válido en cualquier SO.

Rechaza nombres vacíos o de más de 255 caracteres, caracteres
`<>:"/\|?*` y de control, nombres que terminan en punto o espacio, y los
nombres reservados de Windows (`CON`, `NUL`, `COM1`...) con cualquier
extensión.

**Parámetros**

- `raw`: Nombre de fichero (sin ruta) a validar.

**Devuelve:** `True` si el nombre es válido.

**Ejemplos**

```pycon
>>> valid_filename("informe.pdf")
True
>>> valid_filename("a/b.txt")
False
>>> valid_filename("CON.txt")
False
>>> valid_filename("archivo.")
False
```

### `valid_hex_color`

```python
valid_hex_color(raw: str, allow_alpha: bool = True) -> bool
```

Comprueba si el string es un color hexadecimal (`#rgb`, `#rrggbb`...).

**Parámetros**

- `raw`: String a validar.
- `allow_alpha`: Si se admiten las formas con canal alfa (`#rgba`, `#rrggbbaa`).

**Devuelve:** `True` si el string es un color hexadecimal válido.

**Ejemplos**

```pycon
>>> valid_hex_color("#fff")
True
>>> valid_hex_color("#ff00cc80")
True
>>> valid_hex_color("#ff00cc80", allow_alpha=False)
False
>>> valid_hex_color("fff")
False
```

### `valid_iban`

```python
valid_iban(raw: str) -> bool
```

Comprueba si el string es un IBAN con dígitos de control correctos.

Admite espacios y minúsculas. Valida el formato general y el módulo 97,
pero no la longitud específica de cada país.

**Parámetros**

- `raw`: String a validar.

**Devuelve:** `True` si el IBAN es válido.

**Ejemplos**

```pycon
>>> valid_iban("ES91 2100 0418 4502 0005 1332")
True
>>> valid_iban("ES91 2100 0418 4502 0005 1333")
False
```

### `valid_ip`

```python
valid_ip(raw: str, version: int | None = None) -> bool
```

Comprueba si el string es una dirección IPv4 o IPv6 válida.

**Parámetros**

- `raw`: String a validar.
- `version`: `4` o `6` para exigir esa versión; `None` admite ambas.

**Devuelve:** `True` si es una dirección IP válida (de la versión indicada).

**Lanza**

- `ValueError`: Si `version` no es `None`, `4` ni `6`.

**Ejemplos**

```pycon
>>> valid_ip("192.168.1.1")
True
>>> valid_ip("::1", version=4)
False
>>> valid_ip("999.1.1.1")
False
```

### `valid_json`

```python
valid_json(raw: str) -> bool
```

Comprueba si el string es JSON bien formado (RFC 8259).

Se rechazan `NaN`, `Infinity` y `-Infinity`.

**Parámetros**

- `raw`: String a validar.

**Devuelve:** `True` si el string es JSON válido.

**Ejemplos**

```pycon
>>> valid_json('{"a": [1, 2]}')
True
>>> valid_json("{'a': 1}")
False
>>> valid_json("NaN")
False
```

### `valid_mac`

```python
valid_mac(raw: str) -> bool
```

Comprueba si el string es una dirección MAC de 48 bits válida.

Admite los separadores `:` y `-` (seis pares hexadecimales), `.` (tres
grupos de cuatro) o ningún separador (doce dígitos seguidos), en
mayúsculas o minúsculas.

**Parámetros**

- `raw`: String a validar.

**Devuelve:** `True` si el string es una MAC válida.

**Ejemplos**

```pycon
>>> valid_mac("00:1A:2B:3C:4D:5E")
True
>>> valid_mac("00-1a-2b-3c-4d-5e")
True
>>> valid_mac("001A.2B3C.4D5E")
True
>>> valid_mac("00:1A:2B:3C:4D")
False
>>> valid_mac("GG:1A:2B:3C:4D:5E")
False
```

### `valid_nie`

```python
valid_nie(raw: str) -> bool
```

Comprueba si el string es un NIE español válido (X/Y/Z, 7 dígitos, letra).

**Parámetros**

- `raw`: String a validar.

**Devuelve:** `True` si el formato y la letra de control son correctos.

**Ejemplos**

```pycon
>>> valid_nie("X1234567L")
True
>>> valid_nie("X1234567A")
False
```

### `valid_passport`

```python
valid_passport(raw: str) -> bool
```

Comprueba si el string tiene formato de pasaporte genérico.

Cada país usa su propio formato, así que aquí se acepta el patrón más
habitual: entre 6 y 9 caracteres alfanuméricos. No valida el dígito de
control ni el país emisor.

**Parámetros**

- `raw`: String a validar.

**Devuelve:** `True` si el string presenta un formato de pasaporte genérico.

**Ejemplos**

```pycon
>>> valid_passport("ABC123456")
True
>>> valid_passport("12345678")
True
>>> valid_passport("AB123")
False
>>> valid_passport("ABC-1234")
False
```

### `valid_password`

```python
valid_password(
    raw: str,
    length: tuple[int, int],
    special_characters: str = '',
    allow_uppercase: bool = True,
    only_digits: bool = False,
) -> bool
```

Comprueba si el string presenta el formato de contraseña requerido.

Solo valida longitud y caracteres permitidos; no exige mínimos de cada
tipo de carácter. Con `only_digits`, `allow_uppercase` carece de efecto.

**Parámetros**

- `raw`: Contraseña a validar.
- `length`: Rango (mínimo, máximo) de longitud permitida, ambos inclusive.
- `special_characters`: Caracteres especiales permitidos.
- `allow_uppercase`: Mayúsculas permitidas.
- `only_digits`: Si solo se permiten dígitos.

**Devuelve:** `True` si la contraseña cumple las condiciones.

**Lanza**

- `ValueError`: Si se han indicado argumentos ambiguos o incoherentes.

### `valid_phone`

```python
valid_phone(raw: str) -> bool
```

Comprueba si el string es un teléfono en formato internacional básico.

Admite un `+` inicial y los separadores espacio, punto, guion y
paréntesis; exige entre 7 y 15 dígitos (E.164). No valida por país.

**Parámetros**

- `raw`: String a validar.

**Devuelve:** `True` si el formato es válido.

**Ejemplos**

```pycon
>>> valid_phone("+34 612 345 678")
True
>>> valid_phone("(91) 123-4567")
True
>>> valid_phone("12345")
False
```

### `valid_port`

```python
valid_port(raw: str) -> bool
```

Comprueba si el string lo aceptaría `to_port`.

**Parámetros**

- `raw`: String a validar.

**Devuelve:** `True` si el string representa un puerto en el rango 1-65535.

**Ejemplos**

```pycon
>>> valid_port("8080")
True
>>> valid_port("0")
False
>>> valid_port("70000")
False
>>> valid_port("abc")
False
```

### `valid_slug`

```python
valid_slug(raw: str) -> bool
```

Comprueba si el string es un slug: minúsculas, dígitos y guiones simples.

**Parámetros**

- `raw`: String a validar.

**Devuelve:** `True` si el string es un slug válido (el que produce `parse_slug`).

**Ejemplos**

```pycon
>>> valid_slug("hola-mundo")
True
>>> valid_slug("Hola Mundo")
False
>>> valid_slug("hola--mundo")
False
```

### `valid_url`

```python
valid_url(raw: str) -> bool
```

Comprueba si el string presenta formato de URL http/https.

**Parámetros**

- `raw`: String a validar.

**Devuelve:** `True` si es una URL http/https con host y sin espacios.

**Ejemplos**

```pycon
>>> valid_url("https://example.com/x")
True
>>> valid_url("https://[::1")
False
```

### `valid_uuid`

```python
valid_uuid(raw: str) -> bool
```

Comprueba si el string es un UUID en forma canónica (8-4-4-4-12).

**Parámetros**

- `raw`: String a validar.

**Devuelve:** `True` si el string es un UUID válido.

**Ejemplos**

```pycon
>>> valid_uuid("123e4567-e89b-12d3-a456-426614174000")
True
>>> valid_uuid("123e4567")
False
```

## Getters

Obtienen valores del entorno del programa.

### `get_env`

```python
get_env(
    name: str,
    cast: Callable[[str], T | None] = to_int,
    default: T | None = None,
) -> T | None
```

Lee una variable de entorno y la convierte con un conversor `to_*`.

**Parámetros**

- `name`: Nombre de la variable de entorno.
- `cast`: Conversor a aplicar sobre el valor leído (por defecto `to_int`).
- `default`: Valor a devolver si la variable falta o el conversor falla.

**Devuelve:** El valor convertido, o `default` si la variable no está definida o su valor no es convertible por `cast`.

**Ejemplos**

```pycon
>>> import os
>>> from irg_utils import to_str
>>> os.environ["IRG_PORT"] = "8080"
>>> get_env("IRG_PORT")
8080
>>> get_env("IRG_PORT", cast=to_str)
'8080'
>>> get_env("IRG_AUSENTE", default=7)
7
>>> del os.environ["IRG_PORT"]
```

### `get_hash`

```python
get_hash(raw: str | bytes | PathLike[str], algorithm: str = 'sha256') -> str
```

Calcula el hash hexadecimal de un texto, bytes o fichero.

Si `raw` es una ruta a un fichero existente, se hashea su contenido por
bloques (sin cargarlo entero en memoria); en caso contrario se interpreta
como texto o bytes y se codifica en UTF-8.

**Parámetros**

- `raw`: Texto, bytes o ruta a un fichero cuyo hash se quiere calcular.
- `algorithm`: Algoritmo de `hashlib` (por ejemplo `sha256`, `sha1`).

**Devuelve:** El hash en formato hexadecimal.

**Lanza**

- `ValueError`: Si el algoritmo no está soportado por `hashlib`.

**Ejemplos**

```pycon
>>> get_hash("abc")
'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
>>> get_hash(b"abc", "sha1")
'a9993e364706816aba3e25717850c26c9cd0d89d'
```

### `get_hmac`

```python
get_hmac(
    key: str | bytes,
    message: str | bytes,
    algorithm: str = 'sha256',
) -> str
```

Calcula el HMAC hexadecimal de un mensaje con una clave secreta.

A diferencia de `get_hash`, usa una clave, lo que permite verificar la
integridad y autenticidad de un mensaje, no solo su huella.

**Parámetros**

- `key`: Clave secreta (texto o bytes).
- `message`: Mensaje a autenticar (texto o bytes).
- `algorithm`: Algoritmo de `hashlib` (por ejemplo `sha256`, `sha1`).

**Devuelve:** El HMAC en formato hexadecimal.

**Lanza**

- `ValueError`: Si el algoritmo no está soportado por `hashlib`.

**Ejemplos**

```pycon
>>> get_hmac("clave", "mensaje", "sha1")
'25dff5fc3efc225e6d8a520e32dec1c8f671b86f'
>>> get_hmac("Jefe", "what do ya want for nothing?")
'5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843'
```

### `get_now`

```python
get_now() -> datetime
```

Devuelve la fecha y hora actual en UTC, con zona horaria.

**Devuelve:** El `datetime` actual, consciente de zona horaria (UTC).

**Ejemplos**

```pycon
>>> get_now().tzinfo is not None
True
```

### `get_random_password`

```python
get_random_password(
    length: tuple[int, int] = (8, 16),
    special_characters: str = '',
    allow_uppercase: bool = True,
    only_digits: bool = False,
) -> str
```

Genera una contraseña aleatoria que cumple los criterios de `valid_password`.

Usa `secrets` (CSPRNG), nunca `random`. La longitud se elige al azar
dentro del rango indicado y cada carácter se toma del mismo conjunto que
admitiría `valid_password` con esos argumentos.

**Parámetros**

- `length`: Rango (mínimo, máximo) de longitud, ambos inclusive.
- `special_characters`: Caracteres especiales permitidos.
- `allow_uppercase`: Mayúsculas permitidas.
- `only_digits`: Si solo se generan dígitos.

**Devuelve:** La contraseña generada.

**Lanza**

- `ValueError`: Si se han indicado argumentos ambiguos o incoherentes.

### `get_random_token`

```python
get_random_token(nbytes: int = 32, url_safe: bool = True) -> str
```

Genera un token aleatorio criptográficamente seguro con `secrets`.

**Parámetros**

- `nbytes`: Cantidad de bytes de entropía (por defecto 32).
- `url_safe`: Si es `True`, usa codificación URL-segura (`token_urlsafe`); si es `False`, genera hexadecimal (`token_hex`).

**Devuelve:** El token generado.

**Lanza**

- `ValueError`: Si `nbytes` no es un entero positivo.

**Ejemplos**

```pycon
>>> token = get_random_token()
>>> len(token) >= 40
True
>>> len(get_random_token(16, url_safe=False))
32
```
