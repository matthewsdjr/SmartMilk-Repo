"""Funciones utilitarias para el protocolo USB HID."""


def shiftBytes(list):
    """Combinar lista de bytes en un entero (big-endian)."""
    sum_to_return = 0
    for count, item in enumerate(list):
        sum_to_return += item << ((len(list) - 1 - count) * 8)
    return sum_to_return
