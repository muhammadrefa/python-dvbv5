"""
Provides interfaces to deal with DVB Satellite systems.
"""

from ctypes import Structure
from ctypes import c_char_p
from ctypes import c_uint

from . import libdvbv5


class c_dvb_sat_lnb(Structure):
    class _c_dvbsat_freqrange(Structure):
        _fields_ = [
            ('low', c_uint),
            ('high', c_uint)
        ]

    _fields_ = [
        ('name', c_char_p),
        ('alias', c_char_p),
        ('lowfreq', c_uint),
        ('highfreq', c_uint),
        ('rangeswitch', c_uint),
        ('freqrange', _c_dvbsat_freqrange * 2),
    ]


def dvb_sat_search_lnb(name: str) -> int:
    """
    Search for a LNBf entry.
    :param name: Name of the LNBf entry to seek
    :return: Non-negative number with corresponds to the LNBf entry inside the LNBf structure
    """
    ret = libdvbv5.dvb_sat_search_lnb(name.encode())
    if ret < 0:
        raise ValueError("LNBf not found!")
    return ret


def dvb_print_lnb(index: int) -> None:
    """
    Prints the contents of a LNBf entry at STDOUT.
    :param index: Index for the entry
    """
    ret = libdvbv5.dvb_print_lnb(index)
    if ret < 0:
        raise IndexError("Index out of range!")


def dvb_print_all_lnb() -> None:
    """
    Prints all LNBf entries at STDOUT.

    This function doesn't return anything. Internally, it calls dvb_print_lnb() for all entries inside its LNBf
    database.
    """
    libdvbv5.dvb_print_all_lnb()
