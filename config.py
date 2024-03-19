import yaml


class Config:
    def __init__(self):
        try:
            with open('config.yaml', 'r') as cookies_file:
                settings_dict = yaml.load(cookies_file, Loader=yaml.Loader)
                self.webhook_url = settings_dict['webhook_url']

                delay = int(settings_dict['delay'])

                if delay <= 0:
                    raise ValueError('config.yaml file contains incorrect delay value')
                else:
                    self.delay = delay
        except FileNotFoundError:
            with open('config.yaml', 'w') as cookies_file:
                data = {
                    'webhook_url': '',
                    'delay': '5'
                }

                yaml.dump(data, cookies_file)

            raise FileNotFoundError('config.yaml file does not exist! File created')
        except KeyError:
            raise KeyError('config.yaml file contains incorrect data')

    def get_webhook_url(self):
        return self.webhook_url

    def get_delay(self):
        return self.delay
