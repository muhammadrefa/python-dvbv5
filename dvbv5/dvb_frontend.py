import enum

from ctypes import Structure, Union
from ctypes import c_void_p
from ctypes import c_char, c_int, c_uint8, c_uint32, c_uint64, c_int64


MAX_DTV_STATS = 4


class c_dvb_frontend_info(Structure):
    _fields_ = [
        ('name', c_char * 128),
        ('type', c_int),
        ('frequency_min', c_uint32),
        ('frequency_max', c_uint32),
        ('frequency_stepsize', c_uint32),
        ('frequency_tolerance', c_uint32),
        ('symbol_rate_min', c_uint32),
        ('symbol_rate_max', c_uint32),
        ('symbol_rate_tolerance', c_uint32),
        ('notifier_delay', c_uint32),
        ('caps', c_int),
    ]


class FECaps(enum.IntEnum):
    """
    Frontend capabilities
    """
    FE_IS_STUPID = 0,
    """
    There's something wrong at the frontend, and it can't report its capabilities.
    """
    FE_CAN_INVERSION_AUTO = 0x1,
    """
    Can auto-detect frequency spectral band inversion
    """
    FE_CAN_FEC_1_2 = 0x2,
    FE_CAN_FEC_2_3 = 0x4,
    FE_CAN_FEC_3_4 = 0x8,
    FE_CAN_FEC_4_5 = 0x10,
    FE_CAN_FEC_5_6 = 0x20,
    FE_CAN_FEC_6_7 = 0x40,
    FE_CAN_FEC_7_8 = 0x80,
    FE_CAN_FEC_8_9 = 0x100,
    FE_CAN_FEC_AUTO = 0x200,
    FE_CAN_QPSK = 0x400,
    FE_CAN_QAM_16 = 0x800,
    FE_CAN_QAM_32 = 0x1000,
    FE_CAN_QAM_64 = 0x2000,
    FE_CAN_QAM_128 = 0x4000,
    FE_CAN_QAM_256 = 0x8000,
    FE_CAN_QAM_AUTO = 0x10000,
    FE_CAN_TRANSMISSION_MODE_AUTO = 0x20000,
    FE_CAN_BANDWIDTH_AUTO = 0x40000,
    FE_CAN_GUARD_INTERVAL_AUTO = 0x80000,
    FE_CAN_HIERARCHY_AUTO = 0x100000,
    FE_CAN_8VSB = 0x200000,
    FE_CAN_16VSB = 0x400000,
    FE_HAS_EXTENDED_CAPS = 0x800000,
    """
    Unused
    """
    FE_CAN_MULTISTREAM = 0x4000000,
    FE_CAN_TURBO_FEC = 0x8000000,
    FE_CAN_2G_MODULATION = 0x10000000,
    """
    Supports "2nd generation" modulation, e. g. DVB-S2, DVB-T2, DVB-C2
    """
    FE_NEEDS_BENDING = 0x20000000,
    """
    Unused
    """
    FE_CAN_RECOVER = 0x40000000,
    """
    Can recover from a cable unplug automatically
    """
    FE_CAN_MUTE_TS = 0x80000000,
    """
    Can stop spurious TS data output
    """


class FEType(enum.IntEnum):
    """
    DEPRECATED: Should be kept just due to backward compatibility.
    """
    FE_QPSK = 0,
    FE_QAM = enum.auto(),
    FE_OFDM = enum.auto(),
    FE_ATSC = enum.auto()


class FEStatus(enum.IntFlag):
    """
    Enumerates the possible frontend status.
    """
    FE_NONE = 0x00,
    FE_HAS_SIGNAL = 0x01,
    FE_HAS_CARRIER = 0x02,
    FE_HAS_VITERBI = 0x04,
    FE_HAS_SYNC = 0x08,
    FE_HAS_LOCK = 0x10,
    FE_TIMEDOUT = 0x20,
    FE_REINIT = 0x40,


class DVBv5PropertyCommand(enum.IntEnum):
    """
    DVBv5 property Commands
    """
    DTV_UNDEFINED = 0,
    DTV_TUNE = 1,
    DTV_CLEAR = 2,
    DTV_FREQUENCY = 3,
    DTV_MODULATION = 4,
    DTV_BANDWIDTH_H = 5,
    DTV_INVERSION = 6,
    DTV_DISEQC_MASTER = 7,
    DTV_SYMBOL_RATE = 8,
    DTV_INNER_FEC = 9,
    DTV_VOLTAGE	 = 10,
    DTV_TONE	 = 11,
    DTV_PILOT	 = 12,
    DTV_ROLLOFF	 = 13,
    DTV_DISEQC_SLAVE_REPLY = 14,

    # Basic enumeration set for querying unlimited capabilities
    DTV_FE_CAPABILITY_COUNT = 15,
    DTV_FE_CAPABILITY = 16,
    DTV_DELIVERY_SYSTEM = 17,

    # ISDB-T and ISDB-Tsb
    DTV_ISDBT_PARTIAL_RECEPTION = 18,
    DTV_ISDBT_SOUND_BROADCASTING = 19,

    DTV_ISDBT_SB_SUBCHANNEL_ID = 20,
    DTV_ISDBT_SB_SEGMENT_IDX = 21,
    DTV_ISDBT_SB_SEGMENT_COUNT = 22,

    DTV_ISDBT_LAYERA_FEC	 = 23,
    DTV_ISDBT_LAYERA_MODULATION = 24,
    DTV_ISDBT_LAYERA_SEGMENT_COUNT = 25,
    DTV_ISDBT_LAYERA_TIME_INTERLEAVING = 26,

    DTV_ISDBT_LAYERB_FEC	 = 27,
    DTV_ISDBT_LAYERB_MODULATION = 28,
    DTV_ISDBT_LAYERB_SEGMENT_COUNT = 29,
    DTV_ISDBT_LAYERB_TIME_INTERLEAVING = 30,

    DTV_ISDBT_LAYERC_FEC	 = 31,
    DTV_ISDBT_LAYERC_MODULATION = 32,
    DTV_ISDBT_LAYERC_SEGMENT_COUNT = 33,
    DTV_ISDBT_LAYERC_TIME_INTERLEAVING = 34,

    DTV_API_VERSION = 35,

    DTV_CODE_RATE_HP = 36,
    DTV_CODE_RATE_LP = 37,
    DTV_GUARD_INTERVAL = 38,
    DTV_TRANSMISSION_MODE = 39,
    DTV_HIERARCHY = 40,

    DTV_ISDBT_LAYER_ENABLE = 41,

    DTV_STREAM_ID = 42,
    DTV_ISDBS_TS_ID_LEGACY = 42,
    DTV_DVBT2_PLP_ID_LEGACY = 43,

    DTV_ENUM_DELSYS = 44,

    # ATSC-MH
    DTV_ATSCMH_FIC_VER	 = 45,
    DTV_ATSCMH_PARADE_ID	 = 46,
    DTV_ATSCMH_NOG		 = 47,
    DTV_ATSCMH_TNOG		 = 48,
    DTV_ATSCMH_SGN		 = 49,
    DTV_ATSCMH_PRC		 = 50,
    DTV_ATSCMH_RS_FRAME_MODE = 51,
    DTV_ATSCMH_RS_FRAME_ENSEMBLE = 52,
    DTV_ATSCMH_RS_CODE_MODE_PRI = 53,
    DTV_ATSCMH_RS_CODE_MODE_SEC = 54,
    DTV_ATSCMH_SCCC_BLOCK_MODE = 55,
    DTV_ATSCMH_SCCC_CODE_MODE_A = 56,
    DTV_ATSCMH_SCCC_CODE_MODE_B = 57,
    DTV_ATSCMH_SCCC_CODE_MODE_C = 58,
    DTV_ATSCMH_SCCC_CODE_MODE_D = 59,

    DTV_INTERLEAVING = 60,
    DTV_LNA		 = 61,

    # Quality parameters
    DTV_STAT_SIGNAL_STRENGTH = 62,
    DTV_STAT_CNR		 = 63,
    DTV_STAT_PRE_ERROR_BIT_COUNT = 64,
    DTV_STAT_PRE_TOTAL_BIT_COUNT = 65,
    DTV_STAT_POST_ERROR_BIT_COUNT = 66,
    DTV_STAT_POST_TOTAL_BIT_COUNT = 67,
    DTV_STAT_ERROR_BLOCK_COUNT = 68,
    DTV_STAT_TOTAL_BLOCK_COUNT = 69,

    # Physical layer scrambling
    DTV_SCRAMBLING_SEQUENCE_INDEX = 70,


DTV_MAX_COMMAND = DVBv5PropertyCommand.DTV_SCRAMBLING_SEQUENCE_INDEX


class FEDeliverySystem(enum.IntEnum):
    """
    Type of the delivery system
    """
    SYS_UNDEFINED = 0,
    """
    Undefined standard. Generally, indicates an error
    """
    SYS_DVBC_ANNEX_A = enum.auto(),
    """
    Cable TV: DVB-C following ITU-T J.83 Annex A spec
    """
    SYS_DVBC_ANNEX_B = enum.auto(),
    """
    Cable TV: DVB-C following ITU-T J.83 Annex B spec (ClearQAM)
    """
    SYS_DVBT = enum.auto(),
    SYS_DSS = enum.auto(),
    """
    Satellite TV: DSS (not fully supported)
    """
    SYS_DVBS = enum.auto(),
    SYS_DVBS2 = enum.auto(),
    SYS_DVBH = enum.auto(),
    """
    Terrestrial TV (mobile): DVB-H (standard deprecated)
    """
    SYS_ISDBT = enum.auto(),
    SYS_ISDBS = enum.auto(),
    SYS_ISDBC = enum.auto(),
    """
    Cable TV: ISDB-C (no drivers yet)
    """
    SYS_ATSC = enum.auto(),
    SYS_ATSCMH = enum.auto(),
    SYS_DTMB = enum.auto(),
    SYS_CMMB = enum.auto(),
    """
    Terrestrial TV (mobile): CMMB (not fully supported)
    """
    SYS_DAB = enum.auto(),
    """
    Digital audio: DAB (not fully supported)
    """
    SYS_DVBT2 = enum.auto(),
    SYS_TURBO = enum.auto(),
    SYS_DVBC_ANNEX_C = enum.auto(),
    """
    Cable TV: DVB-C following ITU-T J.83 Annex C spec
    """
    SYS_DVBC2 = enum.auto(),

    # Backward compatibility
    SYS_DVBC_ANNEX_AC = 1,      # SYS_DVBC_ANNEX_A
    SYS_DTMBH = 13,             # SYS_DTMB


class c_dtv_stats(Structure):
    class _c_u(Union):
        __fields__ = [
            ('uvalue', c_uint64),
            ('svalue', c_int64)
        ]

    _pack_ = 1
    __fields__ = [
        ('scale', c_uint8),
        ('_u', _c_u)
    ]


class c_dtv_fe_stats(Structure):
    _pack_ = 1
    __fields__ = [
        ('len', c_uint8),
        ('stat', c_dtv_stats * MAX_DTV_STATS)  # !!
    ]


class c_dtv_property(Structure):
    class _c_u(Union):
        class _c_buffer(Structure):
            _fields_ = [
                ('data', c_uint8 * 32),
                ('len', c_uint32),
                ('reserved1', c_uint32 * 3),
                ('reserved2', c_void_p)
            ]

        _fields_ = [
            ('data', c_uint32),
            ('st', c_dtv_fe_stats),
            ('buffer', _c_buffer)
        ]

    _pack_ = 1
    _fields_ = [
        ('cmd', c_uint32),
        ('reserved', c_uint32 * 3),
        ('u', _c_u),
        ('result', c_int)
    ]
