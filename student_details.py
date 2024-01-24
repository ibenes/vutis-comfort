#!/usr/bin/env python3

import argparse
import os.path
import logging

from cookie_magic import get_session


def get_termin_points(session, predmet_id, termin_id, el_index_id):
    hodnoceni_query_template = 'https://api.vut.cz/api/fit/aktualni_predmet/{}/termin/{}/el_index/{}/v3'
    hq = hodnoceni_query_template.format(predmet_id, termin_id, el_index_id)
    r = session.get(hq)

    try:
        student_data = r.json()['data']['studenti'][0]
        body = student_data['pocet_bodu']
    except KeyError:
        body = None

    return body


def get_termins(session, predmet_id):
    terminy_query = f'https://api.vut.cz/api/fit/aktualni_predmet/{predmet_id}/terminy/v3'
    r = session.get(terminy_query)
    this_class = r.json()['data']['predmety'][0]['aktualni_predmety'][0]
    assert this_class['aktualni_predmet_id'] == predmet_id

    terminy_ids = []
    for classification_item in this_class['zkousky']:
        for instance in classification_item['terminy']:
            terminy_ids.append(instance['termin_id'])
            print(classification_item['zkouska_projekt_nazev'], instance['termin_nazev'], instance['zacatek_zkousky'])

    return terminy_ids


def get_students(session, predmet_id):
    studeni_query = f'https://api.vut.cz/api/fit/aktualni_predmet/{predmet_id}/studenti/zapsani/v3'
    r = session.get(studeni_query)
    studenti = r.json()['data']['studenti']

    return studenti


def get_student_details(session, predmet_id, el_index_id):
    detail_query = f'https://api.vut.cz/api/fit/aktualni_predmet/{predmet_id}/el_index/{el_index_id}/v3'
    r = session.get(detail_query)
    student_data = r.json()['data']['student'][0]
    login = student_data['login']
    body_celkem = student_data['bodove_hodnoceni']

    return login, body_celkem


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cookie', default=f'{os.path.expanduser("~")}/.vut_cookie')
    parser.add_argument('--predmet-id', type=int, required=True)
    args = parser.parse_args()

    logging.basicConfig(level='INFO')

    session = get_session(args.cookie)

    studenti = get_students(session, args.predmet_id)
    terminy_ids = get_termins(session, args.predmet_id)

    for student in studenti:
        el_index_id = student['el_index_id']

        login, body_celkem = get_student_details(session, args.predmet_id, el_index_id)
        points_all = [get_termin_points(session, args.predmet_id, termin_id, el_index_id) for termin_id in terminy_ids]

        print(login, body_celkem, points_all)


if __name__ == '__main__':
    main()
