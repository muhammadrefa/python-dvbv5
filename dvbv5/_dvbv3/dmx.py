# Ported from DVBv3 API

import enum

from ctypes import Structure
from ctypes import c_int32, c_uint32


DMX_FILTER_SIZE = 16


class c_dmx_buffer(Structure):
    """
    dmx buffer info

    Contains data exchanged by appplication and driver using one of the streaming I/O methods

    Please notice that, for &DMX_QBUF, only @index should be filled.
    On &DMX_DQBUF calls, all fields will be field by the Kernel.
    """
    _fields_ = [
        ('index', c_uint32),
        ('bytesused', c_uint32),
        ('offset', c_uint32),
        ('length', c_uint32),
        ('flags', c_uint32),
        ('count', c_uint32),
    ]


class c_dmx_requestbuffers(Structure):
    """
    request dmx buffer information

    Contains data used for requesting a dmx buffer.
    All reserved fields must be set to zero.
    """
    _fields_ = [
        ('count', c_uint32),
        ('size', c_uint32),
    ]


class c_dmx_exportbuffer(Structure):
    """
    export to dmx buffer as DMABUF file descriptor
    """
    _fields_ = [
        ('index', c_uint32),
        ('flags', c_uint32),
        ('fd', c_int32),
    ]


class dmx_output(enum.IntEnum):
    """
    Output for the demux
    """
    DMX_OUT_DECODER = 0,
    DMX_OUT_TAP = enum.auto(),
    DMX_OUT_TS_TAP = enum.auto(),
    DMX_OUT_TSDEMUX_TAP = enum.auto(),


class dmx_input(enum.IntEnum):
    """
    Input from the demux
    """
    DMX_IN_FRONTEND = 0,
    DMX_IN_DVR = enum.auto(),


class dmx_ts_pes(enum.IntEnum):
    """
    Type of the PES filter
    """
    DMX_PES_AUDIO0 = 0,
    DMX_PES_VIDEO0 = enum.auto(),
    DMX_PES_TELETEXT0 = enum.auto(),
    DMX_PES_SUBTITLE0 = enum.auto(),
    DMX_PES_PCR0 = enum.auto(),

    DMX_PES_AUDIO1 = enum.auto(),
    DMX_PES_VIDEO1 = enum.auto(),
    DMX_PES_TELETEXT1 = enum.auto(),
    DMX_PES_SUBTITLE1 = enum.auto(),
    DMX_PES_PCR1 = enum.auto(),

    DMX_PES_AUDIO2 = enum.auto(),
    DMX_PES_VIDEO2 = enum.auto(),
    DMX_PES_TELETEXT2 = enum.auto(),
    DMX_PES_SUBTITLE2 = enum.auto(),
    DMX_PES_PCR2 = enum.auto(),

    DMX_PES_AUDIO3 = enum.auto(),
    DMX_PES_VIDEO3 = enum.auto(),
    DMX_PES_TELETEXT3 = enum.auto(),
    DMX_PES_SUBTITLE3 = enum.auto(),
    DMX_PES_PCR3 = enum.auto(),

    DMX_PES_OTHER = enum.auto(),


DMX_PES_AUDIO = dmx_ts_pes.DMX_PES_AUDIO0
DMX_PES_VIDEO = dmx_ts_pes.DMX_PES_VIDEO0
DMX_PES_TELETEXT = dmx_ts_pes.DMX_PES_TELETEXT0
DMX_PES_SUBTITLE = dmx_ts_pes.DMX_PES_SUBTITLE0
DMX_PES_PCR = dmx_ts_pes.DMX_PES_PCR0


class dmx_buffer_flags(enum.IntFlag):
    DMX_BUFFER_FLAG_HAD_CRC32_DISCARD = 1 << 0,
    DMX_BUFFER_FLAG_TEI = 1 << 1,
    DMX_BUFFER_PKT_COUNTER_MISMATCH = 1 << 2,
    DMX_BUFFER_FLAG_DISCONTINUITY_DETECTED = 1 << 3,
    DMX_BUFFER_FLAG_DISCONTINUITY_INDICATOR = 1 << 4,
