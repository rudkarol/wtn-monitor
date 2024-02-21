import settings
from proxy import Load_proxies, Rotate_proxy


session = tls_client.Session(client_identifier="chrome_120", random_tls_extension_order=True)

proxies = Load_proxies()
Rotate_proxy(session, proxies)
