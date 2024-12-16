"""
Provides interfaces to scan programs inside MPEG-TS digital TV streams.
"""

from ctypes import Structure, POINTER, byref
from ctypes import c_void_p
from ctypes import c_uint, c_uint32

from . import libdvbv5
from . import dvb_fe
from . import dvb_file


class c_dvb_v5_descriptors(Structure):
    _fields_ = [
        ('delivery_systems', c_uint32),
        ('entry', POINTER(dvb_file.c_dvb_entry)),
        ('num_entry', c_uint),
        ('pat', c_void_p),      # *dvb_table_pat
        ('vct', c_void_p),      # *atsc_table_vct
        ('program', c_void_p),  # *dvb_v5_descriptors_program
        ('nit', c_void_p),      # *dvb_table_nit
        ('sdt', c_void_p),      # *dvb_table_sdt
        ('num_program', c_uint),
        ('other_nits', c_void_p),  # **dvb_table_nit
        ('num_other_nits', c_uint),
        ('other_sdts', c_void_p),  # **dvb_table_sdt
        ('num_other_sdts', c_uint),
    ]


class DVBv5Descriptors(object):
    """
    Contains the descriptors needed to scan the Service ID and other relevant info at a MPEG-TS Digital TV stream

    Those descriptors are filled by the scan routines when the tables are found. Otherwise, they're None.
    """
    def __init__(self, struct: c_dvb_v5_descriptors):
        self._dvb_v5_descriptors: c_dvb_v5_descriptors = struct
        # TODO: Check how to alloc this

    def __del__(self):
        libdvbv5.dvb_scan_free_handler_table(self.C_POINTER)

    @property
    def C_POINTER(self) -> POINTER(c_dvb_v5_descriptors):
        return byref(self._dvb_v5_descriptors)

    @property
    def num_entry(self) -> int:
        return self._dvb_v5_descriptors.num_entry

    @property
    def num_program(self) -> int:
        """
        Number of program entries at @ref program array.
        """
        return self._dvb_v5_descriptors.num_program

    # TODO: Access other struct fields


def dvb_add_scaned_transponders(parms: dvb_fe.DVBv5FEParms, dvb_scan_handler: DVBv5Descriptors,
                                target: dvb_file.DVBFile, entry: dvb_file.DVBEntry) -> None:
    """
    Add new transponders to a dvb_file
    :param parms: DVBv5FEParms object that created when the frontend is opened
    :param dvb_scan_handler: DVBv5Descriptors object containing scaned MPEG-TS
    :param target: DVBFile object which the entry will be added to
    :param entry: DVBEntry to add

    When the NIT table is parsed, some new transponders could be described inside. This function adds new entries to a
    DVBFile with the new transponders. It is used inside the scan loop, as shown at the dvb_scan_transponder(), to add
    new channels.
    """
    return libdvbv5.dvb_add_scaned_transponders(parms.C_POINTER, dvb_scan_handler.C_POINTER,
                                                target.entry[0].C_POINTER, entry.C_POINTER)


def dvb_estimate_freq_shift(parms: dvb_fe.DVBv5FEParms) -> int:
    return libdvbv5.dvb_estimate_freq_shift(parms.C_POINTER)
