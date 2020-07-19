import sys
import itertools
import time

__version__ = "1.0"

MARGIN = 3
DEFAULT_WIDTH = 100

PACMAN = ["\033[1;33mC\033[m", "\033[1;33mc\033[m"]
CANDY = ["\033[0;37mo\033[m", "\033[0;37m \033[m", "\033[0;37m \033[m"]


class Pacman:
    """PacMan Progress Bar"""

    def __init__(self, start=0, end=100, width=-1, step=0, text='', enconde='UTF-8', follower=True):
        """
        :param follower: bool
        :param start: Initial Position, default
        :param end: Defines the bar's dimenssion in an amount of items or steps
        :param width: Size (in chars) of the bar, default is the console size
        :param step: Current position in the progrressbar
        :param text: Write some text at the beginning of the line
        :param enconde: Encoding type
        """
        self.start = start
        self.end = end
        self.percentage = 0
        self.step = step
        self.encode = enconde
        self.text = '{0}: '.format(text) if text != '' else ''
        self.len = self.end - self.start

        if (width - MARGIN) in range(0, DEFAULT_WIDTH):
            self.width = width - MARGIN
        else:
            self.width = DEFAULT_WIDTH

        self.bar = "-"
        self.pacman = itertools.cycle(PACMAN)
        self.candy = itertools.cycle(CANDY)
        self.candybar = [None] * self.width

        for i in range(self.width):
            self.candybar[i] = next(self.candy)

        self.follower = follower

    @staticmethod
    def _write(value, encode='UTF-8'):
        """
        Write the values in the buffer
        :param value: Value to write
        :param encode: Encoding
        """

        if sys.version_info.major == 3:
            sys.stdout.buffer.write(bytes(value, encode))
        else:
            sys.stdout.write(value)

    def _set_percentage(self):
        """
        Set the current porcentage
        """

        step = float(self.step)
        end = float(self.end)
        self.percentage = format((100 * step / end), '.1f')

    def _draw(self):
        """
        Draw the values in the console
        """

        self._set_percentage()
        spaces = "".join([' ' for _ in range(len(str(self.percentage)), 5)])
        porc = "\r" + str(self.text) + spaces + str(self.percentage) + "%["
        pos = (((self.step / (self.end - self.start) * 100) * (self.width - len(porc))) / 100)
        self._write(porc)
        for i in range(int(pos)):
            self._write(self.bar)
        self._write(next(self.pacman))
        for i in range(int(pos), len(self.candybar) - 18):
            self._write(self.candybar[i])
        self._write("] > " if self.follower and self.step < self.len else "]")

        sys.stdout.flush()

        if self.step == self.len:
            self._write("\n")

    def update(self, value=1):
        """ Update the progress in the bar
            Parameter: value, is the incresing size of the bar. By default 1
        """
        self.step += float(value)
        self._draw()

    def progress(self, value):
        """ Set the progress in the bar
            Parameter: value, is the specific size of the bar. No default value
        """
        self.step = float(value)
        self._draw()


if __name__ == "__main__":
    print("TEST")
    p = Pacman(end=100, text="Progress", width=50)
    p.update(0)
    time.sleep(1)
    p.update(10)
    time.sleep(1)
    p.update(20)
    time.sleep(1)
    p.update(10)
    time.sleep(1)
    p.update(30)
    time.sleep(1)
    p.update(20)
    time.sleep(1)
    p.update(10)
    time.sleep(1)
    print("Finished")
