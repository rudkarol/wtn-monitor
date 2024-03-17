import datetime
import pickle
import time
import httpx
import csv
import sys

from random import choice

import cookies
import discord_webhook
import headers
import settings
from proxy import load_proxies
from discord_webhook import accepted_webhook, offer_webhook, failed_webhook


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
            print(f'recent offers: {offers}')

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


def multiple_failed_requests(count: int, proxies_len: int):
    count += 1

    if count > 15 or proxies_len:
        stop_monitor('Too many failed requests. Check proxies, login and fill out the cookies.json file')


def stop_monitor(mess: str, clear_cookies: bool = True):
    if clear_cookies:
        cookies.clear_cookies_file()

    discord_webhook.error_webhook(f'MONITOR STOPPED! - {mess}')
    sys.exit(f'ERROR - {mess}')


class Monitor:
    def __init__(self):
        self.proxies = load_proxies()
        self.clients_pool: list[httpx.Client] = []
        self.client = None
        self.access_token = ""
        self.cookies = cookies.restore_cookies()
        self.acceptable_offers = read_acceptable_offers()
        self.recent_offers = read_recent_offers()

        for proxy in self.proxies:
            c = httpx.Client(mounts=proxy.get_proxy())
            self.clients_pool.append(c)

    def initial_request(self) -> str:
        r = (self.client.get('https://sell.wethenew.com/api/auth/session')
             .raise_for_status()
             .json())

        try:
            if 'error' in r['user'] or r['user']['accessToken'] == '':
                raise ValueError('ERROR: accessToken is invalid - cookies are expired')

            print(f'{datetime.datetime.now().strftime("%H:%M:%S")} initial request success')

            cookies.save_cookies(self.client.cookies.jar)

            return r['user']['accessToken']
        except KeyError:
            raise KeyError('ERROR: accessToken is invalid - cookies are expired')

    def get_offers(self):
        r = (self.client.get(
            'https://api-sell.wethenew.com/offers?take=10',
            headers=headers.get_offers_header(self.access_token))
             .raise_for_status()
             .json()
             )

        try:
            print(f'{datetime.datetime.now().strftime("%H:%M:%S")} offers: {r["results"]}')

            self.review_offers(r['results'])

            cookies.save_cookies(self.client.cookies.jar)
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
                print('ERROR: the offer is incorrect')

    def accept_offer(self, offer: dict[str, str]):
        data = {
            'name': offer['id'],
            'status': "ACCEPTED",
            'variantId': offer['variantId']
        }

        r = self.client.post(
            'https://api-sell.wethenew.com/offers',
            json=data,
            headers=headers.accept_offer_header(self.access_token)
        )

        if r.status_code == 201:
            print(f'Offer {offer["id"]} accepted')
            accepted_webhook(offer)
        elif r.status_code == httpx.codes.OK:
            print(f'Offer {offer["id"]} accepted, - status code: {r.status_code}'
                  '\nCheck the sales tab on wtn to make sure the offer has been accepted.')

            accepted_webhook(
                offer,
                additional_mess='\nCheck the sales tab on wtn to make sure the offer has been accepted'
            )
        elif r.status_code != httpx.codes.OK:
            print(f'Failed to accept offer {offer["id"]} - status code: {r.status_code}')
            failed_webhook(offer)

    def start(self):
        failed_requests = 0

        try:
            self.client = choice(self.clients_pool)
            self.client.cookies = self.cookies
            self.access_token = self.initial_request()
            self.cookies = self.client.cookies.jar
        except (ValueError, KeyError, httpx.HTTPStatusError):
            stop_monitor('Session expired. Login and fill out the cookies.json file')
        except Exception as e:
            stop_monitor(str(e), False)

        time.sleep(settings.DELAY)

        while True:
            try:
                self.client = choice(self.clients_pool)
                self.client.cookies = self.cookies
                self.get_offers()
                self.cookies = self.client.cookies.jar
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    stop_monitor('Session expired (429). Login and fill out the cookies.json file')
                else:
                    multiple_failed_requests(failed_requests, len(self.proxies))
            except Exception as e:
                print(e)
                multiple_failed_requests(failed_requests, len(self.proxies))

            time.sleep(settings.DELAY)


if __name__ == '__main__':
    monitor = Monitor()
    monitor.start()
