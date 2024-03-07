import pickle
import time
import httpx
import csv
import sys

import cookies
import headers
import settings
from proxy import load_proxies, rotate_proxy
from discord_webhook import accepted_webhook, offer_webhook


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


def read_recent_offers() -> dict[int, int]:
    try:
        with open('offers_IDs', 'rb') as file:
            offers = pickle.load(file)
            print('recent_offers_list: ', offers)

            return offers
    except FileNotFoundError:
        with open('offers_IDs', 'wb'):
            return {}
    except Exception:
        return {}


def save_recent_offers(offers: dict[int, int]):
    try:
        with open('offers_IDs', 'wb') as file:
            pickle.dump(offers, file)
    except Exception:
        pass


class Monitor:
    def __init__(self):
        self.client = httpx.Client()
        self.access_token = ""
        self.acceptable_offers = read_acceptable_offers()
        self.recent_offers = read_recent_offers()

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

    def review_offers(self, offers):
        for offer in offers:
            try:
                if offer['variantId'] in self.acceptable_offers:
                    if offer['price'] >= self.acceptable_offers[offer['variantId']]:
                        self.accept_offer(offer)
                    elif (offer['id'], offer['price']) not in self.recent_offers.items():
                        offer_webhook(offer)

                        self.recent_offers.update({offer['id']: offer['price']})
                        save_recent_offers(self.recent_offers)
            except KeyError:
                pass

    def accept_offer(self, offer: dict[str, str]):
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
            accepted_webhook(offer)
        else:
            print('Failed to accept offer ', offer['id'], '- status code:', str(r.status_code))
    #         TODO add failed webhook

    def start(self):
        self.client.cookies.update(cookies.restore_cookies())

        try:
            self.access_token = self.initial_request()
        except (ValueError, KeyError) as e:
            cookies.clear_cookies_file()
            sys.exit(e)

        while True:
            try:
                self.get_offers()
            except (httpx.HTTPStatusError, KeyError) as e:
                print(e)
                cookies.clear_cookies_file()
            except httpx.HTTPError:
                pass
            except httpx.ProxyError:
                pass

            time.sleep(settings.DELAY)


if __name__ == '__main__':
    monitor = Monitor()
    monitor.start()

# TODO handling multiple failed requests
