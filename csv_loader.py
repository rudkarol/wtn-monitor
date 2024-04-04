import csv
import httpx
import sys
from ssl import SSLError

import config
import cookies
import headers
from monitor import Monitor


def read_file() -> list[dict[str, str]]:
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


def write_file(data: list[dict[str, str]] = None):
    with open('wtn_acceptable.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['SKU', 'NAME', 'SIZE', 'PID', 'MIN_PRICE'])
        writer.writeheader()

        if data:
            for row in data:
                writer.writerow(row)


class CsvLoader(Monitor):
    def __init__(self):
        self.client = httpx.Client()
        self.access_token = ""

        try:
            monitor_config = config.Config()

            self.cookies = cookies.restore_cookies()

            if not self.cookies:
                self.cookies = monitor_config.get_token()

        except (FileNotFoundError, KeyError, ValueError, PermissionError, EOFError) as e:
            sys.exit(e)

    def get_listings(self):
        self.get_access_token()

        try:
            r = (self.client.get(
                url='https://api-sell.wethenew.com/listings?take=10',
                headers=headers.get_listings_header(self.access_token))
                 .raise_for_status()
                 .json())

            cookies.save_cookies(self.client.cookies.jar)

            return r['results']

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 or 401:
                print(f'Session expired ({e.response.status_code}). Login and update the session token in the config.yaml file')
                cookies.clear_cookies_file()
            else:
                print(e)
        except (httpx.HTTPError, KeyError, ValueError, SSLError) as e:
            print(e)

    def update_file(self):
        file_data = read_file()
        listings = self.get_listings()

        if len(file_data) > len(listings):
            size = len(file_data)
        else:
            size = len(listings)

        for listing in listings:
            for i in range(size):
                try:
                    if listing['product']['variantId'] == file_data[i]['PID']:
                        break
                except (KeyError, IndexError) as e:
                    print(e)

                file_data.append({
                    'SKU': listing['product']['sku'],
                    'NAME': listing['product']['name'],
                    'SIZE': listing['product']['europeanSize'],
                    'PID': listing['product']['variantId'],
                    'MIN_PRICE': listing['price']
                })

                break

        write_file(file_data)

        print('File updated successfully')
