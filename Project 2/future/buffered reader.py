import io


class DataStream:

    def current(self) -> str:
        ...

    def peek(self) -> str:
        ...

    def skip(self) -> None:
        ...

    def __iter__(self):
        ...

    def __next__(self):
        ...


class BufferedStream(DataStream):

    _buffer: list
    _buffer_size: int

    def __init__(self, file, size: int) -> None:
        if size < 1:
            raise ValueError(f'Buffer Size must be greater than 0. Got {size} instead.')
        self._file = file
        self._buffer_size = size
        self._buffer = []

    def __iter__(self):
        return self

    def __next__(self):
        if self._buffer_is_empty():
            self._fill_buffer()
        if self._buffer_is_empty():
            raise StopIteration
        char = self._buffer.pop(0)
        return char

    def _fill_buffer(self) -> None:
        self._buffer = [char for char in self._file.read(self._buffer_size)]

    def _remaining(self) -> int:
        return len(self._buffer)

    def _buffer_is_empty(self) -> bool:
        return self._remaining() < 1

    def peek(self) -> str:
        if self._buffer_is_empty():
            self._fill_buffer()
        return self._buffer[0] if not self._buffer_is_empty() else '\0'

    def skip(self) -> None:
        self._buffer = self._buffer[1:]


class CSVReader:

    def __init__(self, file: DataStream, headers=False, escape='\"', delimiter=',', linebreak='\n') -> None:
        self._file = file
        self._escape, self._delimiter, self._linebreak = escape, delimiter, linebreak
        self.headers = self.__next__() if headers else None

    def __iter__(self) -> object:
        return self

    def __next__(self) -> list[str]:
        is_escaped, string, row = False, [], []
        for character in self._file:
            if self._escape in character and self._escape in self._file.peek():
                self._file.skip()
                string.append(character)
                continue
            if self._escape in character:
                is_escaped = not is_escaped
                continue
            if self._delimiter in character and not is_escaped:
                row.append(''.join(item for item in string))
                string = []
                continue
            if self._linebreak in character and not is_escaped:
                row.append(''.join(item for item in string))
                return row
            string.append(character)
        if string:
            row.append(''.join(item for item in string))
            return row
        raise StopIteration


f = io.StringIO('one,tw""o,three\nfour,five,six\nseven,eight,"ni""ne"')
b = BufferedStream(f, 6)
c = CSVReader(b)
print([item for item in c])
