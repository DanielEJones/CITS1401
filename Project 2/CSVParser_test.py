from unittest import TestCase, main
from random import shuffle
from io import StringIO
import CSVParser


class CSVReaderTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.name = cls.__name__

    def test_Splits_At_Commas(self):
        # Test that values in row are correctly splits at commas.
        test_data = StringIO('this,is,a,csv,file\n')
        expected_data = (['this', 'is', 'a', 'csv', 'file'],)
        for given, expected in zip(CSVParser.csv_reader(test_data.read()), expected_data):
            self.assertEqual(expected, given, f'{self.name}: Fails to split at commas.')

    def test_Splits_At_Newline(self):
        # Test that correctly splits data into separate rows at newline character.
        test_data = StringIO('this,is,a,csv,file\nwith,two,lines,after,each-other!\n')
        expected_data = (['this', 'is', 'a', 'csv', 'file'], ['with', 'two', 'lines', 'after', 'each-other!'])
        for given, expected in zip(CSVParser.csv_reader(test_data.read()), expected_data):
            self.assertEqual(expected, given, f'{self.name}: Fails to split at newlines')

    def test_Skips_Escaped_Characters(self):
        # Test that correctly skips escaped commas and newlines when parsing.
        test_data = StringIO('this,is,a,csv,file\nwith,"escaped\n",newlines,and,"com,mas"\n')
        expected_data = (['this', 'is', 'a', 'csv', 'file'], ['with', 'escaped\n', 'newlines', 'and', 'com,mas'])
        for given, expected in zip(CSVParser.csv_reader(test_data.read()), expected_data):
            self.assertEqual(expected, given, f'{self.name}: Fails to escape the newlines/commas.')

    def test_No_Trailing_Newline(self):
        # Test that correctly returns all the data from files with no trailing newline, including the last line.
        test_data = StringIO('this,does,not,have,a,newline')
        expected_data = (['this', 'does', 'not', 'have', 'a', 'newline'],)
        for given, expected in zip(CSVParser.csv_reader(test_data.read()), expected_data):
            self.assertEqual(expected, given, f'{self.name}: Fails to handle file with no trailing newline.')

    def test_Empty_File(self):
        # Test that it correctly handles empty files by returning and empty list.
        test_data = StringIO('')
        expected_data = ([],)
        for given, expected in zip(CSVParser.csv_reader(test_data.read()), expected_data):
            self.assertEqual(expected, given, f'{self.name}: Fails to handle an empty file.')

    def test_String_Of_Commas(self):
        # Test that correctly handles a string of commas by returning a list of empty values.
        test_data = StringIO(',,,\n,,,')
        expected_data = (['', '', '', ''], ['', '', '', ''])
        for given, expected in zip(CSVParser.csv_reader(test_data.read()), expected_data):
            self.assertEqual(expected, given, f'{self.name}: Fails to handle repeat commas.')

    def test_Escaping_Escape_Character(self):
        # Test that correctly handles escaping an escape character that is intended to be printed.
        test_data = StringIO(',""," "" "\n')
        expected_data = (['', '"', ' " '],)
        for given, expected in zip(CSVParser.csv_reader(test_data.read()), expected_data):
            self.assertEqual(expected, given, f'{self.name}: Fails to escape the escape character.')

    def test_Large_Files(self):
        # Test that it correctly splits a large (contains no escapes).
        with open('Countries.csv', 'r') as f:
            given, expected = [line for line in CSVParser.csv_reader(f.read())], []
            f.seek(0)
            for line in f.readlines():
                expected.append([item.strip('\"') for item in line.strip().split(',')])
            self.assertEqual(expected, given)


class GetHeaderIndexes(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.name = cls.__name__

    def test_Headers_In_Order(self):
        # Test that get_header_indexes does indeed return indices.
        test_data, expected_out = ['country', 'population', 'net change', 'land area', 'regions'], (0, 1, 2, 3, 4)
        given = CSVParser.get_header_indexes(test_data)
        self.assertEqual(expected_out, given, f'{self.name}: cannot return headers when in order')

    def test_Headers_In_Random_Order(self):
        # Test when headers appear in a random order.
        test_data = ['country', 'population', 'net change', 'land area', 'regions']
        for _ in range(500):
            new = test_data.copy()
            shuffle(new)
            expected_out = tuple(new.index(item) for item in test_data)
            given = CSVParser.get_header_indexes(new)
            self.assertEqual(expected_out, given, f'{self.name}: cannot return correct index when order is randomised.')

    def test_Headers_With_Noise(self):
        # Test when there are more than just the default headers.
        test_data = ['country', 'Nonsense', 'population', 'more nonsense', 'net change', 'land area', 'lol', 'regions']
        expected_out = (0, 2, 4, 5, 7)
        given = CSVParser.get_header_indexes(test_data)
        self.assertEqual(expected_out, given, f'{self.name}: cannot return correct index when headers include noise.')

    def test_Headers_In_Random_Order_With_Noise(self):
        # Tests when both noise is added and the data is shuffled,
        correct_data = ['country', 'population', 'net change', 'land area', 'regions']
        test_data = ['country', 'Nonsense', 'population', 'more nonsense', 'net change', 'land area', 'lol', 'regions']
        for _ in range(500):
            new = test_data.copy()
            shuffle(new)
            expected_out = tuple(new.index(item) for item in correct_data)
            given = CSVParser.get_header_indexes(new)
            self.assertEqual(expected_out, given, f'{self.name}: cannot return correct index with random noise.')

    def test_No_Headers(self):
        # Tests that an error is raised if headers are not given.
        test_data = []
        flag = False
        try:
            CSVParser.get_header_indexes(test_data)
        except ValueError:
            flag = True
        self.assertTrue(flag, f'{self.name}: does not raise exception if no headers are present.')


class MainFunctionTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.name = cls.__name__

    def test_Main(self):
        # Tests that the data returned matches the data provided in specification
        stats, region_data = CSVParser.main('Countries.csv')

        # Test that the stats are as expected
        expected_stats = [80089583.56, 0.7841]
        given = stats['northern america']
        self.assertEqual(given, expected_stats, f'{self.name}: Stats output does not match expected')

        # Test the region data is as expected
        expected_region_data = {
            'united states': [331002651, 1937734, 89.7357, 36.1854, 1], 'canada': [37742154, 331107, 10.232, 4.1504, 2],
            'bermuda': [62278, -228, 0.0169, 1245.56, 3], 'greenland': [56770, 98, 0.0154, 0.1383, 4]}
        given = region_data['northern america']
        self.assertEqual(given, expected_region_data, f'{self.name}: Region Data does not match expected')


if __name__ == '__main__':
    main()
