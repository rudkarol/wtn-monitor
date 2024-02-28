import httpx
import csv
import json

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
            return {}
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


def initial_request(client: httpx.Client):
    response = client.get("https://sell.wethenew.com/api/auth/session")

    # TODO if response == {} raise exception

    response = response.json()
    print(response['user']['accessToken'])

    return response['user']['accessToken']


def main():
    with httpx.Client() as client:
        # proxies = Load_proxies()
        # offers = read_past_offers()

        # Rotate_proxy(session, proxies)
        client.cookies.update(cookies.restore_cookies())

        try:
            accessToken = initial_request(client)
        except httpx.HTTPStatusError as e:
            print(e)

        get_offers = client.get("https://api-sell.wethenew.com/offers?take=10", headers=headers.get_offers_header(accessToken))
        print(get_offers.text)


if __name__ == "__main__":
    main()
