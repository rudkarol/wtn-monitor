import sys


class Proxy:
    def __init__(self, host: str, port: str, username: str, password: str):
        self.requests_proxy = username + ":" + password + "@" + host + ":" + port

    def getProxy(self):
        return {
            "http": self.requests_proxy,
            "https": self.requests_proxy
        }


def load_proxies():
    proxy_list = []

    try:
        with open("proxies.txt", "r") as proxies_file:
            for line in proxies_file:
                host, port, username, password = line.strip().split(":")
                proxy_obj = Proxy(host, port, username, password)
                proxy_list.append(proxy_obj)
    except EOFError:
        sys.exit("ERROR - proxies.txt file is empty!")
    except FileNotFoundError:
        proxies_file = open("proxies.txt", "w")
        proxies_file.close()
        sys.exit("ERROR - proxies.txt file does not exist! File created")
    except Exception as e:
        sys.exit("ERROR - " + str(e))

    return proxy_list
