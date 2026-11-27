"""Carga del CSV de 1 minuto.

Cada vela se guarda en arrays compactos. El tiempo se guarda como ``om``:
minutos desde el ordinal de fecha (``date.toordinal() * 1440 + minuto del día``)
de la APERTURA de la vela en hora ET ingenua (sin zona horaria). Como la marca
del CSV es el cierre, ``om = marca - 1``.
"""

from array import array
from dataclasses import dataclass, field
from datetime import date


@dataclass
class Bars:
    om: array = field(default_factory=lambda: array("q"))
    open: array = field(default_factory=lambda: array("d"))
    high: array = field(default_factory=lambda: array("d"))
    low: array = field(default_factory=lambda: array("d"))
    close: array = field(default_factory=lambda: array("d"))
    volume: array = field(default_factory=lambda: array("d"))

    def __len__(self):
        return len(self.close)

    def append(self, om, o, h, l, c, v):
        self.om.append(om)
        self.open.append(o)
        self.high.append(h)
        self.low.append(l)
        self.close.append(c)
        self.volume.append(v)


def stamp_to_open_minute(stamp, _cache={}):
    """'YYYY-MM-DD HH:MM[:SS]' (cierre ET) -> minuto absoluto de APERTURA."""
    d = stamp[:10]
    base = _cache.get(d)
    if base is None:
        base = date.fromisoformat(d).toordinal() * 1440
        _cache[d] = base
    return base + int(stamp[11:13]) * 60 + int(stamp[14:16]) - 1


def minute_of_day(om):
    return om % 1440


def open_date(om):
    return date.fromordinal(om // 1440)


def format_open(om):
    d = open_date(om)
    m = om % 1440
    return "%s %02d:%02d" % (d.isoformat(), m // 60, m % 60)


def load_csv(path, limit=None):
    bars = Bars()
    with open(path, "r", encoding="utf-8") as f:
        header = f.readline().strip().lower().split(",")
        if header[:6] != ["datetime", "open", "high", "low", "close", "volume"]:
            raise ValueError("encabezado inesperado: %r" % (header,))
        n = 0
        for line in f:
            if limit is not None and n >= limit:
                break
            p = line.rstrip("\r\n").split(",")
            if len(p) < 6:
                continue
            bars.append(stamp_to_open_minute(p[0]), float(p[1]), float(p[2]),
                        float(p[3]), float(p[4]), float(p[5]))
            n += 1
    return bars
