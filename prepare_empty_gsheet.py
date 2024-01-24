#!/usr/bin/env python3

import argparse
import os.path
import logging
import sys

from cookie_magic import get_session

import class_session


def index_collection(collection, key):
    return {item[key]: item for item in collection}


def format_line(items):
    return '\t'.join(items) + '\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cookie', default=f'{os.path.expanduser("~")}/.vut_cookie')
    parser.add_argument('-p', '--predmet-zkratka', required=True)
    parser.add_argument('-y', '--predmet-year', type=int)
    parser.add_argument('-t', '--termin-id', type=int, required=True)
    parser.add_argument('-q', '--nb-questions', type=int, required=True)
    parser.add_argument('--no-assignment-variant', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(level='INFO')

    session = get_session(args.cookie)
    aktualni_predmet_id = class_session.get_aktualni_predmet_id(session, args.predmet_zkratka, args.predmet_year)
    predmet_session = class_session.ClassSession(session, aktualni_predmet_id)

    terminy_ids = predmet_session.get_termins()

    students_all = index_collection(predmet_session.get_students(), 'student_id')
    students_termin = predmet_session.get_termin_students(args.termin_id)

    header = ['login', *[str(i+1) for i in range(args.nb_questions)], 'login', 'name']
    if not args.no_assignment_variant:
        header.insert(1, 'variant')
    sys.stdout.write(format_line(header))
    for s_id in students_termin:
        s_info = students_all[s_id]

        line = [s_info['login'], *['' for _ in range(args.nb_questions)], s_info['login'], s_info['label_pr']]
        if not args.no_assignment_variant:
            line.insert(1, '')

        sys.stdout.write(format_line(line))


if __name__ == '__main__':
    main()
