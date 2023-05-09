from unittest import TestCase
from ProjectOneCSVParser import BufferedReader, csv_read, main
import io


class TestBufferedReader(TestCase):

    @classmethod
    def setUp(cls) -> None:
        cls.file = io.StringIO('This is a file\nWith lines\nAnd things...')

    def testPeekBeforeRead(self):
        b = BufferedReader(self.file, 16)
        self.assertTrue(b.peek() == 'T')

    def testTraverse(self):
        b = BufferedReader(self.file, 5)
        s = [item for item in 'This is a file\nWith lines\nAnd things...']
        traverse = 0
        error_msg = f'"{b.current()}" not equal "{s[traverse - 1]}": {b.file.tell()}.'

        b.traverse(traverse := 7)
        self.assertTrue(b.current() == s[traverse - 1], error_msg)

        b.__init__(self.file, 5)
        b.traverse(traverse := 1)
        self.assertTrue(b.current() == s[traverse - 1], error_msg)

        b.__init__(self.file, 5)
        b.traverse(traverse := 5)
        self.assertTrue(b.current() == s[traverse - 1], error_msg)

    def testOutput(self):
        b = BufferedReader(self.file, 100)
        result = ''.join([character for character in b])
        self.assertTrue(result == 'This is a file\nWith lines\nAnd things...',
                        'Output of Reader does not match input file.')

    def testCsvRead(self):
        with open('countries.csv', 'r') as file:
            b = [line for line in csv_read(file)]
            file.seek(0)
            expected = []
            for line in file.readlines():
                expected.append([item.strip('\"') for item in line.strip().split(',')])
            self.assertTrue(b == expected)

    def testMain(self):
        b = main('Project 1/countries.csv', 'Africa')
        expected = (['Western Sahara', 'Seychelles'],
                    [291620.6667, 239936.4497],
                    [['Mayotte', 727.5067], ['Sao Tome & Principe', 228.2906],
                     ['Cabo Verde', 137.9620], ['Saint Helena', 15.5821],
                     ['Seychelles', 11.0008], ['Western Sahara', 2.2456]],
                    0.6243)
        self.assertTrue(b == expected,
                        'Output of Main does not match expected output.')
