"""
Provides libdvbv5 defined properties for the frontend.
"""

import enum


DTV_USER_COMMAND_START = 256


class DTVUserPropertyCommand(enum.IntEnum):
    """
    DTV properties that don't belong to Kernelspace

    Those properties contain data that comes from the MPEG-TS tables, like audio/video/other PIDs, and satellite config
    """
    DTV_POLARIZATION = (DTV_USER_COMMAND_START + 0),
    """
    Satellite polarization (for Satellite delivery systems)
    """
    DTV_VIDEO_PID = (DTV_USER_COMMAND_START + 1),
    DTV_AUDIO_PID = (DTV_USER_COMMAND_START + 2),
    DTV_SERVICE_ID = (DTV_USER_COMMAND_START + 3),
    """
    MPEG TS service ID
    """
    DTV_CH_NAME = (DTV_USER_COMMAND_START + 4),
    """
    Digital TV service name
    """
    DTV_VCHANNEL = (DTV_USER_COMMAND_START + 5),
    """
    Digital TV channel number. May contain symbols
    """
    DTV_SAT_NUMBER = (DTV_USER_COMMAND_START + 6),
    """
    Number of the satellite (used on multi-dish Satellite systems)
    """
    DTV_DISEQC_WAIT = (DTV_USER_COMMAND_START + 7),
    """
    Extra time needed to wait for DiSeqC to complete, in ms.
    The minimal wait time is 15 ms. The time here will be added to the minimal time.
    """
    DTV_DISEQC_LNB = (DTV_USER_COMMAND_START + 8),
    DTV_FREQ_BPF = (DTV_USER_COMMAND_START + 9),
    """
    SCR/Unicable band-pass filter frequency in kHz
    """
    DTV_PLS_CODE = (DTV_USER_COMMAND_START + 10),
    """
    DVB-T2 PLS code. Not used internally. It is needed only for file conversion.
    """
    DTV_PLS_MODE = (DTV_USER_COMMAND_START + 11),
    """
    DVB-T2 PLS mode. Not used internally. It is needed only for file conversion.
    """
    DTV_COUNTRY_CODE = (DTV_USER_COMMAND_START + 12),
    """
    Country variant of international delivery system standard. in ISO 3166-1 two letter code.
    """


DTV_MAX_USER_COMMAND = DTVUserPropertyCommand.DTV_COUNTRY_CODE


class DVBSatPolarization(enum.IntEnum):
    """
    Polarization types for Satellite systems
    """
    POLARIZATION_OFF = 0,
    POLARIZATION_H = 1,
    POLARIZATION_V = 2,
    POLARIZATION_L = 3,
    POLARIZATION_R = 4


DTV_STAT_COMMAND_START = 512


class DTVStatPropertyCommand(enum.IntEnum):
    """
    Those properties contain statistics measurements that aren't either provided by the Kernel via property cmd/value
    pair, like status (with has its own ioctl), or that are derivated measures from two or more Kernel reported stats.
    """
    DTV_STATUS = (DTV_STAT_COMMAND_START + 0),
    """
    Lock status of a DTV frontend. This actually comes from the Kernel, but it uses a separate ioctl.
    """
    DTV_BER = (DTV_STAT_COMMAND_START + 1),
    """
    Bit Error Rate. This is a parameter that it is derivated from two counters at the Kernel side
    """
    DTV_PER = (DTV_STAT_COMMAND_START + 2),
    """
    Packet Error Rate. This is a parameter that it is derivated from two counters at the Kernel side
    """
    DTV_QUALITY = (DTV_STAT_COMMAND_START + 3),
    """
    A quality indicator that represents if a locked channel provides a good, OK or poor signal. This is estimated
    considering the error rates, signal strength and/or S/N ratio of the carrier.
    """
    DTV_PRE_BER = (DTV_STAT_COMMAND_START + 4),
    """
    Bit Error Rate before Viterbi. This is the error rate before applying the Forward Error Correction. This is a
    parameter that it is derivated from two counters at the Kernel side.
    """


DTV_MAX_STAT_COMMAND = DTVStatPropertyCommand.DTV_PRE_BER
DTV_STAT_NAME_SIZE = (1 + DTV_MAX_STAT_COMMAND - DTV_STAT_COMMAND_START)
DTV_NUM_KERNEL_STATS = 8
DTV_NUM_STATS_PROPS = (DTV_NUM_KERNEL_STATS + DTV_STAT_NAME_SIZE)


class DVBQuality(enum.IntEnum):
    """
    Provides an estimation about the user's experience while watching to a given MPEG stream
    """
    DVB_QUAL_UNKNOWN = 0,
    """
    Quality could not be estimated, as the Kernel driver doesn't provide enough statistics
    """
    DVB_QUAL_POOR = enum.auto(),
    """
    The signal reception is poor. Signal loss or packets can be lost too frequently.
    """
    DVB_QUAL_OK = enum.auto(),
    """
    The signal reception is ok. Eventual artifacts could be expected, but it should work.
    """
    DVB_QUAL_GOOD = enum.auto(),
    """
    The signal is good, and not many errors are happening. The user should have a good experience watching the stream.
    """
