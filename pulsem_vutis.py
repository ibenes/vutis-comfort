#!/usr/bin/env python3

import argparse
import os.path
import logging
import pickle

from cookie_magic import get_session


def get_el_index_map(query_res):
    students = query_res.json()['data']['studenti']

    return {s['login']: s['el_index_id'] for s in students}


def load_datafile(f):
    dataset = {}

    for line in f:
        fields = line.split()

        login = fields[0]

        if len(login) not in [8, 9]:
            raise ValueError(f"Login {login} doesn't have exactly 8 or 9 characters")

        if login in dataset:
            raise ValueError(f'Login {login} duplicated in dataset')

        dataset[login] = min(float(fields[1]), 20.0)

    return dataset


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cookie', default=f'{os.path.expanduser("~")}/.vut_cookie')
    parser.add_argument('--predmet-id', required=True)
    parser.add_argument('--cely-termin-id', required=True)
    parser.add_argument('--termin-id', required=True)
    parser.add_argument('points')
    args = parser.parse_args()

    studeni_query = f'https://api.vut.cz/api/fit/aktualni_predmet/{args.predmet_id}/termin/{args.cely_termin_id}/studenti/v3'
    terminy_query = f'https://api.vut.cz/api/fit/aktualni_predmet/{args.predmet_id}/terminy/v3'

    session = get_session(studeni_query, args.cookie)
    r = session.get(studeni_query)

    # t_r = session.get(terminy_query)
    # import IPython; IPython.embed()

    with open(args.cookie, 'wb') as f:
        pickle.dump(session.cookies, f)

    el_index_map = get_el_index_map(r)

    with open(args.points) as f:
        data = load_datafile(f)

    for i, login in enumerate(data):
        prihlaseni_url = f'https://api.vut.cz/api/fit/aktualni_predmet/{args.predmet_id}/termin/{args.cely_termin_id}/zkouska_termin/{args.termin_id}/el_index/{el_index_map[login]}/v4'
        r = session.post(prihlaseni_url)
        if r.status_code != 200:
            logging.warning(f'Failed to register student {login}: {r.status_code} {r.json()}')

        hodnoceni_url = f'https://api.vut.cz/api/fit/aktualni_predmet/{args.predmet_id}/termin/{args.cely_termin_id}/zkouska_termin/{args.termin_id}/el_index/{el_index_map[login]}/v3'
        payload = {"POCET_BODU": data[login], "DATUM": "2023-11-28"}
        print(login, el_index_map[login], data[login], payload)
        r = session.patch(hodnoceni_url, json=payload)

        if r.status_code != 200:
            logging.warning(f'Failed to save points for {login}: {r.status_code} {r.json()}')


if __name__ == '__main__':
    main()
