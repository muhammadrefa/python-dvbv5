import os
import time

from dvbv5 import dvb_v5_std, dvb_frontend, dvb_fe, dvb_file, dvb_dev
from dvbv5.dvb_dev import dmx

# Use a buffer big enough at least 1 second of data. It is interesting to have it multiple of a page.
# So, define it as a multiply of 4096.
DVB_BUF_SIZE = (4096 * 8 * 188)


def parse(parms: dvb_fe.DVBv5FEParms, confpath: str, freq: int = None, channel: str = None, **kwargs):
    # print(f"freq {freq} channel {channel}")

    dvr = False
    if 'dvr' in kwargs:
        dvr = kwargs.get('dvr')

    # Used only when reading old formats
    if parms.current_sys in [dvb_frontend.FEDeliverySystem.SYS_DVBT, dvb_frontend.FEDeliverySystem.SYS_DVBS,
                             dvb_frontend.FEDeliverySystem.SYS_DVBC_ANNEX_A, dvb_frontend.FEDeliverySystem.SYS_ATSC]:
        sys = parms.current_sys
    elif parms.current_sys == dvb_frontend.FEDeliverySystem.SYS_DVBC_ANNEX_C:
        sys = dvb_frontend.FEDeliverySystem.SYS_DVBC_ANNEX_A
    elif parms.current_sys == dvb_frontend.FEDeliverySystem.SYS_DVBC_ANNEX_B:
        sys = dvb_frontend.FEDeliverySystem.SYS_ATSC
    elif parms.current_sys in [dvb_frontend.FEDeliverySystem.SYS_ISDBT, dvb_frontend.FEDeliverySystem.SYS_DTMB]:
        sys = dvb_frontend.FEDeliverySystem.SYS_DVBT
    else:
        sys = dvb_frontend.FEDeliverySystem.SYS_UNDEFINED

    _dvb_file = dvb_file.dvb_read_file_format(confpath, sys, kwargs.get('input_format'))

    entry = None
    for _entry in _dvb_file.entry:
        if _entry.channel and _entry.channel == channel:
            entry = _entry
            print("channel found!")
            break
        if _entry.vchannel and _entry.vchannel == channel:
            entry = _entry
            print("(v)channel found!")
            break

    # Give a second shot, using a case insensitive seek
    if entry is None and channel is not None:
        for _entry in _dvb_file.entry:
            if _entry.channel and _entry.channel.lower() == channel.lower():
                entry = _entry
                print("channel found! (case insensitive)")
                break

    # When this tool is used to just tune to a channel, to monitor it or to capture all PIDs,
    # all it needs is a frequency.
    # So, let the tool to accept a frequency as the tuning channel on those cases.
    # This way, a file in "channel" format can be used instead of a zap file.
    # It is also easier to use it for testing purposes.

    if (entry is None) and (freq is not None) and (not dvr):
        for _entry in _dvb_file.entry:
            f = dvb_file.dvb_retrieve_entry_prop(_entry, dvb_frontend.DVBv5PropertyCommand.DTV_FREQUENCY)
            if f == freq:
                entry = _entry
                print(f"frequency found!")
                break

    if entry is None:
        raise Exception("Can't find channel!")

    # Set the delivery system
    system = dvb_file.dvb_retrieve_entry_prop(entry, dvb_frontend.DVBv5PropertyCommand.DTV_DELIVERY_SYSTEM)
    dvb_fe.dvb_set_compat_delivery_system(parms, system)

    # Copy data into parms
    for k in entry.props:
        if k == dvb_frontend.DVBv5PropertyCommand.DTV_DELIVERY_SYSTEM:
            continue
        dvb_fe.dvb_fe_store_parm(parms, k, entry.props[k])

    return entry


def print_frontend_stats(parms: dvb_fe.DVBv5FEParms):
    try:
        dvb_fe.dvb_fe_get_stats(parms)
    except:
        print(f"get stats failed!")
        return -1

    val = dvb_fe.dvb_fe_retrieve_stats(parms, dvb_v5_std.DTVStatPropertyCommand.DTV_STATUS)
    str_status = ""
    if val & dvb_frontend.FEStatus.FE_HAS_LOCK:
        str_status += " lock"
    if val & dvb_frontend.FEStatus.FE_TIMEDOUT:
        str_status += " timedout"
    print(f"DTV status: {hex(val)}{str_status}")


def get_show_stats(parms: dvb_fe.DVBv5FEParms):
    try:
        dvb_fe.dvb_fe_get_stats(parms)
    except:
        return -1
    print_frontend_stats(parms)


def check_frontend(args, parms: dvb_fe.DVBv5FEParms):
    status = dvb_frontend.FEStatus.FE_NONE
    timeout_cnt = 0
    while True:
        try:
            dvb_fe.dvb_fe_get_stats(parms)
        except:
            # print("get stats failed!")
            time.sleep(1)
            continue

        status = dvb_frontend.FEStatus.FE_NONE
        try:
            status = dvb_fe.dvb_fe_retrieve_stats(parms, dvb_v5_std.DTVStatPropertyCommand.DTV_STATUS)
        except:
            # print("retrieve stats failed")
            time.sleep(1)
            continue

        if status & dvb_frontend.FEStatus.FE_HAS_LOCK:
            break

        time.sleep(1)
        timeout_cnt += 1

    return status & dvb_frontend.FEStatus.FE_HAS_LOCK


def setup_frontend(parms: dvb_fe.DVBv5FEParms):
    try:
        freq = dvb_fe.dvb_fe_retrieve_parm(parms, dvb_frontend.DVBv5PropertyCommand.DTV_FREQUENCY)
    except ValueError:
        print("Error getting frequency!")
        return -1
    print(f"tuning to {freq}")

    try:
        dvb_fe.dvb_fe_set_parms(parms)
    except ValueError:
        print("Set parms failed!")
        return -1


def main(confpath: str, country: str = None, timeout_multiply: int = 1, verbose: int = 0, *args, **kwargs):
    freq = None
    if 'freq' in kwargs:
        freq = kwargs.get('freq')

    channel = None
    if 'channel' in kwargs:
        channel = kwargs.get('channel')

    input_format = dvb_file.DVBFileFormat.FILE_DVBV5
    if 'input_format' in kwargs:
        input_format = kwargs.get('input_format')

    dvr = False
    if 'dvr' in kwargs:
        dvr = kwargs.get('dvr')

    dvb = dvb_dev.DVBDevice()
    dvb = dvb_dev.dvb_dev_find(dvb)

    dmx_dev = dvb_dev.dvb_dev_seek_by_adapter(dvb, 0, 0, dvb_dev.DVBDevType.DVB_DEVICE_DEMUX)
    if dmx_dev is None:
        print("Couldn't find demux device node")
        return -1
    demux_sysname = dmx_dev.sysname
    print(f"using demux {demux_sysname}")

    dvr_dev = dvb_dev.dvb_dev_seek_by_adapter(dvb, 0, 0, dvb_dev.DVBDevType.DVB_DEVICE_DVR)
    if dvr_dev is None:
        print("Couldn't find dvr device node")
        return -1
    print(f"using dvr {dvr_dev.sysname}")

    fe_dev = dvb_dev.dvb_dev_seek_by_adapter(dvb, 0, 0, dvb_dev.DVBDevType.DVB_DEVICE_FRONTEND)
    if fe_dev is None:
        print("Couldn't find frontend device node")
        return -1
    print(f"using frontend {fe_dev.sysname}")

    x = dvb_dev.dvb_dev_open(dvb, fe_dev.sysname, os.O_RDWR)
    if x is None:
        print("Error!")
        return

    try:
        dvb_fe.dvb_fe_set_default_country(dvb.fe_parms, country)
    except ValueError:
        print(f"Failed to set the country code:{country}")

    dvb_entry = parse(dvb.fe_parms, confpath, freq=freq, channel=channel, input_format=input_format, dvr=dvr)
    if setup_frontend(dvb.fe_parms):
        return -1

    if 'all_pids' in kwargs and kwargs.get('all_pids'):
        video_fd = dvb_dev.dvb_dev_open(dvb, dmx_dev.sysname, os.O_RDWR)

        print(f"buffer set to {DVB_BUF_SIZE}")
        dvb_dev.dvb_dev_set_bufsize(video_fd, DVB_BUF_SIZE)

        print("pass all PIDs to TS")

        dvb_dev.dvb_dev_dmx_set_pesfilter(video_fd, 0x2000, dmx.dmx_ts_pes.DMX_PES_OTHER,
                                          dmx.dmx_output.DMX_OUT_TS_TAP, 0)

    else:
        extra_pids = False
        if 'extra_pids' in kwargs:
            extra_pids = kwargs.get('extra_pids')

        if dvb_entry.video_pid:
            n_vpid = 0
            if 'n_vpid' in kwargs:
                n_vpid = kwargs.get('n_vpid')
            if n_vpid >= len(dvb_entry.video_pid):
                n_vpid = 0

            video_fd = dvb_dev.dvb_dev_open(dvb, dmx_dev.sysname, os.O_RDWR)

            print(f"buffer set to {DVB_BUF_SIZE}")
            dvb_dev.dvb_dev_set_bufsize(video_fd, DVB_BUF_SIZE)

            for i in range(0, len(dvb_entry.video_pid)):
                if (not extra_pids) and (i != n_vpid):
                    continue

                pes_type = dmx.dmx_ts_pes.DMX_PES_VIDEO0 if i == n_vpid else dmx.dmx_ts_pes.DMX_PES_OTHER
                output = dmx.dmx_output.DMX_OUT_TS_TAP if dvr else dmx.dmx_output.DMX_OUT_DECODER

                dvb_dev.dvb_dev_dmx_set_pesfilter(video_fd, dvb_entry.video_pid[i],
                                                  pes_type, output, ((1024 * 1024) if dvr else 0))

        if dvb_entry.audio_pid:
            n_apid = 0
            if 'n_apid' in kwargs:
                n_apid = kwargs.get('n_apid')
            if n_apid >= len(dvb_entry.audio_pid):
                n_apid = 0

            for i in range(0, len(dvb_entry.audio_pid)):
                if (not extra_pids) and (i != n_apid):
                    continue

                audio_fd = dvb_dev.dvb_dev_open(dvb, dmx_dev.sysname, os.O_RDWR)

                pes_type = dmx.dmx_ts_pes.DMX_PES_AUDIO0 if i == n_apid else dmx.dmx_ts_pes.DMX_PES_OTHER
                output = dmx.dmx_output.DMX_OUT_TS_TAP if dvr else dmx.dmx_output.DMX_OUT_DECODER

                dvb_dev.dvb_dev_dmx_set_pesfilter(audio_fd, dvb_entry.audio_pid[i],
                                                  pes_type, output, ((64 * 1024) if dvr else 0))

        if extra_pids and dvb_entry.other_el_pid:
            for other_el_pid in dvb_entry.other_el_pid:
                other_fd = dvb_dev.dvb_dev_open(dvb, dmx_dev.sysname, os.O_RDWR)
                print(f"other pid {other_el_pid.pid} ({other_el_pid.type})")

                output = dmx.dmx_output.DMX_OUT_TS_TAP if dvr else dmx.dmx_output.DMX_OUT_DECODER

                dvb_dev.dvb_dev_dmx_set_pesfilter(other_fd, other_el_pid.pid,
                                                  dmx.dmx_ts_pes.DMX_PES_OTHER, output, ((64 * 1024) if dvr else 0))

    _args = {}
    if not check_frontend(_args, dvb.fe_parms):
        print("frontend does not lock!")
        return

    if ('dvr' in kwargs) and kwargs.get('dvr'):
        get_show_stats(dvb.fe_parms)
        print(f"DVR interface '{dvr_dev.path}' can now be opened")
        while True:
            get_show_stats(dvb.fe_parms)
            time.sleep(1)

    try:
        while True:
            get_show_stats(dvb.fe_parms)
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"KeyboardInterrupt!")


if __name__ == "__main__":
    country: str = None     # ISO 3166-1 two letter code

    # Uncomment to tune into frequency
    # confpath: str = "/path/to/DVBV5/channel/file"
    # input_format: dvb_file.DVBFileFormat = dvb_file.DVBFileFormat.FILE_DVBV5
    # freq = 0      # frequency here
    # channel = None
    # dvr = False

    # Uncomment to tune into channel
    # confpath: str = "/path/to/DVBV5/channel/file/zap/formatted"
    # input_format: dvb_file.DVBFileFormat = dvb_file.DVBFileFormat.FILE_ZAP
    # freq = None
    # channel = "Channel name"    # channel name here
    # dvr = True

    main(confpath, country, input_format=input_format, freq=freq, channel=channel, dvr=dvr)
