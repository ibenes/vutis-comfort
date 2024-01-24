#!/usr/bin/env python3

import argparse
import datetime
import os.path
import logging

from cookie_magic import get_session

import class_session


def get_aktualni_predmet_id(session, abbreviation, academic_year):
    if academic_year is None:
        today = datetime.date.today()
        if today.month in [1, 2, 3, 4, 5, 6, 7, 8]:
            academic_year = today.year - 1
        else:
            academic_year = today.year
        logging.info(f'Academic year has not been provided, estimating {academic_year} based on current date {today}')

    q = f'https://api.vut.cz/api/fit/predmety/v3?zkratka={abbreviation}'
    r = session.get(q)
    predmety = r.json()['data']['predmety']
    assert len(predmety) == 1

    desired_aktualni_predmet_id = None
    for aktualni_predmet in predmety[0]['aktualni_predmety']:
        year = aktualni_predmet['rok']
        aktualni_predmet_id = aktualni_predmet['aktualni_predmet_id']

        if year == academic_year:
            desired_aktualni_predmet_id = aktualni_predmet_id
            break

    return desired_aktualni_predmet_id


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cookie', default=f'{os.path.expanduser("~")}/.vut_cookie')
    parser.add_argument('-p', '--predmet-zkratka', required=True)
    parser.add_argument('-y', '--predmet-year', type=int)
    args = parser.parse_args()

    logging.basicConfig(level='INFO')

    session = get_session(args.cookie)
    aktualni_predmet_id = get_aktualni_predmet_id(session, args.predmet_zkratka, args.predmet_year)
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
