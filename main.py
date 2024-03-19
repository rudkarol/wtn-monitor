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
import config
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

        raise FileNotFoundError('wtn_acceptable.csv file does not exist! File created')


def read_recent_offers() -> dict[int, int]:
    try:
        with open('offers_IDs', 'rb') as file:
            return pickle.load(file)
    except (EOFError, FileNotFoundError):
        pass
    except PermissionError:
        raise PermissionError('delete the "offers_IDs" file')

    return {}


def save_recent_offers(offers: dict[int, int]):
    with open('offers_IDs', 'wb') as file:
        pickle.dump(offers, file)


class Monitor:
    def __init__(self):
        self.client = None
        self.clients_pool: list[httpx.Client] = []
        self.access_token = ""

        try:
            self.recent_offers = read_recent_offers()
            print(f'recent offers: {self.recent_offers}')

            self.acceptable_offers = read_acceptable_offers()
            self.proxies = load_proxies()

            monitor_config = config.Config()
            self.delay = monitor_config.get_delay()
            self.webhook_url = monitor_config.get_webhook_url()

            self.cookies = cookies.restore_cookies()

            if not self.cookies:
                self.cookies = monitor_config.get_token()

        except (FileNotFoundError, KeyError, ValueError, PermissionError, EOFError) as e:
            sys.exit(e)

        for proxy in self.proxies:
            c = httpx.Client(mounts=proxy.get_proxy())
            self.clients_pool.append(c)

    def initial_request(self) -> str:
        self.client = choice(self.clients_pool)
        self.client.cookies = self.cookies

        r = (self.client.get('https://sell.wethenew.com/api/auth/session')
             .raise_for_status()
             .json())

        try:
            if 'error' in r['user'] or r['user']['accessToken'] == '':
                raise ValueError('accessToken is invalid - cookies are expired')
        except KeyError:
            raise KeyError('accessToken is invalid - cookies are expired')

        self.cookies = self.client.cookies.jar
        cookies.save_cookies(self.client.cookies.jar)

        print(f'{datetime.datetime.now().strftime("%H:%M:%S")} initial request success')

        return r['user']['accessToken']

    def get_offers(self):
        self.client = choice(self.clients_pool)
        self.client.cookies = self.cookies

        r = (self.client.get(
            url='https://api-sell.wethenew.com/offers?take=10',
            headers=headers.get_offers_header(self.access_token))
             .raise_for_status()
             .json())

        try:
            print(f'{datetime.datetime.now().strftime("%H:%M:%S")} offers: {r["results"]}')

            self.review_offers(r['results'])
        except KeyError:
            raise KeyError('offers list is empty')
        except ValueError:
            raise

        self.cookies = self.client.cookies.jar
        cookies.save_cookies(self.client.cookies.jar)

    def review_offers(self, offers):
        for offer in offers:
            try:
                if offer['variantId'] in self.acceptable_offers:
                    if offer['price'] >= self.acceptable_offers[offer['variantId']]:
                        self.accept_offer(offer)
                    elif (offer['id'], offer['price']) not in self.recent_offers.items():
                        offer_webhook(data=offer, url=self.webhook_url)

                        self.recent_offers.update({offer['id']: offer['price']})
                        save_recent_offers(self.recent_offers)
            except KeyError:
                raise ValueError('the offer is incorrect')

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
            accepted_webhook(data=offer, url=self.webhook_url)
        elif r.status_code == httpx.codes.OK:
            print(f'Offer {offer["id"]} accepted, - status code: {r.status_code}'
                  '\nCheck the sales tab on wtn to make sure the offer has been accepted.')

            accepted_webhook(
                data=offer,
                additional_mess='\nCheck the sales tab on wtn to make sure the offer has been accepted',
                url=self.webhook_url
            )
        elif r.status_code != httpx.codes.OK:
            print(f'Failed to accept offer {offer["id"]} - status code: {r.status_code}')
            failed_webhook(data=offer, url=self.webhook_url)

    def stop_monitor(self, mess: str, clear_cookies: bool = True):
        if clear_cookies:
            cookies.clear_cookies_file()

        discord_webhook.error_webhook(f'MONITOR STOPPED! - {mess}', self.webhook_url)
        sys.exit(f'ERROR - {mess}')

    def multiple_failed_requests(self, count: int, proxies_len: int):
        # TODO fix
        count += 1

        if count > 15 or proxies_len:
            self.stop_monitor('Too many failed requests', False)

    def start(self):
        failed_requests = 0

        try:
            self.access_token = self.initial_request()
        except (ValueError, KeyError, httpx.HTTPStatusError):
            self.stop_monitor('Session expired. Login and update the session token in the config.yaml file')

        time.sleep(self.delay)

        while True:
            try:
                self.get_offers()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    self.stop_monitor('Session expired (429). Login and update the session token in the config.yaml file')
                else:
                    self.multiple_failed_requests(failed_requests, len(self.proxies))
            except httpx.HTTPError as e:
                print(e)
                self.multiple_failed_requests(failed_requests, len(self.proxies))
            except (KeyError, ValueError) as e:
                print(e)

            time.sleep(self.delay)


if __name__ == '__main__':
    monitor = Monitor()
    monitor.start()
