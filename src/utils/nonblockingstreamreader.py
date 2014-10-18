#! /usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Thread
from Queue import Queue, Empty

class UnexpectedStreamEndError(Exception):
    pass


class NonBlockingStreamReader:
    """
    A nonblocking reader for a stream.
    Usable for reading input from another process asyncronously.
    """
    def __init__(self, stream, lines=False):
        """
        Initialize the stream reader.

        Parameters:
        - stream: The stream to read from.
                  Usually a process' stdout or stderr.
        - lines: Read full lines, if not set then, reader
                 will read all available bytes from buffer.
        """
        self._stream = stream
        self._queue = Queue()
        if lines:
            self._runner = self._run_lines
        else:
            self._runner = self._run_bytes

        self._thread = Thread(target = self._runner,
                args = (self._stream, self._queue))
        self._thread.daemon = True
        self._thread.start()

    def read(self, timeout = None):
        """
        Read from stream.
        Return after the timeout at the latest.
        Block if no timeout given.
        """
        try:
            return self._queue.get(block = timeout is not None,
                    timeout = timeout)
        except Empty:
            return None

    def _run_bytes(self, stream, queue):
        """
        Collect bytes from 'stream' and put them in 'queue'.
        """
        while True:
            char = stream.read(1)
            if char != None and char != "":
                queue.put(char)
            elif char == "":
                return
            else:
                raise UnexpectedStreamEndError

    def _run_lines(self, stream, queue):
        """
        Collect lines from 'stream' and put them in 'queue'.
        """
        while True:
            line = stream.readline()
            if line:
                queue.put(line)
            else:
                raise UnexpectedStreamEndError


