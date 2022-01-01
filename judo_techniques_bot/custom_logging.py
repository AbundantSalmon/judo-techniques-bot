import time
from logging import Formatter


class CustomFormatter(Formatter):
    include_tz = True
    tz_format = "%Z"

    def formatTime(self, record, datefmt=None):
        s = super().formatTime(record, datefmt)

        ct = self.converter(record.created)
        if self.include_tz:
            s += f" {time.strftime(self.tz_format, ct)}"
        return s
