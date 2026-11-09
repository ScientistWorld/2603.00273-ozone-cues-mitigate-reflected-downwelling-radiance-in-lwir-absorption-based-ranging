"""Minimal MATLAB v5 (.mat) reader for numeric arrays, standard library only.

Only what the gym needs: real numeric matrices, optionally zlib-compressed.
Arrays are returned as (dims, flat column-major list).
"""

from __future__ import annotations

import array
import struct
import zlib
from pathlib import Path

_MI_TYPES = {1: "b", 2: "B", 3: "h", 4: "H", 5: "i", 6: "I", 7: "f", 9: "d", 12: "q", 13: "Q"}
_MI_COMPRESSED = 15
_MI_MATRIX = 14


def _elements(buf: bytes, off: int, end: int):
    while off < end:
        tag, nbytes = struct.unpack_from("<II", buf, off)
        if tag >> 16:  # small data element format
            nbytes = tag >> 16
            tag &= 0xFFFF
            yield tag, buf[off + 4 : off + 4 + nbytes]
            off += 8
        else:
            yield tag, buf[off + 8 : off + 8 + nbytes]
            off += 8 + nbytes + ((8 - nbytes % 8) % 8)


def _parse_matrix(payload: bytes) -> tuple[str, tuple[int, ...], list[float]]:
    items = _elements(payload, 0, len(payload))
    next(items)  # array flags
    _, dims_raw = next(items)
    _, name_raw = next(items)
    dims = struct.unpack("<%di" % (len(dims_raw) // 4), dims_raw)
    dtype, data = next(items)
    code = _MI_TYPES[dtype]
    values = array.array(code)
    values.frombytes(data[: len(data) // values.itemsize * values.itemsize])
    return name_raw.decode("ascii"), tuple(dims), [float(v) for v in values]


def load_mat(path: str | Path) -> dict[str, tuple[tuple[int, ...], list[float]]]:
    buf = Path(path).read_bytes()
    out: dict[str, tuple[tuple[int, ...], list[float]]] = {}
    off = 128
    while off < len(buf):
        tag, nbytes = struct.unpack_from("<II", buf, off)
        payload = buf[off + 8 : off + 8 + nbytes]
        off += 8 + nbytes
        if tag == _MI_COMPRESSED:
            payload = zlib.decompress(payload)
            tag, nbytes = struct.unpack_from("<II", payload, 0)
            payload = payload[8 : 8 + nbytes]
        if tag == _MI_MATRIX:
            name, dims, values = _parse_matrix(payload)
            out[name] = (dims, values)
    return out
