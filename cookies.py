import pickle
import sys

from tls_client.sessions import cookiejar_from_dict


def read_session_token():
    try:
        with open("session-token.txt", "r") as session_token_file:
            return session_token_file.read()
    except FileNotFoundError:
        with open("session-token.txt", "w"):
            print("ERROR - session-token.txt file does not exist! File created")
    except Exception as e:
        print("ERROR - " + str(e))


def Restore_cookies():
    try:
        with open('cookies', 'rb') as cookies_file:
            return pickle.load(cookies_file)
    except Exception as e:
        print("WARNING - " + str(e))
        print("reading session-token.txt ...")

        try:
            return cookiejar_from_dict({
                "__Secure-next-auth.session-token": read_session_token()
            })
        except Exception as e:
            sys.exit(str(e))


def save_cookies(session):
    try:
        with open('cookies', 'wb') as cookies_file:
            pickle.dump(session.cookies, cookies_file)
    except Exception as e:
        print("ERROR - " + str(e))
