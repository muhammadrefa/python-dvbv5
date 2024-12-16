"""
Provides interfaces to deal with DVB channel and program files.

There are basically two types of files used for DVB:
- files that describe the physical channels (also called as transponders);
- files that describe the several programs found on a MPEG-TS (also called as zap files).

The libdvbv5 library defines an unified type for both types. Other applications generally use different formats.

The purpose of the functions and structures defined herein is to provide support to read and write to those different
formats.
"""

from __future__ import annotations

import enum

from ctypes import Structure, POINTER, byref, cast
from ctypes import c_int, c_uint, c_uint16, c_uint32
from ctypes import c_char_p, c_void_p
from typing import List, Dict, Union, TYPE_CHECKING

from . import libdvbv5
from . import dvb_frontend
from . import dvb_fe
from . import dvb_v5_std

if TYPE_CHECKING:
    from . import dvb_scan


class c_dvb_entry(Structure):
    _fields_ = [
        ('props', dvb_frontend.c_dtv_property * dvb_frontend.DTV_MAX_COMMAND),
        ('n_props', c_uint),
        ('next', c_void_p),     # *c_dvb_entry
        ('service_id', c_uint16),
        ('video_pid', POINTER(c_uint16)),
        ('audio_pid', POINTER(c_uint16)),
        ('other_el_pid', c_void_p),     # *dvb_elementary_pid
        ('video_pid_len', c_uint),
        ('audio_pid_len', c_uint),
        ('other_el_pid_len', c_uint),
        ('channel', c_char_p),
        ('vchannel', c_char_p),
        ('location', c_char_p),
        ('sat_number', c_int),
        ('freq_bpf', c_uint),
        ('diseqc_wait', c_uint),
        ('lnb', c_char_p),
        ('network_id', c_uint16),
        ('transport_id', c_uint16),
    ]


class c_dvb_file(Structure):
    _fields_ = [
        ('fname', c_char_p),
        ('n_entries', c_int),
        ('first_entry', POINTER(c_dvb_entry)),
    ]


class DVBEntry(object):
    """
    Represents one entry on a DTV file
    """
    def __init__(self, struct: c_dvb_entry=None):
        self._dvb_entry: c_dvb_entry = None
        if struct is not None:
            self._dvb_entry = struct

    @property
    def C_POINTER(self) -> POINTER(c_dvb_entry):
        return byref(self._dvb_entry)

    @property
    def props(self) -> Dict[int, int]:
        """
        A property key/value pair. The keys are the ones specified at the DVB API, plus the ones defined internally by
        libdvbv5, at the dvb_v5_std file
        :return:
        """
        _p = dict()
        for i in range(0, self._dvb_entry.n_props):
            _cmd = self._dvb_entry.props[i].cmd
            if _cmd <= dvb_frontend.DTV_MAX_COMMAND:
                cmd = dvb_frontend.DVBv5PropertyCommand(_cmd)
            elif dvb_v5_std.DTV_USER_COMMAND_START <= _cmd <= dvb_v5_std.DTV_MAX_USER_COMMAND:
                cmd = dvb_v5_std.DTVUserPropertyCommand(_cmd)
            else:
                cmd = _cmd
            _p[cmd] = self._dvb_entry.props[i].u.data
        return _p

    @property
    def service_id(self) -> int:
        """
        Service ID associated with a program inside a transponder. Please note that pure "channel" files will have this
        field filled with 0.
        :return:
        """
        return self._dvb_entry.service_id

    @property
    def video_pid(self) -> List[int]:
        """
        List of video program IDs inside a service
        """
        _video_pid = list()
        for i in range(0, self._dvb_entry.video_pid_len):
            _video_pid.append(self._dvb_entry.video_pid[i])
        return _video_pid

    @property
    def audio_pid(self) -> List[int]:
        """
        List of audio program IDs inside a service
        """
        _audio_pid = list()
        for i in range(0, self._dvb_entry.audio_pid_len):
            _audio_pid.append(self._dvb_entry.audio_pid[i])
        return _audio_pid

    # TODO: other_el_pid

    @property
    def channel(self) -> str:
        """
        Channel name
        """
        return self._dvb_entry.channel.decode()

    @property
    def vchannel(self) -> str:
        """
        String representing the Number of the channel
        """
        return self._dvb_entry.vchannel.decode()

    @property
    def location(self) -> str:
        """
        String representing the location of the channel
        """
        return self._dvb_entry.location.decode()

    @property
    def sat_number(self) -> int:
        """
        For satellite streams, this represents the number of the satellite dish on a DiSeqC arrangement.
        Should be zero on arrangements without DiSeqC.
        """
        return self._dvb_entry.sat_number

    @property
    def freq_bpf(self) -> int:
        """
        SCR/Unicable band-pass filter frequency to use, in kHz.
        For non SRC/Unicable arrangements, it should be zero.
        """
        return self._dvb_entry.freq_bpf

    @property
    def diseqc_wait(self) -> int:
        """
        Extra time to wait for DiSeqC commands to complete, in ms. The library will use 15 ms as the minimal time,
        plus the time specified on this field.
        :return:
        """
        return self._dvb_entry.diseqc_wait

    # TODO: lnb

    @property
    def network_id(self) -> int:
        return self._dvb_entry.network_id

    @property
    def transport_id(self) -> int:
        return self._dvb_entry.transport_id



class DVBFile(object):
    """
    Describes an entire DVB file opened
    """
    def __init__(self, struct: c_dvb_file=None):
        self._dvb_file: c_dvb_file = None
        if struct is not None:
            self._dvb_file = struct

    def __del__(self):
        # TODO: dvb_file_free is static inline void
        # libdvbv5.dvb_file_free(self.C_POINTER)
        pass

    @property
    def C_POINTER(self) -> POINTER(c_dvb_file):
        return byref(self._dvb_file)

    @property
    def n_entries(self) -> int:
        """
        Number of the entries read
        """
        return self._dvb_file.n_entries

    @property
    def entry(self) -> List[DVBEntry]:
        entry = list()
        _e = self._dvb_file.first_entry
        while _e:
            entry.append(DVBEntry(_e.contents))
            _e = cast(_e.contents.next, POINTER(c_dvb_entry))
        return entry


class DVBFileFormat(enum.IntEnum):
    """
    Known file formats

    Please notice that the channel format defined here has a few optional fields that aren't part of the dvb-apps
    format, for DVB-S2 and for DVB-T2. They're there to match the formats found at dtv-scan-tables package up to
    September, 5 2014.
    """
    FILE_UNKNOWN = 0,
    FILE_ZAP = enum.auto(),
    """
    File is at the dvb-apps "dvbzap" format
    """
    FILE_CHANNEL = enum.auto(),
    """
    File is at the dvb-apps output format for dvb-zap
    """
    FILE_DVBV5 = enum.auto(),
    FILE_VDR = enum.auto(),
    """
    File is at DVR format (as supported on version 2.1.6).
    Note: this is only supported as an output format.
    """


def dvb_read_file_format(filename: str, delivery_system: dvb_frontend.FEDeliverySystem, fmt: DVBFileFormat) -> DVBFile:
    """
    Read a file on any format natively supported by the library
    :param filename: File name
    :param delivery_system: Delivery system, as specified by enum FEDeliverySystem
    :param fmt: Name of the format to be read
    :return: DVBFile object describing the entries that were read from the file
    """
    c_dvb_read_file_format = libdvbv5.dvb_read_file_format
    c_dvb_read_file_format.restype = POINTER(c_dvb_file)
    _c_dvb_file = c_dvb_read_file_format(filename.encode(), delivery_system, fmt)
    if _c_dvb_file is None:
        raise Exception("Read file failed!")
    return DVBFile(_c_dvb_file.contents)


def dvb_write_file_format(filename: str, dvb_file: DVBFile, delivery_system: dvb_frontend.FEDeliverySystem,
                          fmt: DVBFileFormat) -> DVBFile:
    """
    Write a file on any format natively supported by the library
    :param filename: File name
    :param dvb_file: Contents of the file to be written
    :param delivery_system: Delivery system, as specified by enum FEDeliverySystem
    :param fmt: Name of the format to be read
    :return: DVBFile object
    """
    _c_dvb_file = libdvbv5.dvb_write_file_format(filename.encode(), dvb_file.C_POINTER, delivery_system, fmt)
    if _c_dvb_file is None:
        raise Exception("Write file failed!")
    return DVBFile(_c_dvb_file.contents)


def dvb_retrieve_entry_prop(entry: DVBEntry,
                            cmd: Union[dvb_frontend.DVBv5PropertyCommand, dvb_v5_std.DTVUserPropertyCommand]) -> int:
    """
    Retrieves the value associated with a key on a DVB file entry
    :param entry: Entry to be used
    :param cmd: Key for the property to be found. It be one of the DVBv5 properties, plus the libdvbv5 ones,
    as defined at dvb_v5_std
    :return: Value associated with the property

    This function seeks for a property with the name specified by cmd and returns its contents.
    """
    val = c_uint32()
    ret = libdvbv5.dvb_retrieve_entry_prop(entry.C_POINTER, cmd, byref(val))
    if ret:
        raise KeyError("Entry does not exist!")
    return val.value


def dvb_store_channel(parms: dvb_fe.DVBv5FEParms, dvb_desc: dvb_scan.DVBv5Descriptors, get_detected: int,
                      get_nit: bool) -> DVBFile:
    """
    Stored a new scanned channel into a DVBFile object
    :param parms: DVBv5Descriptors used by libdvbv5 frontend
    :param dvb_desc: DVBv5Descriptors filled with the descriptors associated with a DVB channel. Those descriptors
    can be filled by calling one of the scan functions defined at dvb_sat.
    :param get_detected: If different than zero, uses the frontend parameters obtained from the device driver (such as
    modulation, FEC, etc)
    :param get_nit: If true, uses the parameters obtained from the MPEG-TS NIT table to add newly detected transponders.
    :return: Filled DVBFile object

    This function should be used to store the services found on a scanned transponder. Initially, it copies the same
    parameters used to set the frontend, that came from a file where the Service ID and Elementary Stream PIDs are
    unknown. At tuning time, it is common to set the device to tune on auto-detection mode (e. g. using QAM/AUTO,
    for example, to autodetect the QAM modulation). The libdvbv5's logic will be to check the detected values.
    So, the modulation might, for example, have changed to QAM/256. In such case, if get_detected is 0, it will store
    QAM/AUTO at the struct. If get_detected is different than zero, it will store QAM/256. If get_nit is different than
    zero, and if the MPEG-TS has info about other physical channels/transponders, this function will add newer entries
    to dvb_file, for it to seek for new transponders. This is very useful especially for DVB-C, where all transponders
    belong to the same operator. Knowing one frequency is generally enough to get all DVB-C transponders.
    """
    new_dvb_file = POINTER(c_dvb_file)()
    ret = libdvbv5.dvb_store_channel(byref(new_dvb_file), parms.C_POINTER, dvb_desc.C_POINTER, get_detected,
                                     1 if get_nit else 0)
    if ret:
        raise Exception("Store failed!")
    return DVBFile(new_dvb_file.contents)
