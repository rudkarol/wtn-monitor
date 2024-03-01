import json
import sys

from http.cookiejar import CookieJar


def read_session_token():
    try:
        with open('session-token.txt', 'r') as session_token_file:
            return session_token_file.read()
    except FileNotFoundError:
        with open('session-token.txt', 'w'):
            print('ERROR - session-token.txt file does not exist! File created')
    except Exception as e:
        print('ERROR - ' + str(e))


def restore_cookies():
    try:
        with open('cookies.json', 'r') as cookies_file:
            return json.load(cookies_file)
    except Exception as e:
        print('WARNING - ' + str(e))
        print('reading session-token.txt ...')

        try:
            return {'__Secure-next-auth.session-token': read_session_token()}
        except Exception as e:
            sys.exit(str(e))


def get_dict(self, domain=None, path=None):
    dictionary = {}

    for cookie in iter(self):
        if (domain is None or cookie.domain == domain) and (
                path is None or cookie.path == path
        ):
            dictionary[cookie.name] = cookie.value

    return dictionary


CookieJar.get_dict = get_dict


def save_cookies(cookie_jar: CookieJar):
    cookies_dict = cookie_jar.get_dict()

    with open('cookies.json', 'w') as cookies_file:
        json.dump(cookies_dict, cookies_file)
