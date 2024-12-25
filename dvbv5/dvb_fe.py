"""
Provides interfaces to deal with DVB frontend.

The libdvbv5 API works with a set of key/value properties.
There are two types of properties:

- The ones defined at the Kernel's frontend API, that are found at /usr/include/linux/dvb/frontend.h (actually, it
  uses a local copy of that file, stored at ./include/linux/dvb/frontend.h)

- Some extra properties used by libdvbv5. Those can be found at lib/include/libdvbv5/dvb-v5-std.h and start at
  DTV_USER_COMMAND_START.

Just like the DTV properties, the stats are cached. That warrants that all stats are got at the same time, when
dvb_fe_get_stats() is called.
"""

from ctypes import Structure, POINTER, byref
from ctypes import c_int, c_uint, c_int32, c_uint32
from ctypes import c_void_p, c_char_p
from typing import List, Union

from . import libdvbv5
from . import dvb_frontend
from . import dvb_sat
from . import dvb_v5_std


MAX_DELIVERY_SYSTEMS = 20


class c_dvb_v5_fe_parms(Structure):
    _fields_ = [
        ('info', dvb_frontend.c_dvb_frontend_info),     # RO
        ('version', c_int32),       # RO
        ('has_v5_stats', c_int),    # RO
        ('current_sys', c_int),     # RO (dvb_frontend.FEDeliverySystem)
        ('num_systems', c_int),     # RO
        ('systems', c_int * MAX_DELIVERY_SYSTEMS),      # RO (dvb_frontend.FEDeliverySystem)
        ('legacy_fe', c_int),       # RO
        ('abort', c_int),           # RW
        ('lna', c_int),             # RW
        ('lnb', POINTER(dvb_sat.c_dvb_sat_lnb)),        # RW
        ('sat_number', c_int),      # RW
        ('freq_bpf', c_uint),
        ('diseqc_wait', c_uint),
        ('verbose', c_uint),        # RW
        ('logfunc', c_void_p),      # RO (dvb_logfunc)
        ('default_charset', c_char_p),  # RW
        ('output_charset', c_char_p)    # RW
    ]


class DVBv5FEParms(object):
    """
    Keeps data needed to handle the DVB frontend
    """
    def __init__(self, struct: c_dvb_v5_fe_parms=None):
        self._dvb_v5_fe_parms: c_dvb_v5_fe_parms = struct
        # TODO: Check how to allocate

    @property
    def C_POINTER(self) -> POINTER(c_dvb_v5_fe_parms):
        return byref(self._dvb_v5_fe_parms)

    @property
    def version(self) -> int:
        """
        Version of the Linux DVB API (RO)
        """
        return self._dvb_v5_fe_parms.version

    @property
    def has_v5_stats(self) -> int:
        """
        A value different than 0 indicates that the frontend supports DVBv5 stats (RO)
        """
        return self._dvb_v5_fe_parms.has_v5_stats

    @property
    def current_sys(self) -> dvb_frontend.FEDeliverySystem:
        """
        Currently selected delivery system (RO)
        """
        return dvb_frontend.FEDeliverySystem(self._dvb_v5_fe_parms.current_sys)

    @property
    def systems(self) -> List[dvb_frontend.FEDeliverySystem]:
        """
        Delivery systems supported by the hardware (RO)
        """
        return [dvb_frontend.FEDeliverySystem(self._dvb_v5_fe_parms.system[i]) for i in range(0, self._dvb_v5_fe_parms.num_systems)]

    @property
    def abort(self):
        return self._dvb_v5_fe_parms.abort

    @abort.setter
    def abort(self, value: int):
        self._dvb_v5_fe_parms.abort = value

    # TODO: Access other struct fields


def dvb_set_compat_delivery_system(parms: DVBv5FEParms, desired_systems: dvb_frontend.FEDeliverySystem) -> None:
    ret = libdvbv5.dvb_set_compat_delivery_system(parms.C_POINTER, desired_systems)
    if ret < 0:
        raise ValueError("Set compat delivery system unsuccessful!")


def dvb_fe_retrieve_parm(parms: DVBv5FEParms,
                         cmd: Union[dvb_frontend.DVBv5PropertyCommand, dvb_v5_std.DTVUserPropertyCommand]) -> int:
    """
    Retrieves the value of a DVBv5/libdvbv5 property
    :param parms: DVBv5FEParms object of the opened device
    :param cmd: DVBv5 or libdvbv5 property
    :return: Value associated with the property

    This reads the value of a property stored at the cache. Before using it, a dvb_fe_get_parms() is likely required.
    """
    _v = c_uint32()
    ret = libdvbv5.dvb_fe_retrieve_parm(parms.C_POINTER, cmd, byref(_v))
    if ret:
        raise ValueError(f"Retrieve parm unsuccessful! (cmd: {cmd})")
    return _v.value


def dvb_fe_store_parm(parms: DVBv5FEParms,
                      cmd: Union[dvb_frontend.DVBv5PropertyCommand, dvb_v5_std.DTVUserPropertyCommand],
                      value: int) -> int:
    """
    Stores the value of a DVBv5/libdvbv5 property
    :param parms: DVBv5FEParms object of the opened device
    :param cmd: DVBv5 or libdvbv5 property
    :param value: Value to be stored
    """
    ret = libdvbv5.dvb_fe_store_parm(parms.C_POINTER, cmd, value)
    if ret < 0:
        raise ValueError("Store parm unsuccessful!")


def dvb_fe_set_parms(parms: DVBv5FEParms) -> None:
    """
    Prints all the properties at the cache
    :param parms: DVBv5FEParms object of the opened device

    Writes the properties stored at the DVB cache at the DVB hardware. At return, some properties could have a
    different value, as the frontend may not support the values set.
    """
    ret = libdvbv5.dvb_fe_set_parms(parms.C_POINTER)
    if ret:
        raise ValueError("Set parms failed!")


def dvb_fe_get_parms(parms: DVBv5FEParms) -> None:
    """
    Prints all the properties at the cache
    :param parms: DVBv5FEParms object of the opened device

    Gets the properties from the DVB hardware. The values will only reflect what's set at the hardware if the frontend
    is locked.
    """
    ret = libdvbv5.dvb_fe_get_parms(parms.C_POINTER)
    if ret:
        raise ValueError("Get parms failed!")


def dvb_fe_retrieve_stats_layer(parms: DVBv5FEParms, cmd: dvb_v5_std.DTVStatPropertyCommand, layer: int) -> int:
    """
    Retrieve the stats for a DTV layer from cache
    :param parms: DVBv5FEParms object of the opened device
    :param cmd: DVBv5 or libdvbv5 property
    :param layer: DTV layer
    :return: Value associated with the property

    Gets the value for one stats property for layer = 0.

    For it to be valid, dvb_fe_get_stats() should be called first.
    """
    _v = c_uint32()
    ret = libdvbv5.dvb_fe_retrieve_stats(parms.C_POINTER, cmd, byref(_v))
    if ret:
        raise ValueError(f"Retrieve stats failed! (cmd: {cmd})")
    return _v.value


def dvb_fe_retrieve_stats(parms: DVBv5FEParms, cmd: dvb_v5_std.DTVStatPropertyCommand) -> int:
    """
    Retrieve the stats for a DTV layer from cache
    :param parms: DVBv5FEParms object of the opened device
    :param cmd: DVBv5 or libdvbv5 property
    :return: Value associated with the property

    Gets the value for one stats property for layer = 0.

    For it to be valid, dvb_fe_get_stats() should be called first.
    """
    _v = c_uint32()
    ret = libdvbv5.dvb_fe_retrieve_stats(parms.C_POINTER, cmd, byref(_v))
    if ret:
        raise ValueError(f"Retrieve stats failed! (cmd: {cmd})")
    return _v.value


def dvb_fe_get_stats(parms: DVBv5FEParms) -> None:
    """
    Retrieve the stats from the Kernel
    :param parms: DVBv5FEParms object of the opened device
    """
    ret = libdvbv5.dvb_fe_get_stats(parms.C_POINTER)
    if ret:
        raise ValueError("Get stats failed!")


def dvb_fe_set_default_country(parms: DVBv5FEParms, country: str) -> None:
    """
    Set default country variant of delivery systems like ISDB-T
    :param parms: DVBv5FEParms object of the opened device
    :param country: default country, in ISO 3166-1 two letter code. If None, default charset is guessed from locale
    environment variables.
    """
    ret = libdvbv5.dvb_fe_set_default_country(parms.C_POINTER, country.encode() if country is not None else None)
    if ret:
        raise ValueError("Country unknown!")
