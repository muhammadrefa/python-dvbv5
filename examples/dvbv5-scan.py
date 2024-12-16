#!/usr/bin/env python3

"""
dvbv5-scan.py

Frequency scanning tool ported from dvbv5-scan
This example utilises DVBv5 class
"""

import os
import time

from dvbv5 import dvb_v5_std, dvb_frontend, dvb_fe, dvb_file, dvb_dev
from dvbv5.DVBv5 import DVBv5


def check_frontend(args, parms: dvb_fe.DVBv5FEParms):
    status = dvb_frontend.FEStatus.FE_NONE
    timeout_cnt = 0
    while timeout_cnt < (40 * args['timeout_multiply']):
        if parms.abort:
            return 0

        try:
            dvb_fe.dvb_fe_get_stats(parms)
        except:
            print("ERROR: get stats failed!")

        try:
            status = dvb_fe.dvb_fe_retrieve_stats(parms, dvb_v5_std.DTVStatPropertyCommand.DTV_STATUS)
        except:
            pass

        if status & dvb_frontend.FEStatus.FE_HAS_LOCK:
            break

        time.sleep(1)
        timeout_cnt += 1

    return 0 if status & dvb_frontend.FEStatus.FE_HAS_LOCK else -1


def run_scan(dvb: DVBv5, demux_dev: dvb_dev.DVBDevList, confpath: str, timeout_multiply: int = 1):
    parms: dvb_fe.DVBv5FEParms = dvb.fe_parms

    # This is used only when reading old formats
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

    try:
        _dvb_file = dvb_file.dvb_read_file_format(confpath, sys, dvb_file.DVBFileFormat.FILE_DVBV5)
    except:
        print("Read dvb conf failed")
        return

    try:
        dmx_fd = dvb.dev_open(demux_dev, os.O_RDWR)
    except:
        print("Opening demux failed")
        return

    for entry in _dvb_file.entry:
        stream_id: int

        # TODO: This can be done by reading the dictionary
        try:
            freq = dvb_file.dvb_retrieve_entry_prop(entry, dvb_frontend.DVBv5PropertyCommand.DTV_FREQUENCY)
        except KeyError:
            continue

        print(f"Scanning frequency {freq}")

        # Run the scanning logic
        _args = {'timeout_multiply': timeout_multiply}
        dvb_scan_handler = dmx_fd.dvb_dev_scan(entry, check_frontend, _args, 0, timeout_multiply)
        if parms.abort:
            # handler table freed in destructor
            break
        if dvb_scan_handler is None:
            print("Scan error!")
            continue

        # Store the service entry
        x = dvb_file.dvb_store_channel(parms, dvb_scan_handler, 0, False)

        # handler table freed in destructor

    # demux descriptor closed in destructor


def main(confpath: str, country: str = None, timeout_multiply: int = 1, verbose: int = 0):
    dvb = DVBv5()
    dev_list = dvb.dev_find()

    try:
        dmx_dev = dvb.dev_seek_by_adapter(0, 0, dvb_dev.DVBDevType.DVB_DEVICE_DEMUX)
        if verbose:
            print(f"Using demux {dmx_dev.sysname}")
    except:
        print("Couldn't find demux device node")
        return

    try:
        fe_dev = dvb.dev_seek_by_adapter(0, 0, dvb_dev.DVBDevType.DVB_DEVICE_FRONTEND)
    except:
        print("Couldn't find frontend device node")
        return

    try:
        # Store return value to prevent error
        fe_fd = dvb.dev_open(fe_dev, os.O_RDWR)
    except:
        print("Couldn't open frontend device node")
        return

    try:
        dvb.fe_set_default_country(country)
    except ValueError:
        print(f"Failed to set the country code:{country}")

    run_scan(dvb, dmx_dev, confpath, timeout_multiply)


if __name__ == "__main__":
    confpath: str = "/path/to/DVBV5/channel/file"
    country: str = None     # ISO 3166-1 two letter code
    timeout_multiply = 1
    verbose = 0
    main(confpath, country, timeout_multiply, verbose)
