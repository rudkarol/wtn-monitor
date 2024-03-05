import pickle
import httpx
import csv
import sys

import cookies
import headers
from proxy import load_proxies, rotate_proxy


def read_acceptable_offers() -> dict[int, int]:
    try:
        with open('wtn_acceptable.csv', 'r') as csvfile:
            acceptable_dict: dict[int, int] = {}
            reader = csv.DictReader(csvfile)

            for row in reader:
                acceptable_dict.update({int(row['PID']): int(row['MIN_PRICE'])})

            print('acceptable_dict: ', acceptable_dict)

            return acceptable_dict
    except FileNotFoundError:
        with open('wtn_acceptable.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['SKU', 'NAME', 'PID', 'MIN_PRICE'])
            writer.writeheader()

        sys.exit('ERROR - wtn_acceptable.csv file does not exist! File created')
    except Exception as e:
        sys.exit('ERROR - ' + str(e))


def save_offers(offers_dict):
    try:
        with open('offers_IDs', 'wb') as file:
            pickle.dump(offers_dict, file)
    except Exception:
        pass


class Monitor:
    def __init__(self):
        self.client = httpx.Client()
        self.access_token = ""
        self.acceptable_offers = read_acceptable_offers()

    def initial_request(self) -> str:
        r = (self.client.get('https://sell.wethenew.com/api/auth/session')
             .raise_for_status()
             .json())

        try:
            if 'error' in r['user'] or r['user']['accessToken'] == '':
                raise ValueError('ERROR: accessToken is invalid - cookies are expired')

            print('access token request success')

            cookies.save_cookies(self.client.cookies.jar)

            return r['user']['accessToken']
        except KeyError:
            raise KeyError('ERROR: accessToken is invalid - cookies are expired')

    def review_offers(self, offers):
        for offer in offers:
            try:
                if (offer['variantId'] in self.acceptable_offers) and (
                        offer['price'] >= self.acceptable_offers[offer['variantId']]
                ):
                    self.accept_offer(offer)
            except KeyError:
                pass

    def accept_offer(self, offer):
        # TODO test
        data = {
            'name': offer['id'],
            'status': "ACCEPTED",
            'variantId': offer['variantId']
        }

        r = self.client.post(
            'https://api-sell.wethenew.com/offers',
            data=data,
            headers=headers.accept_offer_header(self.access_token)
        )

        if r.status_code == httpx.codes.OK:
            print('Offer ', offer['id'], 'accepted - status code:', str(r.status_code))
        else:
            print('Failed to accept offer ', offer['id'], '- status code:', str(r.status_code))

    def get_offers(self):
        r = (self.client.get('https://api-sell.wethenew.com/offers?take=10',
                             headers=headers.get_offers_header(self.access_token))
             .raise_for_status()
             .json())

        try:
            print('offers: ', r['results'])

            cookies.save_cookies(self.client.cookies.jar)

            self.review_offers(r['results'])
        except KeyError:
            raise KeyError('ERROR: offers list is empty')

    def start(self):
        self.client.cookies.update(cookies.restore_cookies())

        try:
            self.access_token = self.initial_request()
        except (ValueError, KeyError) as e:
            cookies.clear_cookies_file()
            sys.exit(e)

        try:
            self.get_offers()
        except (httpx.HTTPStatusError, KeyError) as e:
            print(e)
            cookies.clear_cookies_file()


if __name__ == '__main__':
    monitor = Monitor()
    monitor.start()
