def csv_reader(file, delimiter=',', escape='\"', linebreak='\n') -> list:
    escaped, string, row = False, '', []
    for character in file:
        if escape in character:
            escaped = not escaped
            continue
        if character in {delimiter, linebreak} and not escaped:
            row.append(string)
            string = ''
            if character == linebreak:
                yield row
                row = []
            continue
        string += character
    if string:
        row.append(string)
        yield row


def get_header_indexes(received: list, expected=('country', 'population', 'net change', 'land area', 'regions')):
    received = tuple(heading.lower() for heading in received)
    return tuple(received.index(header) for header in expected)


class Country:

    def __init__(self, data, headers):
        data = [set_type(item) for item in data]
        self.NAME, self.POPULATION, self.NET_CHANGE, self.LAND_AREA, self.REGION = (data[i] for i in headers)
        expected_types = (str, int, int, int, str)
        properties = (self.NAME, self.POPULATION, self.NET_CHANGE, self.LAND_AREA, self.REGION)
        for type_, property_ in zip(expected_types, properties):
            if not isinstance(property_, type_) or not property_:
                raise ValueError(f'{self.NAME!r}: was expecting {type_.__name__!r} but got {type(property_).__name__!r}')


def set_type(item: str):
    return int(item) if item.lstrip('-+').isdigit() else item


def main(file):
    with open(file, 'r') as f:
        received_headers, *data = csv_reader(f.read())
        header_indexes = get_header_indexes(received_headers)
        countries = []
        for country in data:
            pass

    stats = {'northern america': [80089583.56, 0.7841]}
    northern_america_data = {
        'united states': [331002651, 1937734, 89.7357, 36.1854, 1],
        'canada': [37742154, 331107, 10.232, 4.1504, 2],
        'bermuda': [62278, -228, 0.0169, 1245.56, 3],
        'greenland': [56770, 98, 0.0154, 0.1383, 4]
    }
    region_data = {'northern america': northern_america_data}
    return stats, region_data


if __name__ == '__main__':
    main('Countries.csv')
