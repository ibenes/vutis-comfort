#!/usr/bin/env python3

import argparse
import datetime
import os.path
import pickle
import logging

from cookie_magic import get_session


def get_el_index_map(query_res):
    students = query_res.json()['data']['studenti']

    return {s['login']: s['el_index_id'] for s in students}


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--cookie', default=f'{os.path.expanduser("~")}/.vut_cookie')
    parser.add_argument('--predmet-id', required=True)
    parser.add_argument('--zadani-id', required=True)
    parser.add_argument('--max-points', required=True, type=float)
    parser.add_argument('--bonus-points-file', required=True)
    parser.add_argument('--datum')
    parser.add_argument('points')
    args = parser.parse_args()

    if args.datum is None:
        args.datum = str(datetime.date.today())

    studeni_query = f'https://api.vut.cz/api/fit/aktualni_predmet/{args.predmet_id}/zadani/{args.zadani_id}/studenti/v3'

    session = get_session(studeni_query, args.cookie)
    r = session.get(studeni_query)

    with open(args.cookie, 'wb') as f:
        pickle.dump(session.cookies, f)

    el_index_map = get_el_index_map(r)

    points_map = {}
    bonus_map = {}
    with open(args.points) as f:
        for line in f:
            fields = line.split()
            login = fields[0]
            pts = float(fields[1])

            if pts > args.max_points:
                bonus_map[login] = pts - args.max_points
                pts = args.max_points
            points_map[login] = pts

    for login in points_map:
        hodnoceni_url = f'https://api.vut.cz/api/fit/aktualni_predmet/{args.predmet_id}/zadani/{args.zadani_id}/el_index/{el_index_map[login]}/v4'
        payload = {"POCET_BODU": points_map[login], "DATUM": args.datum}
        logging.info(f'{login}, {el_index_map[login]}, {points_map[login]}, {payload}')
        r = session.patch(hodnoceni_url, json=payload)

    if bonus_map:
        with open(args.bonus_points_file, 'w') as f:
            for login, bonus in bonus_map.items():
                f.write(f'{login} {bonus}\n')


if __name__ == '__main__':
    main()
