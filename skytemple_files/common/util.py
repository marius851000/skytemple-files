#  Copyright 2020 Parakoopa
#
#  This file is part of SkyTemple.
#
#  SkyTemple is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SkyTemple is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SkyTemple.  If not, see <https://www.gnu.org/licenses/>.

import warnings
from typing import List

from ndspy.fnt import Folder
from ndspy.rom import NintendoDSRom


DEBUG = False


def read_bytes(data: bytes, start=0, length=1) -> bytes:
    """
    Read a number of bytes (default 1) from a bytes-like object
    Recommended usage with memoryview for performance!
    """
    _check_memoryview(data)
    return data[start:(start+length)]


def read_uintle(data: bytes, start=0, length=1) -> int:
    """
    Return an unsiged integer in little endian from the bytes-like object at the given position.
    Recommended usage with memoryview for performance!
    """
    _check_memoryview(data)
    return int.from_bytes(data[start:(start+length)], byteorder='little', signed=False)


def read_sintle(data: bytes, start=0, length=1) -> int:
    """
    Return an signed integer in little endian from the bytes-like object at the given position.
    Recommended usage with memoryview for performance!
    """
    _check_memoryview(data)
    return int.from_bytes(data[start:(start+length)], byteorder='little', signed=True)


def read_uintbe(data: bytes, start=0, length=1) -> int:
    """
    Return an unsiged integer in big endian from the bytes-like object at the given position.
    Recommended usage with memoryview for performance!
    """
    _check_memoryview(data)
    return int.from_bytes(data[start:(start+length)], byteorder='big', signed=False)


def read_sintbe(data: bytes, start=0, length=1) -> int:
    """
    Return an signed integer in big endian from the bytes-like object at the given position.
    Recommended usage with memoryview for performance!
    """
    _check_memoryview(data)
    return int.from_bytes(data[start:(start+length)], byteorder='big', signed=True)


def write_uintle(data: bytes, to_write: int, start=0, length=1):
    """
    Write an unsiged integer in little endian to the bytes-like mutable object at the given position.
    """
    data[start:start+length] = to_write.to_bytes(length, byteorder='little', signed=False)


def write_sintle(data: bytes, to_write: int, start=0, length=1):
    """
    Write an signed integer in little endian to the bytes-like mutable object at the given position.
    """
    data[start:start+length] = to_write.to_bytes(length, byteorder='little', signed=True)


def write_uintbe(data: bytes, to_write: int, start=0, length=1):
    """
    Write an unsiged integer in big endian to the bytes-like mutable object at the given position.
    """
    data[start:start+length] = to_write.to_bytes(length, byteorder='big', signed=False)


def write_sintbe(data: bytes, to_write: int, start=0, length=1):
    """
    Write an signed integer in big endian to the bytes-like mutable object at the given position.
    """
    data[start:start+length] = to_write.to_bytes(length, byteorder='big', signed=True)


def iter_bits(number: int):
    """Iterate over the bits of a byte, starting with the high bit"""
    bit = 0x80
    while bit > 0:
        if number & bit:
            yield 1
        else:
            yield 0
        bit >>= 1


def iter_bytes(data: bytes, slice_size, start=0, end=None):
    if end is None:
        end = len(data)
    _check_memoryview(data)
    for i in range(start, end, slice_size):
        yield data[i: i + slice_size]


def iter_bytes_4bit_le(data: bytes, start=0, end=None):
    """
    Generator that generates two 4 bit integers for each byte in the bytes-like object data.
    The 4 bit integers are expected to be stored little endian in the bytes.
    """
    for byte in iter_bytes(data, 1, start, end):
        upper = byte[0] >> 4
        lower = byte[0] & 0x0f
        yield lower
        yield upper


def get_files_from_rom_with_extension(rom: NintendoDSRom, ext: str) -> List[str]:
    """Returns paths to files in the ROM ending with the specified extension."""
    return _get_files_from_rom_with_extension__recursion('', rom.filenames, ext)


def _get_files_from_rom_with_extension__recursion(path: str, folder: Folder, ext: str) -> List[str]:
    files = [path + x for x in folder.files if x.endswith('.' + ext)]
    for subfolder in folder.folders:
        files += _get_files_from_rom_with_extension__recursion(
            path + subfolder[0] + '/', subfolder[1], ext
        )
    return files


def _check_memoryview(data):
    """Check if data is actually a memory view object and if not warn. Only used for testing, otherwise does nothing."""
    if DEBUG and not isinstance(data, memoryview):
        warnings.warn('Byte operation without memoryview.')


def lcm(x, y):
    from math import gcd
    return x * y // gcd(x, y)


def make_palette_colors_unique(inp: List[List[int]]) -> List[List[int]]:
    """
    Works with a list of lists of rgb color palettes and returns a modified copy.

    Returns a list that does not contain duplicate colors. This is done by slightly changing
    the color values of duplicate colors.
    """
    # List of single RGB colors
    already_collected_colors = []
    out = []
    for palette in inp:
        out_p = []
        out.append(out_p)
        for color_idx in range(0, len(palette), 3):
            color = palette[color_idx:color_idx+3]
            new_color = _mpcu__check(color, already_collected_colors)
            already_collected_colors.append(new_color)
            out_p += new_color

    return out


def _mpcu__check(color: List[int], already_collected_colors: List[List[int]], change_next=0, change_amount=1) -> List[int]:
    if color not in already_collected_colors:
        return color
    else:
        # Try to find a unique color
        # Yes I didn't really think all that much when writing this and it doesn't even cover all possibilities.
        if change_next == 0:
            # r + 1
            new_color = [color[0] + change_amount, color[1]                , color[2]                ]
        elif change_next == 1:
            # g + 1
            new_color = [color[0] - change_amount, color[1] + change_amount, color[2]                ]
        elif change_next == 2:
            # b + 1
            new_color = [color[0]                , color[1] - change_amount, color[2] + change_amount]
        elif change_next == 3:
            # gb + 1
            new_color = [color[0]                , color[1] + change_amount, color[2]]
        elif change_next == 4:
            # rgb + 1
            new_color = [color[0] + change_amount, color[1]                , color[2]]
        elif change_next == 5:
            # rg + 1
            new_color = [color[0]                , color[1]                , color[2] - change_amount]
        elif change_next == 6:
            # b - 1
            new_color = [color[0] - change_amount, color[1] - change_amount, color[2] - change_amount]
        elif change_next == 7:
            # g - 1
            new_color = [color[0]                , color[1] - change_amount, color[2] + change_amount]
        else:
            # r - 1
            new_color = [color[0] - change_amount, color[1] + change_amount, color[2]                ]
        for i in [0, 1, 2]:
            if new_color[i] < 0:
                new_color[i] = 0
            elif new_color[i] > 255:
                new_color[i] = 255
        new_change_next = (change_next + 1) % 8
        if new_change_next == 0:
            change_amount += 1
        return _mpcu__check(new_color, already_collected_colors, new_change_next, change_amount)
