import pickle
import httpx
import csv
import json
import sys

import cookies
import headers
from proxy import Load_proxies, Rotate_proxy


# def read_past_offers():
#     try:
#         with open('offers_IDs', 'rb') as offers_file:
#             offers_dict = pickle.load(offers_file)
#             print('offers_list: ', offers_dict)
#
#             return offers_dict
#     except FileNotFoundError:
#         with open('offers_IDs', 'wb'):
#             return {}
#     except Exception:
#         return {}


def save_offers(offers_dict):
    try:
        with open('offers_IDs', 'wb') as file:
            pickle.dump(offers_dict, file)
    except Exception:
        pass


def read_acceptable_offers() -> dict:
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

        sys.exit('ERROR - wtn_acceptable.csv file does not exist! File created')
    except Exception as e:
        sys.exit('ERROR - ' + str(e))


def initial_request(client: httpx.Client) -> str:
    r = (client.get('https://sell.wethenew.com/api/auth/session')
         .raise_for_status()
         .json())

    try:
        if 'error' in r['user'] or r['user']['accessToken'] == '':
            raise ValueError('ERROR: accessToken is invalid - cookies are expired')

        print('access token request success')

        cookies.save_cookies(client.cookies.jar)

        return r['user']['accessToken']
    except KeyError:
        raise KeyError('ERROR: accessToken is invalid - cookies are expired')


def review_offers(offers, acceptable_dict: dict, client: httpx.Client, access_token: str) -> None:
    for offer in offers:
        try:
            if (offer['variantId'] in acceptable_dict) and (
                    offer['price'] >= acceptable_dict[offer['variantId']]
            ):
                accept_offer(offer, client, access_token)
        except KeyError:
            pass


def accept_offer(offer, client: httpx.Client, access_token: str) -> None:
    # TODO: test
    data = {
        'name': offer['id'],
        'status': "ACCEPTED",
        'variantId': offer['variantId']
    }

    r = client.post(
        'https://api-sell.wethenew.com/offers',
        data=data,
        headers=headers.accept_offer_header(access_token)
    )

    if r.status_code == httpx.codes.OK:
        # accepted_webhook(offer)
        print('Offer ', offer['id'], 'accepted - status code:', str(r.status_code))
    else:
        print('Failed to accept offer ', offer['id'], '- status code:', str(r.status_code))


def get_offers(client: httpx.Client, access_token: str, acceptable: dict) -> None:
    r = (client.get('https://api-sell.wethenew.com/offers?take=10', headers=headers.get_offers_header(access_token))
         .raise_for_status()
         .json())

    try:
        print('offers: ', r['results'])

        cookies.save_cookies(client.cookies.jar)

        review_offers(r['results'], acceptable, client, access_token)
    except KeyError:
        raise KeyError('ERROR: offers list is empty')


def main():
    with httpx.Client() as client:
        # proxies = Load_proxies()
        acceptable_offers = read_acceptable_offers()

        # Rotate_proxy(session, proxies)
        client.cookies.update(cookies.restore_cookies())

        try:
            access_token = initial_request(client)
        except (ValueError, KeyError) as e:
            cookies.clear_cookies_file()
            sys.exit(e)

        try:
            get_offers(client, access_token, acceptable_offers)
        except (httpx.HTTPStatusError, KeyError) as e:
            print(e)
            cookies.clear_cookies_file()


if __name__ == '__main__':
    main()
