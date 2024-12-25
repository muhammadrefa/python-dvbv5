"""
Provides interfaces to handle Digital TV devices.

Digital TV device node file names depend on udev configuration. For example, while frontends are typically
found at/dev/dvb/adapter?/frontend?, the actual file name can vary from system to system, depending on the
udev ruleset.

The libdvbv5 provides a set of functions to allow detecting and getting the device paths in a sane way, via libudev.
"""

import enum

from ctypes import Structure, POINTER, byref, CFUNCTYPE
from ctypes import c_char_p, c_void_p, c_int
from ctypes import py_object
from typing import Callable, List, Any

from . import libdvbv5
from . import dvb_fe
from . import dvb_file
from . import dvb_scan
from ._dvbv3 import dmx


class c_dvb_dev_list(Structure):
    _fields_ = [
        ('syspath', c_char_p),
        ('path', c_char_p),
        ('sysname', c_char_p),
        ('dvb_type', c_int),
        ('bus_addr', c_char_p),
        ('bus_id', c_char_p),
        ('manufacturer', c_char_p),
        ('product', c_char_p),
        ('serial', c_char_p),
    ]


class c_dvb_open_descriptor(Structure):
    pass


class c_dvb_device(Structure):
    _fields_ = [
        ('devices', POINTER(c_dvb_dev_list)),
        ('num_devices', c_int),
        ('fe_parms', POINTER(dvb_fe.c_dvb_v5_fe_parms))
    ]


class DVBDevType(enum.IntEnum):
    """
    DVB device types
    """
    DVB_DEVICE_FRONTEND = 0,
    DVB_DEVICE_DEMUX = enum.auto(),
    DVB_DEVICE_DVR = enum.auto(),
    DVB_DEVICE_NET = enum.auto(),
    DVB_DEVICE_CA = enum.auto(),
    DVB_DEVICE_CA_SEC = enum.auto(),
    DVB_DEVICE_VIDEO = enum.auto(),
    DVB_DEVICE_AUDIO = enum.auto()


class DVBDevChangeType(enum.IntEnum):
    """
    Describes the type of change to be notifier_delay
    """

    DVB_DEV_ADD = 0,
    """New device detected"""

    DVB_DEV_CHANGE = enum.auto(),
    """Device has changed something"""

    DVB_DEV_REMOVE = enum.auto()
    """A hot-pluggable device was removed"""


class DVBDevList(object):
    """
    Digital TV device node properties
    """
    def __init__(self, struct: c_dvb_dev_list=None):
        self._dvb_dev_list: c_dvb_dev_list = struct

    @property
    def C_POINTER(self) -> POINTER(c_dvb_dev_list):
        """
        Pointer to dvb_dev_list C struct
        """
        return byref(self._dvb_dev_list)

    @property
    def syspath(self) -> str:
        return self._dvb_dev_list.syspath.decode()

    @property
    def path(self) -> str:
        """
        Path for the /dev file handler
        """
        return self._dvb_dev_list.path.decode()

    @property
    def sysname(self) -> str:
        """
        Kernel's system name for the device (dvb?.frontend?, for example)
        """
        return self._dvb_dev_list.sysname.decode()

    @property
    def dvb_type(self) -> DVBDevType:
        """
        Type of the DVB device, as defined by enum dvb_dev_type
        """
        return DVBDevType(self._dvb_dev_list.dvb_type)

    @property
    def bus_addr(self) -> str:
        """
        Address of the device at the bus. For USB devices, it will be like: usb:3-1.1.4;
        for PCI devices:pci:0000:01:00.0)
        """
        return self._dvb_dev_list.bus_addr.decode()

    @property
    def bus_id(self) -> str:
        """
        Id of the device at the bus (optional, PCI ID or USB ID)
        """
        return self._dvb_dev_list.bus_id.decode()

    @property
    def manufacturer(self) -> str:
        """
        Device's manufacturer name (optional, only on USB)
        """
        return self._dvb_dev_list.manufacturer.decode()

    @property
    def product(self) -> str:
        """
        Device's product name (optional, only on USB)
        """
        return self._dvb_dev_list.product.decode()

    @property
    def serial(self) -> str:
        """
        Device's serial name (optional, only on USB)
        """
        return self._dvb_dev_list.serial.decode()


class DVBOpenDescriptor(object):
    def __init__(self, struct: c_dvb_open_descriptor=None):
        self._dvb_open_descriptor: c_dvb_open_descriptor = None
        if struct is not None:
            self._dvb_open_descriptor = struct

    def __del__(self):
        libdvbv5.dvb_dev_close(self.C_POINTER)

    @property
    def C_POINTER(self) -> POINTER(c_dvb_open_descriptor):
        return byref(self._dvb_open_descriptor)


class DVBDevice(object):
    """
    Digital TV list of devices
    """
    def __init__(self, struct: c_dvb_device=None):
        self._dvb_device: c_dvb_device = struct
        if self._dvb_device is None:
            c_dvb_dev_alloc = libdvbv5.dvb_dev_alloc
            c_dvb_dev_alloc.restype = POINTER(c_dvb_device)
            dvb: POINTER(c_dvb_device) = c_dvb_dev_alloc()
            self._dvb_device = dvb.contents

    def __del__(self):
        libdvbv5.dvb_dev_free(self.C_POINTER)

    @property
    def C_POINTER(self) -> POINTER(c_dvb_device):
        return byref(self._dvb_device)

    @property
    def devices(self) -> List[DVBDevList]:
        """
        List with a dvb_dev_list of devices. Each device node is a different entry at the list.
        """
        return [DVBDevList(self._dvb_device.devices[d]) for d in range(0, self.num_devices)]

    @property
    def num_devices(self) -> int:
        """
        Number of elements at the devices array.
        """
        return self._dvb_device.num_devices

    @property
    def fe_parms(self) -> dvb_fe.DVBv5FEParms:
        return dvb_fe.DVBv5FEParms(self._dvb_device.fe_parms.contents)


def dvb_dev_find(dvb: DVBDevice, handler: Callable[[str, DVBDevChangeType, c_void_p], int] = None,
                 user_priv: c_void_p = None) -> DVBDevice:
    """
    Finds all DVB devices on the local machine
    :param dvb: DVBDevice object to be filled
    :param user_priv: Pointer to user private data
    :return: DVBDevice

    This routine can be called on two modes: normal or monitor mode

    In normal mode, it will seek for the local Digital TV devices, store them
    at the DVBDevice object and return.

    In monitor mode, it will not only enumerate all devices, but it will also
    keep waiting for device changes. The device seek loop will only be
    interrupted after calling dvb_dev_stop_monitor().

    Please notice that, in such mode, the function will wait forever. So, it
    is up to the application to put start a separate thread to handle it in
    monitor mode, and add the needed mutexes to make it thread safe.
    """
    @CFUNCTYPE(c_int, c_char_p, c_int, c_void_p)
    def _handler(sysname: str, change_type: DVBDevChangeType, priv: c_void_p) -> int:
        return handler(sysname, change_type, priv)

    ret = libdvbv5.dvb_dev_find(dvb.C_POINTER, _handler if handler is not None else None, user_priv)
    if ret:
        raise Exception("Find DVB device unsuccessful!")
    return dvb


def dvb_dev_seek_by_adapter(dvb: DVBDevice, adapter: int, num: int, dvb_type: DVBDevType) -> DVBDevList:
    """
    Find a device that matches the search criteria given by this functions's parameters.
    :param dvb: DVBDevice object to be used
    :param adapter: Adapter number, as defined internally at the Kernel. Always start with 0
    :param num: Digital TV device number (e. g. frontend0, net0, etc)
    :param dvb_type: Type of the device, as given by enum DVBDevType
    :return: DVBDevList object or None if the desired device was not found
    """
    c_dvb_dev_seek_by_adapter = libdvbv5.dvb_dev_seek_by_adapter
    c_dvb_dev_seek_by_adapter.restype = POINTER(c_dvb_dev_list)
    p_device: POINTER(c_dvb_dev_list) = c_dvb_dev_seek_by_adapter(dvb.C_POINTER, adapter, num, dvb_type)
    if not p_device:
        return None
    return DVBDevList(p_device.contents)


def dvb_get_dev_info(dvb: DVBDevice, sysname: str) -> DVBDevList:
    """
    Return data about a device from its sysname
    :param dvb: DVBDevice object to be used
    :param sysname: Kernel's name of the device to be opened, as obtained via dvb_dev_seek_by_adapter()
    or via dvb_dev_find().
    :return: DVBDevList object or None if the desired device was not found
    """
    c_dvb_get_dev_info = libdvbv5.dvb_get_dev_info
    c_dvb_get_dev_info.restype = POINTER(c_dvb_dev_list)
    p_device: POINTER(c_dvb_dev_list) = c_dvb_get_dev_info(dvb.C_POINTER, sysname.encode())
    if not p_device:
        return None
    return DVBDevList(p_device.contents)


def dvb_dev_set_log(dvb: DVBDevice, verbose: int, logfunc=None) -> None:
    """
    Sets the DVB verbosity and log function
    :param dvb: DVBDevice object to be used
    :param verbose: Verbosity level of the messages that will be printed
    :param logfunc: Callback function to be called when a log event happens. Can either store the event into a file
    or to print it at the TUI/GUI. Can be None.

    Sets the function to report log errors and to set the verbosity level of debug report messages. If not called,
    or if logfunc is None, the libdvbv5 will report error and debug messages via stderr, and will use colors for
    the debug messages.
    """
    return libdvbv5.dvb_dev_set_log(dvb.C_POINTER, verbose, logfunc)


def dvb_dev_open(dvb: DVBDevice, sysname: str, flags: int) -> DVBOpenDescriptor:
    """
    Opens a dvb device
    :param dvb: DVBDevice object to be used
    :param sysname: Kernel's name of the device to be opened, as obtained via dvb_dev_seek_by_adapter()
    or via dvb_dev_find().
    :param flags: Flags to be passed to open: O_RDONLY, O_RDWR and/or O_NONBLOCK
    :return: DVBOpenDescriptor object that should be used on further calls if success

    This function is equivalent to open(2) system call: it opens a Digital TV given by the dev parameter, using the
    flags.

    Please notice that O_NONBLOCK is not supported for frontend devices, and will be silently ignored.

    The sysname will only work if a previous call to dvb_dev_find() is issued.
    """
    c_dvb_dev_open = libdvbv5.dvb_dev_open
    c_dvb_dev_open.restype = POINTER(c_dvb_open_descriptor)
    _d = c_dvb_dev_open(dvb.C_POINTER, sysname.encode(), flags)
    if not _d:
        raise Exception(f"Failed to open ({sysname}) dvb device!")
    return DVBOpenDescriptor(_d.contents)


def dvb_dev_close(open_dev: DVBOpenDescriptor) -> None:
    """
    Closes a dvb device
    :param open_dev: DVBOpenDescriptor object to be closed
    :return:
    """
    libdvbv5.dvb_dev_close(open_dev.C_POINTER)


def dvb_dev_set_bufsize(open_dev: DVBOpenDescriptor, buffersize: int) -> None:
    """
    Start a demux or dvr buffer size
    :param open_dev: DVBOpenDescriptor object
    :param buffersize: Size of the buffer to be allocated to store the filtered data.

    This is a wrapper function for DMX_SET_BUFFER_SIZE ioctl.

    See http://linuxtv.org/downloads/v4l-dvb-apis/dvb_demux.html for more details.

    valid only for DVB_DEVICE_DEMUX or DVB_DEVICE_DVR.
    """
    ret = libdvbv5.dvb_dev_set_bufsize(open_dev.C_POINTER, buffersize)
    if ret < 0:
        raise Exception("Failed to set buffer size!")


def dvb_dev_dmx_set_pesfilter(open_dev: DVBOpenDescriptor, pid: int, pes_type: dmx.dmx_ts_pes,
                              output: dmx.dmx_output, buffersize: int) -> None:
    """
    Start a filter for a MPEG-TS Packetized Elementary Stream (PES)
    :param open_dev: DVBOpenDescriptor object
    :param pid: Program ID to filter. Use 0x2000 to select all PIDs
    :param pes_type: type of the PID (DMX_PES_VIDEO, DMX_PES_AUDIO, DMX_PES_OTHER, etc).
    :param output: Where the data will be output (DMX_OUT_TS_TAP, DMX_OUT_DECODER, etc).
    :param buffersize: Size of the buffer to be allocated to store the filtered data.

    This is a wrapper function for DMX_SET_PES_FILTER and DMX_SET_BUFFER_SIZE ioctls.

    See http://linuxtv.org/downloads/v4l-dvb-apis/dvb_demux.html for more details.

    valid only for DVB_DEVICE_DEMUX.
    """
    ret = libdvbv5.dvb_dev_dmx_set_pesfilter(open_dev.C_POINTER, pid, pes_type, output, buffersize)
    if ret < 0:
        raise Exception("Failed to start filter!")


def dvb_dev_dmx_get_pmt_pid(open_dev: DVBOpenDescriptor, sid: int) -> int:
    """
    Read the contents of the MPEG-TS PAT table, seeking for an specific service ID
    :param open_dev: DVBOpenDescriptor object
    :param sid: Session ID to seeking
    :return: PID associated with the desired Session ID.

    This function currently assumes that the PAT fits into one session.

    Valid only for DVB_DEVICE_DEMUX.
    """
    ret = libdvbv5.dvb_dev_dmx_get_pmt_pid(open_dev.C_POINTER, sid)
    if ret < 0:
        raise Exception("Error!")
    return ret


def dvb_dev_scan(open_dev: DVBOpenDescriptor, entry: dvb_file.DVBEntry,
                 check_frontend: Callable[[Any, dvb_fe.DVBv5FEParms], int], args: Any,
                 other_nit: int, timeout_multiply: int) -> dvb_scan.DVBv5Descriptors:
    """
    Scans a DVB dvb_add_scaned_transponder
    :param open_dev:
    :param entry: DVB file entry that corresponds to a transponder to be tuned
    :param check_frontend: Callback function that will show the frontend status while tuning into a transponder
    :param args: Arguments that will be used when calling check_frontend. It should contain any parameters that
    could be needed by check_frontend.
    :param other_nit: Use alternate table IDs for NIT and other tables
    :param timeout_multiply: Improves the timeout for each table reception, by

    This is the function that applications should use when doing a transponders scan. It does everything needed to fill
    the entries with DVB programs (virtual channels) and detect the PIDs associated with them.

    This is the dvb_device variant of dvb_scan_transponder().
    """
    @CFUNCTYPE(c_int, py_object, POINTER(dvb_fe.c_dvb_v5_fe_parms))
    def _check_frontend(args: Any, parms: POINTER(dvb_fe.c_dvb_v5_fe_parms)) -> int:
        _p = dvb_fe.DVBv5FEParms(parms.contents)
        return check_frontend(args, _p)

    c_dvb_dev_scan = libdvbv5.dvb_dev_scan
    c_dvb_dev_scan.restype = POINTER(dvb_scan.c_dvb_v5_descriptors)
    res = c_dvb_dev_scan(open_dev.C_POINTER, entry.C_POINTER, _check_frontend if check_frontend is not None else None,
                         py_object(args), other_nit, timeout_multiply)
    if res:
        return dvb_scan.DVBv5Descriptors(res.contents)
    return None


def dvb_dev_remote_init(d: DVBDevice, server: str, port: int) -> int:
    """
    Initialize the dvb-dev to use a remote device running the dvbv5-daemon.
    :param d: DVBDevice object to use
    :param server: Server hostname or address
    :param port: Server port

    The protocol between the dvbv5-daemon and the dvb_dev library is highly experimental and is subject to changes in
    a near future. So, while this is not stable enough, you will only work if both the client and the server are
    running the same version of the v4l-utils library.

    Will return -1 if the function call not available
    """
    try:
        return libdvbv5.dvb_dev_remote_init(d.C_POINTER, server.encode(), port)
    except OSError:     # If HAVE_DVBV5_REMOTE = 0
        return -1
