#!/usr/bin/env python3

import argparse
import os.path
import pickle
import logging
import sys

from cookie_magic import get_session


def print_tymy(file, tymy_data):
    for tym in tymy_data:
        nazev = tym['vedouci_login']
        clenove = [clen['clen_login'] for clen in tym['clenove']]

        print(nazev, *clenove, file=file)


def get_skupina_tymu(session, predmet_id, skupina_name):
    skupiny_query = f"https://api.vut.cz/api/fit/aktualni_predmet/{predmet_id}/skupiny-tymu/v3?lang=cs"
    r = session.get(skupiny_query)

    d = r.json()["data"]

    matching_skupiny = [s for s in d['predmety'][0]['aktualni_predmety'][0]['skupiny_tymu'] if s['nazev'] == skupina_name]
    if not matching_skupiny:
        raise ValueError('Not found any skupina matching "args.skupina_tymu"')
    assert len(matching_skupiny) == 1

    return matching_skupiny[0]


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--predmet-id', required=True)
    parser.add_argument('--skupina-tymu', required=True)
    parser.add_argument('--out-file')
    parser.add_argument('--cookie', default=f'{os.path.expanduser("~")}/.vut_cookie')
    args = parser.parse_args()

    skupiny_query = f"https://api.vut.cz/api/fit/aktualni_predmet/{args.predmet_id}/skupiny-tymu/v3?lang=cs"

    session = get_session(skupiny_query, args.cookie)
    r = session.get(skupiny_query)

    with open(args.cookie, 'wb') as f:
        pickle.dump(session.cookies, f)

    skupina = get_skupina_tymu(session, args.predmet_id, args.skupina_tymu)
    logging.info(skupina)
    skupina_id = skupina['aktualni_predmet_skupina_tymu_id']
    tymy_query = f"https://api.vut.cz/api/fit/aktualni_predmet/{args.predmet_id}/skupina_tymu/{skupina_id}/tymy/v3?clenove=1"

    r = session.get(tymy_query)
    assert r.status_code == 200, f"Chyba pristupu {r}"
    d = r.json()["data"]

    tymy_data = d['predmety'][0]['aktualni_predmety'][0]['skupiny_tymu'][0]['tymy']

    if args.out_file:
        with open(args.out_file, 'w') as f:
            print_tymy(f, tymy_data)
    else:
        print_tymy(sys.stdout, tymy_data)


if __name__ == '__main__':
    main()
