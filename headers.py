def get_offers_header(access_token: str) -> dict[str, str]:
    return {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'pl;q=0.7',
        'authorization': 'Bearer ' + access_token,
        'pragma': 'no-cache',
        'sec-ch-ua': r'"Chromium";v="120", "Not(A:Brand";v="24", "Brave";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': r'"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'x-xss-protection': '1;mode=block'
    }


def accept_offer_header(access_token: str) -> dict[str, str]:
    return {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'pl;q=0.7',
        'authorization': 'Bearer ' + access_token,
        'content-type': 'application/json',
        'pragma': 'no-cache',
        'sec-ch-ua': r'"Chromium";v="120", "Not(A:Brand";v="24", "Brave";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': r'"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'x-xss-protection': '1;mode=block'
    }
