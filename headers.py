def get_offers_header(access_token: str) -> dict:
    return {
        'authority': 'api-sell.wethenew.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'pl;q=0.5',
        'authorization': 'Bearer ' + access_token,
        'origin': 'https://sell.wethenew.com',
        'pragma': 'no-cache',
        'referer': 'https://sell.wethenew.com/',
        'sec-ch-ua': r'"Chromium";v="120", "Not(A:Brand";v="24", "Brave";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': r'"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-xss-protection': '1;mode=block'
    }


def accept_offer_header(access_token: str) -> dict:
    return {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json',
        'Origin': 'https://sell.wethenew.com',
        'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }