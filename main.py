import settings
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


def save_offers(offers_dict):
    try:
        with open('offers_IDs', 'wb') as file:
            pickle.dump(offers_dict, file)
    except Exception:
        pass


session = tls_client.Session(client_identifier="chrome_120", random_tls_extension_order=True)

proxies = Load_proxies()
Rotate_proxy(session, proxies)
