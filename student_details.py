#!/usr/bin/env python3

import argparse
import os.path
import logging

from cookie_magic import get_session

import class_session


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cookie', default=f'{os.path.expanduser("~")}/.vut_cookie')
    parser.add_argument('-p', '--predmet-zkratka', required=True)
    parser.add_argument('-y', '--predmet-year', type=int)
    args = parser.parse_args()

    logging.basicConfig(level='INFO')

    session = get_session(args.cookie)
    aktualni_predmet_id = class_session.get_aktualni_predmet_id(session, args.predmet_zkratka, args.predmet_year)
    predmet_session = class_session.ClassSession(session, aktualni_predmet_id)

    studenti = predmet_session.get_students()
    terminy_ids = predmet_session.get_termins()

    zadani_ids = predmet_session.get_zadanis()

    for student in studenti:
        el_index_id = student['el_index_id']

        login, body_celkem = predmet_session.get_student_details(el_index_id)
        points_termins = [predmet_session.get_termin_points(termin_id, el_index_id) for termin_id in terminy_ids]
        points_zadanis = [predmet_session.get_zadani_points(zadani_id, el_index_id) for zadani_id in zadani_ids]

        print(login, body_celkem, points_termins, points_zadanis)


if __name__ == '__main__':
    main()
