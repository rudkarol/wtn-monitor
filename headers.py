access_token_header = {
    'Accept': 'application/json, text/html, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
    'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}


def get_offers_header(access_token: str) -> dict:
    return {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'Authorization': 'Bearer ' + access_token,
        'Origin': 'https://sell.wethenew.com',
        # 'Sec-Fetch-Dest:': 'empty',
        # 'Sec-Fetch-Mode:': 'cors',
        # 'Sec-Fetch-Site:': 'same-site',
        # 'Sec-Fetch-User:': '?1',
        # 'Upgrade-Insecure-Requests': '1',
        'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }


def accept_offer_header(access_token) -> dict:
    return {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json',
        'Origin': 'https://sell.wethenew.com',
        'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }