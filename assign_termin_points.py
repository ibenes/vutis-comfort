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


def float_or_none(x):
    try:
        parsed = float(x)
    except ValueError:
        parsed = None

    return parsed


class MessageFormatter:
    def __init__(self, first_question_idx, nb_questions, separator='\t', group_sizes=None):
        self.first_question_idx = first_question_idx
        self.nb_questions = nb_questions
        self.separator = separator

        if group_sizes is not None:
            if sum(group_sizes) != nb_questions:
                raise ValueError(f"Group sizes {group_sizes} don't sum up to the given number of {nb_questions} questions")
        self.group_sizes = group_sizes

    def process(self, line):
        fields = line.split(self.separator)
        login = fields[0]
        sum_field = fields[-2]
        norm_field = fields[-1]

        question_fields = fields[self.first_question_idx:(self.first_question_idx+self.nb_questions)]
        question_floats = [float_or_none(x) for x in question_fields]
        nb_nones = sum([x is None for x in question_floats])

        if nb_nones == 0:
            pass  # good, all are numbers
        elif nb_nones == self.nb_questions:
            logging.warning(f'No question data for {login}')
            return None
        else:
            raise ValueError(f'Partial line for {login} malformed: {line}')

        if self.group_sizes:
            group_start = 0
            group_transcripts = []
            for group_size in self.group_sizes:
                group_transcripts.append(' '.join(question_fields[group_start:group_start+group_size]))
                group_start += group_size
            message = ' -- '.join(group_transcripts)
        else:
            message = ' '.join(question_fields)

        summary = f'Celkem {sum_field}, po normalizaci {norm_field}'

        return f'{login}\n{message}\n{summary}\n'


def load_full_datafile(f, message_formatter):
    dataset = {}

    for line in f:
        assert line[-1] == '\n'
        line = line[:-1]
        fields = line.split('\t')

        login = fields[0]

        if len(login) not in [8, 9]:
            raise ValueError(f"Login {login} doesn't have exactly 8 or 9 characters")

        if login in dataset:
            raise ValueError(f'Login {login} duplicated in dataset')

        message = message_formatter.process(line)

        # TODO max points
        # dataset[login] = min(float(fields[1]), 20.0)

        sum_field = fields[-1]
        if sum_field == '':
            continue

        dataset[login] = float(sum_field), message

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

    message_formatter = MessageFormatter(2, 14, group_sizes=[4, 4, 6])
    with open(args.points) as f:
        data = load_full_datafile(f, message_formatter)

    session = get_session(args.cookie)
    aktualni_predmet_id = class_session.get_aktualni_predmet_id(session, args.predmet_zkratka, args.predmet_year)
    predmet_session = class_session.ClassSession(session, aktualni_predmet_id)

    termins = predmet_session.get_termins()
    termin_id = get_termin_id_by_name(termins, args.termin_name)

    termins = index_collection(termins, 'termin_id')
    dt = dateutil.parser.parse(termins[termin_id]['zacatek_zkousky'])
    datum = f'{dt.year}-{dt.month:02}-{dt.day:02}'

    students = predmet_session.get_termin_students(termin_id, key='login')

    for i, login in enumerate(data):
        logging.info(f"{login}, {data[login]}")
        el_index_id = students[login]['el_index_id']

        points, message = data[login]
        predmet_session.set_termin_points(termin_id, el_index_id, points, datum, custom_message=message)


if __name__ == '__main__':
    main()
