import tls_client
import csv

import settings
import cookies
import headers
from proxy import Load_proxies, Rotate_proxy


def read_past_offers():
    try:
        with open('offers_IDs', 'rb') as offers_file:
            offers_dict = pickle.load(offers_file)
            print('offers_list: ', offers_dict)

            return offers_dict
    except FileNotFoundError:
        with open('offers_IDs', 'wb'):
            pass
    except Exception:
        return {}


def save_offers(offers_dict):
    try:
        with open('offers_IDs', 'wb') as file:
            pickle.dump(offers_dict, file)
    except Exception:
        pass


def read_acceptable_offers():
    try:
        with open('wtn_acceptable.csv', 'r') as csvfile:
            acceptable_dict = {}
            reader = csv.DictReader(csvfile)

            for row in reader:
                acceptable_dict.update({int(row['PID']): int(row['MIN_PRICE'])})

            print('acceptable_dict: ', acceptable_dict)

            return acceptable_dict
    except FileNotFoundError:
        with open('wtn_acceptable.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['SKU', 'NAME', 'PID', 'MIN_PRICE'])
            writer.writeheader()

        sys.exit("ERROR - wtn_acceptable.csv file does not exist! File created")
    except Exception as e:
        sys.exit("ERROR - " + str(e))


def main():
    session = tls_client.Session(client_identifier="chrome_120", random_tls_extension_order=True)
    proxies = Load_proxies()
    Rotate_proxy(session, proxies)


if __name__ == "__main__":
    main()
