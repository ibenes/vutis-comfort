#!/usr/bin/env python3
import argparse
import os.path
import logging
import dateutil.parser

from cookie_magic import get_session

import class_session
from prepare_empty_gsheet import get_termin_id_by_name, index_collection


def load_datafile(f):
    dataset = {}

    for line in f:
        fields = line.split()

        login = fields[0]

        if len(login) not in [8, 9]:
            raise ValueError(f"Login {login} doesn't have exactly 8 or 9 characters")

        if login in dataset:
            raise ValueError(f'Login {login} duplicated in dataset')

        # TODO max points
        # dataset[login] = min(float(fields[1]), 20.0)
        dataset[login] = float(fields[1])

    return dataset


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cookie', default=f'{os.path.expanduser("~")}/.vut_cookie')
    parser.add_argument('-p', '--predmet-zkratka', required=True)
    parser.add_argument('-y', '--predmet-year', type=int)
    parser.add_argument('-t', '--termin-name', required=True)
    parser.add_argument('--points', required=True)
    args = parser.parse_args()

    logging.basicConfig(level='INFO')

    session = get_session(args.cookie)
    aktualni_predmet_id = class_session.get_aktualni_predmet_id(session, args.predmet_zkratka, args.predmet_year)
    predmet_session = class_session.ClassSession(session, aktualni_predmet_id)

    termins = predmet_session.get_termins()
    termin_id = get_termin_id_by_name(termins, args.termin_name)

    termins = index_collection(termins, 'termin_id')
    dt = dateutil.parser.parse(termins[termin_id]['zacatek_zkousky'])
    datum = f'{dt.year}-{dt.month:02}-{dt.day:02}'

    students = predmet_session.get_termin_students(termin_id, key='login')

    with open(args.points) as f:
        data = load_datafile(f)

    for i, login in enumerate(data):
        logging.info(f"{login}, {data[login]}")
        el_index_id = students[login]['el_index_id']
        predmet_session.set_termin_points(termin_id, el_index_id, data[login], datum)


if __name__ == '__main__':
    main()
