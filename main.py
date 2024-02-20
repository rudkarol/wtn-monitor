if __name__ == '__main__':
    import tls_client
    import random
    import time
    import csv
    import pickle
    import sys
    import json

    import undetected_chromedriver as uc
    from selenium.webdriver import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as ec

    from discord_webhook import DiscordWebhook, DiscordEmbed

    import settings


    session = tls_client.Session(client_identifier="chrome_107", random_tls_extension_order=True)

    url = 'https://sell.wethenew.com'

    proxies = {
        'http': '',
        'https': '',
        'no_proxy': 'localhost,127.0.0.1'
    }
    proxy_list = []
    ip_no = 0
    request_failed = 0

    delay = 10.0


    # ==================================================================================================================

    # PROXY ROTATION
    def rotate_proxy(IP_NO):
        try:
            proxies['http'] = 'http://' + proxy_list[IP_NO]
            proxies['https'] = 'https://' + proxy_list[IP_NO]
            session.proxies.update(proxies)
        except IndexError:
            global ip_no
            ip_no = 0
            rotate_proxy(0)


    # SLOWTYPE FOR WEBDRIVER LOGIN
    def slow_type(pageElem, pageInput):
        for letter in pageInput:
            time.sleep(float(random.uniform(.03, .1)))
            pageElem.send_keys(letter)


    # OFFER WEBHOOK
    def offer_webhook(_offer):
        embed = DiscordEmbed(title=_offer["name"], color='bfbfbf')

        embed.set_footer(text="WTN Offer Sniper | Lorekk")
        embed.set_timestamp()
        embed.add_embed_field(name="ID", value=_offer["id"], inline=False)
        embed.add_embed_field(name="Price", value=str(_offer["price"]), inline=False)
        embed.add_embed_field(name="Size", value=_offer["europeanSize"], inline=False)
        embed.add_embed_field(name="Listing price", value=str(_offer["listingPrice"]), inline=False)
        embed.add_embed_field(name="Variant", value=str(_offer["variantId"]), inline=False)
        embed.set_thumbnail(url=_offer["image"])

        webhook = DiscordWebhook(url=settings.webhook_url, rate_limit_retry=True)
        webhook.add_embed(embed)
        send_webhook = webhook.execute()


    # OFFER WEBHOOK
    def accepted_webhook(_offer):
        mess = "Offer accepted! - " + _offer["name"]  # zmiana - w title niżej było _offer["name"]
        embed = DiscordEmbed(title=mess, color='00c703')

        embed.set_footer(text="WTN monitor")
        embed.set_timestamp()
        embed.add_embed_field(name="ID", value=_offer["id"], inline=False)
        embed.add_embed_field(name="Price", value=str(_offer["price"]), inline=False)
        embed.add_embed_field(name="Size", value=_offer["europeanSize"], inline=False)
        embed.add_embed_field(name="Listing price", value=str(_offer["listingPrice"]), inline=False)
        embed.add_embed_field(name="Variant", value=str(_offer["variantId"]), inline=False)
        embed.set_thumbnail(url=_offer["image"])

        webhook = DiscordWebhook(url=settings.webhook_url, rate_limit_retry=True)
        webhook.add_embed(embed)
        send_webhook = webhook.execute()


    # LOGIN WITH WEBDRIVER
    def login():
        global driver
        driver = uc.Chrome(executable_path=r'C:\Users\PC\PycharmProjects\chromedriver\chromedriver.exe', port=0)

        print('Logging in...')

        driver.get(url + '/login')

        try:
            for i in range(0, 2):
                cookies_btn = WebDriverWait(driver, 10).until(
                    ec.presence_of_element_located((By.ID, settings.COOKIES_BUTTON))
                )

                driver.execute_script("arguments[0].click();", cookies_btn)
        except:
            pass

        username = WebDriverWait(driver, 15).until(
            ec.presence_of_element_located((By.NAME, settings.LOGIN_USERNAME_FIELD))
        )

        password = WebDriverWait(driver, 15).until(
            ec.presence_of_element_located((By.NAME, settings.LOGIN_PASSWORD_FIELD))
        )

        login_button = WebDriverWait(driver, 15).until(
            ec.presence_of_element_located((By.XPATH, settings.LOGIN_BUTTON))
        )

        slow_type(username, settings.USERNAME)
        slow_type(password, settings.PASSWORD)
        login_button.send_keys(Keys.ENTER)

        print('Successfully logged in!')

        offers_button = WebDriverWait(driver, 15).until(
            ec.presence_of_element_located((By.XPATH, settings.OFFERS))
        )

        offers_button.click()

        set_cookies()


    # READ PROXIES FROM FILE
    def load_proxies():
        try:
            with open('proxies.txt', 'r') as proxies_file:
                for line in proxies_file:
                    temp = line.strip().split(':')
                    proxy_list.append(temp[2] + ':' + temp[3] + '@' + temp[0] + ':' + temp[1])
            proxies_file.close()

            rotate_proxy(ip_no)
        except EOFError:
            sys.exit('ERROR - proxies.txt file is empty!')
        except FileNotFoundError:
            proxies_file = open('proxies.txt', 'w')
            proxies_file.close()
            sys.exit('ERROR - proxies.txt file does not exist! File created')
        except Exception as e:
            sys.exit('ERROR - ', e)


    # SET COOKIES FROM WEBDRIVER TO SESSION AND FILE
    def set_cookies():
        time.sleep(2)
        cookies = driver.get_cookies()
        driver.quit()

        for cookie in cookies:
            session.cookies.set(
                cookie['name'],
                cookie['value'],
                path=cookie['path']
                # domain=cookie['domain'],
                # expires=cookie['expiry'],
                # secure=cookie['secure'],
                # rest={'HttpOnly': cookie['httpOnly']}
            )

        with open('cookies', 'wb') as cookies_file:
            pickle.dump(session.cookies, cookies_file)
        cookies_file.close()


    # GET COOKIES FORM FILE AND SET REQUEST HEADER
    def restore_cookies():
        try:
            with open('cookies', 'rb') as cookies_file:
                session.cookies.update(pickle.load(cookies_file))
            cookies_file.close()
        except FileNotFoundError:
            cookies_file = open('cookies', 'wb')
            cookies_file.close()
            login()
        except EOFError:
            login()
        finally:
            accessToken_header = {
                'Accept': 'application/json, text/html, */*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
                # 'Origin': 'https://sell.wethenew.com',
                'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50'
            }

            accessToken_request = session.get('https://sell.wethenew.com/api/auth/session', headers=accessToken_header)
            accessToken = json.loads(accessToken_request.text)
            accessToken['user']['accessToken']

            global get_offers_header
            global accept_offer_header

            get_offers_header = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
                'Authorization': 'Bearer ' + accessToken['user']['accessToken'],
                'Origin': 'https://sell.wethenew.com',
                # 'Sec-Fetch-Dest:': 'empty',
                # 'Sec-Fetch-Mode:': 'cors',
                # 'Sec-Fetch-Site:': 'same-site',
                # 'Sec-Fetch-User:': '?1',
                # 'Upgrade-Insecure-Requests': '1',
                'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50'
            }

            accept_offer_header = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
                'Authorization': 'Bearer ' + accessToken['user']['accessToken'],
                'Content-Type': 'application/json',
                'Origin': 'https://sell.wethenew.com',
                'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50'
            }


    # INITIAL REQUEST
    def initial_request():
        init_request = session.get(url, headers=get_offers_header)

        if init_request.status_code == 429:
            print('rotate proxy')  # rotate proxy
        elif init_request.status_code == 403:
            print('Init request 403, run login()')
            login()


    # READ OFFERS ID'S FROM FILE
    def read_offers():
        global offers_dict
        offers_dict = {}
        try:
            with open('offers_IDs', 'rb') as offers_file:
                offers_dict = pickle.load(offers_file)
            offers_file.close()
        except FileNotFoundError:
            offers_file = open('offers_IDs', 'wb')
            offers_file.close()
        except EOFError:
            pass

        print('offers_list: ', offers_dict)


    # REVIEW OFFER AND ACCEPTATION REQUEST
    def review_offer(_new_offer):
        try:
            # if _new_offer['variantId'] in acceptable_dict:
            if (_new_offer['price'] >= acceptable_dict[_new_offer['variantId']]):
                body = {
                    "name": _new_offer['id'],
                    "status": "ACCEPTED",
                    "variantId": _new_offer['variantId']
                }

                p = session.post('https://api-sell.wethenew.com/offers', json=body, headers=accept_offer_header)

                if p.status_code == 201:
                    accepted_webhook(_new_offer)
                    print('Offer ', _new_offer['id'], 'accepted - status code:', str(p.status_code))
                else:
                    print('Failed to accept offer ', _new_offer['id'], '- status code:', str(p.status_code))
        except KeyError:
            pass
        except:
            print('review_offer() ERROR')


    # READ MIN PRICES FROM CSV
    def read_acceptable_prices():
        global acceptable_dict
        acceptable_dict = {}

        try:
            with open('wtn_acceptable.csv', 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    acceptable_dict.update({int(row['PID']): int(row['MIN_PRICE'])})
            csvfile.close()
        except FileNotFoundError:
            with open('wtn_acceptable.csv', 'w', newline='') as csvfile:
                fieldnames = ['SKU', 'NAME', 'PID', 'MIN_PRICE']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
            csvfile.close()

            print('file wtn_acceptable.csv created')
            print('file wtn_acceptable.csv is empty - Only monitor function is working!')
        except EOFError:
            pass

        print('acceptable_dict: ', acceptable_dict)


    # FAILED REQUESTS HANDLING
    def failed_request(_i):
        if _i > 15:
            fail_webhook = DiscordWebhook(url=settings.webhook_url, rate_limit_retry=True,
                                          content="Too many failed requests!!! - WTN SNIPER HAS BEEN TURNED OFF")
            send_fail_webhook = fail_webhook.execute()

            sys.exit('Too many failed requests!!!')
        elif _i > 10:
            login()


    # ==================================================================================================================

    # --- MAIN ---
    load_proxies()
    restore_cookies()
    initial_request()
    read_offers()
    read_acceptable_prices()

    # ==================================================================================================================

    while True:
        rotate_proxy(ip_no)
        ip_no += 1

        try:
            r = session.get('https://api-sell.wethenew.com/offers?skip=0&take=10', headers=get_offers_header)
        except:
            print("failed to do get offers request ERROR")

        print('\nChecking for offers - status code: ', r.status_code, '\nSession proxy: ', session.proxies['https'])

        if r.status_code == 200:
            json_data = r.json()
            list_data = json_data['results']

            if list_data != "":
                for r_response_dict in list_data:
                    print(r_response_dict['id'], 'price:', r_response_dict['price'])
            else:
                print('There is no offers')
                time.sleep(delay + random.random())
                continue

            for r_response_dict in list_data:
                review_offer(r_response_dict)

                if (r_response_dict['id'], r_response_dict['price']) not in offers_dict.items():
                    offer_webhook(r_response_dict)

                    offers_dict[r_response_dict['id']] = r_response_dict['price']

                    with open('offers_IDs', 'wb') as file:
                        pickle.dump(offers_dict, file)
                    file.close()

        elif r.status_code == 429:
            print('Rate limit error 429')
            request_failed += 1
            failed_request(request_failed)
        elif r.status_code == 403:
            print('Error 403 - re-logging')
            login()
        else:
            print('Request error: ', r.status_code)
            failed_request(request_failed)

        time.sleep(delay + random.random())

# 429 jest na request, nie proxy
# 429 jest na sesję??? bo po przelogowaniu już nie wywala
# delay na ip > 10sec
# albo dwa logowania i requesty na zmiane z slrspc_token z jednego i z drugiego logowania
# (tylko czy wtedy nie wyloguje z jednego konta)

# sku w success webhook
