#!/usr/bin/env python3

import argparse
import os.path
import logging
import string
import sys

from cookie_magic import get_session

import class_session


def index_collection(collection, key):
    return {item[key]: item for item in collection}


def format_line(items):
    return '\t'.join(items) + '\n'


COLUMN_NAMES = string.ascii_uppercase


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cookie', default=f'{os.path.expanduser("~")}/.vut_cookie')
    parser.add_argument('-p', '--predmet-zkratka', required=True)
    parser.add_argument('-y', '--predmet-year', type=int)
    parser.add_argument('-t', '--termin-id', type=int, required=True)
    parser.add_argument('-q', '--nb-questions', type=int, required=True)
    args = parser.parse_args()

    logging.basicConfig(level='INFO')

    session = get_session(args.cookie)
    aktualni_predmet_id = class_session.get_aktualni_predmet_id(session, args.predmet_zkratka, args.predmet_year)
    predmet_session = class_session.ClassSession(session, aktualni_predmet_id)

    terminy_ids = predmet_session.get_termins()

    students_all = index_collection(predmet_session.get_students(), 'student_id')
    students_termin = predmet_session.get_termin_students(args.termin_id)

    header = ['login', 'variant', *[str(i+1) for i in range(args.nb_questions)], 'login', 'name', 'sum', 'norm']
    nb_columns = len(header)
    sys.stdout.write(format_line(header))

    first_data_column = 2
    last_data_column = 2 + args.nb_questions - 1
    first_letter = COLUMN_NAMES[first_data_column]
    last_letter = COLUMN_NAMES[last_data_column]
    sum_formula_template = f'=if({first_letter}{{row_no}}="", "", sum({first_letter}{{row_no}}:{last_letter}{{row_no}}))'

    sum_column = COLUMN_NAMES[2 + args.nb_questions + 2]
    norm_formula_template = f'=if({sum_column}{{row_no}}="", "", {sum_column}{{row_no}} / (14 * 4) * 60)'

    for row_no, s_id in enumerate(students_termin, start=2):
        s_info = students_all[s_id]

        line = [s_info['login'], '', *['' for _ in range(args.nb_questions)], s_info['login'], s_info['label_pr'], sum_formula_template.format(row_no=row_no), norm_formula_template.format(row_no=row_no)]
        assert len(line) == nb_columns, f'Line with login {s_info["login"]} has {len(line)} items, expected {nb_columns}'

        sys.stdout.write(format_line(line))

    first_data_row = 2
    last_data_row = 2 + len(students_termin) - 1

    single_question_range = f'{{col_letter}}{first_data_row}:{{col_letter}}{last_data_row}'
    aggregation_formulas = [
        ('max', f'=max({single_question_range})'),
        ('avg', f'=average({single_question_range})'),
        ('min', f'=min({single_question_range})'),
    ]

    def produce_column_agregation_lines(name, formula):
        columns_with_agg = list(range(first_data_column, last_data_column+1)) + [last_data_column+2, last_data_column+3]
        return [formula.format(col_letter=COLUMN_NAMES[i]) if i in columns_with_agg else '' for i in range(nb_columns)]

    for name, formula in aggregation_formulas:
        agg_line = produce_column_agregation_lines(name, formula)
        sys.stdout.write(format_line(agg_line))


if __name__ == '__main__':
    main()
