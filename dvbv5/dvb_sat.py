"""
Provides interfaces to deal with DVB Satellite systems.
"""

from ctypes import Structure, byref
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


class DVBSatLNB(object):
    """
    Stores the information of a LNBf

    The LNBf (low-noise block downconverter) is a type of amplifier that is
    installed inside the parabolic dishes. It converts the antenna signal to
    an Intermediate Frequency. Several Ku-band LNBf have more than one IF.
    The lower IF is stored at lowfreq, the higher IF at highfreq.
    The exact setup for those structs actually depend on the model of the LNBf,
    and its usage.
    """
    def __init__(self, struct: c_dvb_sat_lnb):
        self._dvb_sat_lnb = struct

    @property
    def C_POINTER(self):
        return byref(self._dvb_sat_lnb)

    @property
    def name(self) -> str:
        """
        long name of the LNBf type
        """
        return self._dvb_sat_lnb.name.decode()

    @property
    def alias(self) -> str:
        """
        short name of the LNBf type
        """
        return self._dvb_sat_lnb.alias.decode()


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


def dvb_sat_get_lnb(index: int) -> DVBSatLNB:
    """
    gets a LNBf entry at its internal database
    :param index: index for the entry.
    :return: DVBSatLNB object

    NOTE: none of the strings are i18n translated. In order to get the translated name, you should use
    dvb_sat_get_lnb_name()
    """
    ret = libdvbv5.dvb_sat_get_lnb(index)
    if not ret:
        raise Exception("Entry not found!")
    return DVBSatLNB(ret.contents)


def dvb_sat_get_lnb_name(index: int) -> str:
    """
    gets a LNBf entry at its internal database
    :param index: index for the entry.
    :return: Name of a LNBf

    translated to the user language, if translation is available.
    """
    ret = libdvbv5.dvb_sat_get_lnb_name(index)
    if not ret:
        raise Exception("Entry not found!")
    return ret.decode()
