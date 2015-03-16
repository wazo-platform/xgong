from ConfigParser import ConfigParser

DEFAULT_CONFIG = '/etc/xgong/config.ini'


def load_config():
    config = ConfigParser()
    config.read(['/etc/xgong/config.ini'])
    return config
