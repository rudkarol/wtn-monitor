import csv


def read_acceptable_offers() -> dict[int, int]:
    try:
        with open('wtn_acceptable.csv', 'r') as csvfile:
            acceptable_dict: dict[int, int] = {}
            reader = csv.DictReader(csvfile)

            for row in reader:
                acceptable_dict.update({int(row['PID']): int(row['MIN_PRICE'])})

            print(f'acceptable offers : {acceptable_dict}')

            return acceptable_dict
    except FileNotFoundError:
        write_file()

        raise FileNotFoundError('wtn_acceptable.csv file does not exist! File created')


def read_file() -> list[dict[str]]:
    try:
        with open('wtn_acceptable.csv', 'r') as csvfile:
            list_of_dicts = []
            reader = csv.DictReader(csvfile)

            for row in reader:
                list_of_dicts.append(row)

            return list_of_dicts
    except FileNotFoundError:
        write_file()

        raise FileNotFoundError('wtn_acceptable.csv file does not exist! File created')


def write_file(data: list[dict[str]] = None):
    with open('wtn_acceptable.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['SKU', 'NAME', 'PID', 'MIN_PRICE'])
        writer.writeheader()

        if data:
            for row in data:
                writer.writerow(row)


def update_file():
    print(read_file())
