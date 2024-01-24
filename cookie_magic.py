import requests
import getpass
import logging
import pickle


def create_authenticated_session():
    user = input("Zadejte uzivatele IS VUT: ")
    passwd = getpass.getpass("Zadejte heslo do IS VUT: ")

    session = requests.Session()
    session.auth = (user, passwd)

    return session


class NonWorkingCookie(Exception):
    pass


def create_cookie_session(cookie_fn):
    session = requests.Session()

    with open(cookie_fn, 'rb') as f:
        session.cookies.update(pickle.load(f))

    return session


def get_session(cookie_fn=None):
    if cookie_fn:
        try:
            logging.info(f'BUT cookie present, attempting to use it...')
            session = create_cookie_session(cookie_fn)

            r = session.get('https://api.vut.cz/api/fit/predmety/v3')
            if r.status_code == 200:
                logging.info(f'Success!')
            else:
                logging.warning(f'Failed to create a session with the cookie, got {r}')
                raise NonWorkingCookie

            return session
        except (FileNotFoundError, NonWorkingCookie):
            logging.info(f'Creating a new cookie')
            session = create_authenticated_session()

            r = session.get('https://api.vut.cz/api/fit/predmety/v3')

        with open(cookie_fn, 'wb') as f:
            pickle.dump(session.cookies, f)

        return session
    else:
        return create_authenticated_session()
