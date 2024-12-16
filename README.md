# python-dvbv5

Wrapper for [libdvbv5](https://www.linuxtv.org/docs/libdvbv5/)

This library still a _work in progress_.  
Library tested using `libdvbv5` version 1.24.1.  
Scanning DVB-T system (`SYS_DVBT`) has been tested and working.

## Dependency
- libdvbv5 (version 1.24.1)

## Usage
You can use the library in two ways, by using python class
```python
from dvbv5.DVBv5 import DVBv5

dvb = DVBv5()
dev_list = dvb.dev_find()
```

or by using it as a wrapper and code in C-style
```python
from dvbv5 import dvb_dev

dvb = dvb_dev.DVBDevice()           # dvb_dev allocation handled by constructor
dvb_dev.dvb_dev_find(dvb)
# dvb_dev deallocation handled by destructor
```

## Examples
Examples can be found in the [`examples`](examples) directory
