from typing import List, Callable, Any

from . import dvb_dev
from . import dvb_fe
from . import dvb_scan
from . import dvb_file


class DVBv5Descriptor(object):
    def __init__(self, fd: dvb_dev.DVBOpenDescriptor):
        self._dvb_open_descriptor: dvb_dev.DVBOpenDescriptor = fd

    def __del__(self):
        self.dvb_dev_close()

    def dvb_dev_close(self) -> None:
        """
        Closes a dvb device
        """
        if self._dvb_open_descriptor is not None:
            dvb_dev.dvb_dev_close(self._dvb_open_descriptor)
            self._dvb_open_descriptor = None

    def dvb_dev_scan(self, entry: dvb_file.DVBEntry, check_frontend: Callable[[Any, dvb_fe.DVBv5FEParms], int],
                     args: Any, other_nit: int, timeout_multiply: int) -> dvb_scan.DVBv5Descriptors:
        """
        Scans a DVB dvb_add_scaned_transponder
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
        return dvb_dev.dvb_dev_scan(self._dvb_open_descriptor, entry, check_frontend, args, other_nit, timeout_multiply)


class DVBv5(object):
    def __init__(self):
        self._dvb = dvb_dev.DVBDevice()

    @property
    def devices(self) -> List[dvb_dev.DVBDevList]:
        """
        List with a dvb_dev_list of devices. Each device node is a different entry at the list.
        """
        return self._dvb.devices

    @property
    def fe_parms(self) -> dvb_fe.DVBv5FEParms:
        return self._dvb.fe_parms

    def dev_open(self, device: dvb_dev.DVBDevList, flags: int) -> DVBv5Descriptor:
        """
        Opens a dvb device
        :param device: Device to be opened, as obtained via dvb_dev_seek_by_adapter() or via dvb_dev_find().
        :param flags: Flags to be passed to open: O_RDONLY, O_RDWR and/or O_NONBLOCK
        :return: DVBv5Descriptor
        This function is equivalent to open(2) system call: it opens a Digital TV given by the dev parameter, using the
        flags. Please notice that O_NONBLOCK is not supported for frontend devices, and will be silently ignored.

        The device will only work if a previous call to dvb_dev_find() is issued.
        """
        fd = dvb_dev.dvb_dev_open(self._dvb, device.sysname, flags)
        return DVBv5Descriptor(fd)

    def dev_find(self, handler=None, user_priv=None) -> List[dvb_dev.DVBDevList]:
        """
        Finds all DVB devices on the local machine
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
        self._dvb = dvb_dev.dvb_dev_find(self._dvb, handler, user_priv)
        return self._dvb.devices

    def dev_seek_by_adapter(self, adapter: int, num: int, dvb_type: dvb_dev.DVBDevType) -> dvb_dev.DVBDevList:
        """
        Find a device that matches the search criteria given by this functions's parameters.
        :param adapter: Adapter number, as defined internally at the Kernel. Always start with 0
        :param num: Digital TV device number (e. g. frontend0, net0, etc)
        :param dvb_type: Type of the device, as given by enum DVBDevType
        :return: DVBDevList object or None if the desired device was not found
        """
        return dvb_dev.dvb_dev_seek_by_adapter(self._dvb, adapter, num, dvb_type)

    def fe_set_default_country(self, country: str) -> None:
        """
        Set default country variant of delivery systems like ISDB-T
        :param country: default country, in ISO 3166-1 two letter code. If None, default charset is guessed from locale
        environment variables.
        """
        return dvb_fe.dvb_fe_set_default_country(self._dvb.fe_parms, country)
