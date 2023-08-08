"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://github.com/nicc777/mantellum/blob/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

from datetime import datetime

def get_utc_timestamp(with_decimal: bool=False):
    epoch = datetime(1970,1,1,0,0,0)
    now = datetime.utcnow()
    timestamp = (now - epoch).total_seconds()
    if with_decimal:
        return timestamp
    return int(timestamp)
