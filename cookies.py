import json
import sys


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


def save_cookies(cookies):
    try:
        with open('cookies.json', 'w') as cookies_file:
            json.dump(cookies, cookies_file)
    except Exception as e:
        print('ERROR - ' + str(e))
