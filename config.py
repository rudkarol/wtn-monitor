import yaml


class Config:
    def __init__(self):
        try:
            with open('config.yaml', 'r') as cookies_file:
                config_dict = yaml.load(cookies_file, Loader=yaml.Loader)
                self.webhook_url = config_dict['webhook_url']
                self.session_token = config_dict['__Secure-next-auth.session-token']

                delay = int(config_dict['delay'])

                if delay <= 0:
                    raise ValueError('config.yaml file contains incorrect delay value')
                else:
                    self.delay = delay
        except FileNotFoundError:
            with open('config.yaml', 'w') as cookies_file:
                data = {
                    '__Secure-next-auth.session-token': '',
                    'delay': '5',
                    'webhook_url': ''
                }

                yaml.dump(data, cookies_file)

            raise FileNotFoundError('config.yaml file does not exist! File created')
        except KeyError:
            raise KeyError('config.yaml file contains incorrect data')

    def get_webhook_url(self):
        return self.webhook_url

    def get_delay(self):
        return self.delay

    def get_token(self) -> dict[str, str]:
        return {'__Secure-next-auth.session-token': self.session_token}
