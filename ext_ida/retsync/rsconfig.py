#
# Copyright (C) 2019, Alexandre Gazet.
#
# This file is part of ret-sync.
#
# ret-sync is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import sys
import tempfile
import logging
from logging.handlers import RotatingFileHandler

# global plugin settings
PLUGIN_DIR = 'retsync'

# cold storage in IDA database
NETNODE_STORE = "$ SYNC_STORE"
NETNODE_INDEX = 0xFFC0DEFF

# networking settings
HOST = 'localhost'
PORT = 9100
CONNECT_BROKER_MAX_ATTEMPT = 4
RUN_DISPATCHER_MAX_ATTEMPT = 4

# color definitions
COL_BLANK = 0xffffffff
COL_GREEN = 0x33ff00
COL_DEEP_PURPLE = 0xff44dd
COL_YLW = 0x23ffff
COL_YLW_LIGHT = 0xccffff
COL_BLUE_NAVY = 0x000080
COL_GRAY = 0x808080

# general purpose current instruction syncing color
COL_CURLINE = COL_YLW

# trace color, used by !bc feature
COL_CBTRACE = COL_GREEN

# syncrays colors, gradient of yellow
COL_BLANK_HEX = COL_BLANK
COL_CURLINE_HEX = COL_YLW
COL_PREVLINE_HEX = COL_YLW_LIGHT

# dialects to translate debugger commands (breakpoint, step into/over, etc.)
DBG_DIALECTS = {
    'windbg': {
        'prefix': '!',
        'si': 't',
        'so': 'p',
        'go': 'g',
        'bp': 'bp ',
        'hbp': 'ba e 1 ',
        'bp1': 'bp /1 ',
        'hbp1': 'ba e 1 /1 '},
    'gdb': {
        'prefix': '',
        'si': 'si',
        'so': 'ni',
        'go': 'continue',
        'bp': 'b *',
        'hbp': 'hb *',
        'bp1': 'tb *',
        'hbp1': 'thb *'},
    'ollydbg2': {
        'prefix': '',
        'si': 'si',
        'so': 'so',
        'go': 'go',
        'bp': 'bp ',
        'hbp': 'xxx ',
        'bp1': 'xxx ',
        'hbp1': 'xxx '},
    'x64_dbg': {
        'prefix': '',
        'si': 'sti',
        'so': 'sto',
        'go': 'go',
        'bp': 'bp ',
        'hbp': 'bph ',
        'bp1': 'xxx ',
        'hbp1': 'xxx '},
}

# debugging settings
# enable/disable logging JSON received in the IDA output window
DEBUG_JSON = False
# enable/disable broker and dipatcher exception logging to file
LOG_TO_FILE_ENABLE = False

# logging feature for broker and dispatcher (disabled by default)
LOG_FMT_STRING = '%(asctime)-12s [%(levelname)s] %(message)s'


def init_logging(src):
    logging.basicConfig(level=logging.DEBUG)
    name = os.path.basename(src)
    rs_log = logging.getLogger('retsync.plugin.' + name)

    if LOG_TO_FILE_ENABLE:
        rot_handler = logging.handlers.RotatingFileHandler(
            os.path.join(tempfile.gettempdir(), "retsync.%s.err" % name),
            mode='a',
            maxBytes=8192,
            backupCount=1)

        formatter = logging.Formatter(LOG_FMT_STRING)
        rot_handler.setFormatter(formatter)
        rot_handler.setLevel(logging.DEBUG)
        rs_log.addHandler(rot_handler)

    return rs_log


# encoding settings (for data going in/out the plugin)
RS_ENCODING = 'utf-8'


def rs_encode(buffer_str):
    return buffer_str.encode(RS_ENCODING)


def rs_decode(buffer_bytes):
    return buffer_bytes.decode(RS_ENCODING)


# default paths Windows platforms
PY_WIN_DEFAULTS = (
    "C:\\Program Files\\Python37",
    "C:\\Program Files\\Python37-32",
    "C:\\Python27"
    )

# default paths Linux/Mac OS X platforms
PY_LINUX_DEFAULTS = (
    "/usr/bin"
    )


# retsync plugin needs a Python interpreter to run broker and dispatcher
def get_python_interpreter():
    if sys.platform == 'win32':
        PYTHON_BIN = 'python.exe'
        PYTHON_PATHS = PY_WIN_DEFAULTS

    elif sys.platform.startswith('linux') or sys.platform == 'darwin':
        PYTHON_BIN = 'python'
        PYTHON_PATHS = PY_LINUX_DEFAULTS

    else:
        print("\n[sync] plugin initialization failed")
        print("  please fix platform's PYTHON_PATH/PYTHON_BIN values in %s/rsconfig.py" % PLUGIN_DIR)
        print("  unknown platform %s\n" % sys.platform)
        sys.exit(0)

    for pypath in PYTHON_PATHS:
        interpreter = os.path.realpath(os.path.normpath(os.path.join(pypath, PYTHON_BIN)))
        if os.path.exists(interpreter):
            return interpreter

    print("\n[sync] plugin initialization failed")
    print("  please fix PYTHON_PATH/PYTHON_BIN values in %s/rsconfig.py" % PLUGIN_DIR)
    print("  Python interpreter not found\n")
    sys.exit(0)
