import pickle
from http.cookiejar import CookieJar


def clear_cookies_file():
    with open('cookies', 'wb') as cookies_file:
        pickle.dump({}, cookies_file)


def restore_cookies() -> dict[str, str]:
    try:
        with open('cookies', 'rb') as cookies_file:
            return pickle.load(cookies_file)
    except FileNotFoundError:
        return {}


def get_dict(self, domain=None, path=None):
    dictionary: dict[str, str] = {}

    for cookie in iter(self):
        if (domain is None or cookie.domain == domain) and (path is None or cookie.path == path):
            dictionary[cookie.name] = cookie.value

    return dictionary


CookieJar.get_dict = get_dict


def save_cookies(cookie_jar: CookieJar):
    cookies_dict = cookie_jar.get_dict()

    with open('cookies', 'wb') as cookies_file:
        pickle.dump(cookies_dict, cookies_file)
