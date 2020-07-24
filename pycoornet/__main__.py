from .app import App
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    App.run()
    App.get_ct_shares()
    #App.get_shares()
