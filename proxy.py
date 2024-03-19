from httpx import HTTPTransport


class Proxy:
    def __init__(self, host: str, port: str, username: str, password: str):
        self.proxy = username + ':' + password + '@' + host + ':' + port

    def get_proxy(self) -> dict[str, HTTPTransport]:
        return {
            'http://': HTTPTransport(proxy='http://' + self.proxy),
            'https://': HTTPTransport(proxy='https://' + self.proxy)
        }


def load_proxies() -> list[Proxy]:
    try:
        with open('proxies.txt', 'r') as proxies_file:
            proxy_list = []

            for line in proxies_file:
                host, port, username, password = line.strip().split(':')
                proxy_list.append(
                    Proxy(host, port, username, password)
                )

            return proxy_list
    except FileNotFoundError:
        with open('proxies.txt', 'w'):
            pass

        raise FileNotFoundError('proxies.txt file does not exist! File created')
    except PermissionError:
        raise PermissionError('delete the proxies.txt file and start the monitor, then fill in the file')
    except EOFError:
        raise EOFError('proxies.txt file is empty')
