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


def get_zadani_points(session, predmet_id, zadani_id, el_index_id):
    query = f'https://api.vut.cz/api/fit/aktualni_predmet/{predmet_id}/zadani/{zadani_id}/el_index/{el_index_id}/v4'
    r = session.get(query)

    try:
        student_data = r.json()['data']['studenti'][0]
        body = student_data['pocet_bodu']
    except KeyError:
        body = None

    return body


def get_zadanis(session, predmet_id):
    query = f'https://api.vut.cz/api/fit/aktualni_predmet/{predmet_id}/zadani/v3'
    r = session.get(query)

    # this is -- probably -- the general class, i.e. not tied to a year
    predmety = r.json()['data']['predmety']
    if len(predmety) != 1:
        raise ValueError(f'Unexpectedly, got {len(predmety)} classes in the response, expected one')

    predmet = predmety[0]

    # yes, the API response is structured like this
    predmety = predmet['aktualni_predmety']
    if len(predmety) != 1:
        raise ValueError(f'Unexpectedly, got {len(predmety)} classes in the response, expected one')

    predmet = predmety[0]
    if predmet['aktualni_predmet_id'] != predmet_id:
        raise ValueError(f'Unexpectedly, class {predmet["aktualni_predmet_id"]} was returned')

    zadanis = predmet['zkousky']

    zadani_ids = []
    for zadani in zadanis:
        for instance in zadani['zadani']:
            zadani_ids.append(instance['zadani_id'])
            print(zadani['zkouska_projekt_nazev'], instance['zadani_nazev'])

    return zadani_ids


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

    zadani_ids = get_zadanis(session, args.predmet_id)

    for student in studenti:
        el_index_id = student['el_index_id']

        login, body_celkem = get_student_details(session, args.predmet_id, el_index_id)
        points_termins = [get_termin_points(session, args.predmet_id, termin_id, el_index_id) for termin_id in terminy_ids]

        points_zadanis = [get_zadani_points(session, args.predmet_id, zadani_id, el_index_id) for zadani_id in zadani_ids]

        print(login, body_celkem, points_termins, points_zadanis)


if __name__ == '__main__':
    main()
