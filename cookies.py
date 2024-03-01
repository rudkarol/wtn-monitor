import json
import sys

from http.cookiejar import CookieJar


def clear_cookies_file():
    with open('cookies.json', 'w') as cookies_file:
        json.dump({'__Secure-next-auth.session-token': ''}, cookies_file)


def restore_cookies():
    try:
        with open('cookies.json', 'r') as cookies_file:
            return json.load(cookies_file)
    except Exception as e:
        print(e)
        clear_cookies_file()


def get_dict(self, domain=None, path=None):
    dictionary = {}

    for cookie in iter(self):
        if (domain is None or cookie.domain == domain) and (path is None or cookie.path == path):
            dictionary[cookie.name] = cookie.value

    return dictionary


CookieJar.get_dict = get_dict


def save_cookies(cookie_jar: CookieJar):
    cookies_dict = cookie_jar.get_dict()


    with open('cookies.json', 'w') as cookies_file:
        json.dump(cookies_dict, cookies_file)
