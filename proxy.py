import sys
from itertools import cycle


class Proxy:
    def __init__(self, host: str, port: str, username: str, password: str):
        self.requests_proxy = username + ':' + password + '@' + host + ':' + port

    def get_proxy(self) -> dict[str, str]:
        return {
            'http': self.requests_proxy,
            'https': self.requests_proxy
        }


def load_proxies() -> cycle:
    try:
        with open('proxies.txt', 'r') as proxies_file:
            proxy_list = []

            for line in proxies_file:
                host, port, username, password = line.strip().split(':')
                proxy_list.append(
                    Proxy(host, port, username, password)
                )

            return cycle(proxy_list)
    except FileNotFoundError:
        with open('proxies.txt', 'w'):
            pass

        sys.exit('ERROR - proxies.txt file does not exist! File created')
    except Exception as e:
        sys.exit('ERROR - ' + str(e))


def rotate_proxy(session, proxies):
    session.proxies.update(next(proxies).get_proxy())
