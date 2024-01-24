#!/usr/bin/env python3

import argparse
import os.path
import logging

from cookie_magic import get_session


def get_el_index_map(query_res):
    students = query_res.json()['data']['studenti']

    return {s['login']: s['el_index_id'] for s in students}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cookie', default=f'{os.path.expanduser("~")}/.vut_cookie')
    parser.add_argument('--predmet-id', type=int, required=True)
    args = parser.parse_args()

    logging.basicConfig(level='INFO')

    studeni_query = f'https://api.vut.cz/api/fit/aktualni_predmet/{args.predmet_id}/studenti/zapsani/v3'

    session = get_session(args.cookie)
    r = session.get(studeni_query)

    studenti = r.json()['data']['studenti']

    terminy_query = f'https://api.vut.cz/api/fit/aktualni_predmet/{args.predmet_id}/terminy/v3'
    r = session.get(terminy_query)
    this_class = r.json()['data']['predmety'][0]['aktualni_predmety'][0]
    assert this_class['aktualni_predmet_id'] == args.predmet_id

    terminy_ids = []
    for classification_item in this_class['zkousky']:
        for instance in classification_item['terminy']:
            terminy_ids.append(instance['termin_id'])
            print(classification_item['zkouska_projekt_nazev'], instance['termin_nazev'], instance['zacatek_zkousky'])

    hodnoceni_query_template = 'https://api.vut.cz/api/fit/aktualni_predmet/{}/termin/{}/el_index/{}/v3'

    for student in studenti:
        el_index_id = student['el_index_id']

        detail_query = f'https://api.vut.cz/api/fit/aktualni_predmet/{args.predmet_id}/el_index/{el_index_id}/v3'
        r = session.get(detail_query)
        student_data = r.json()['data']['student'][0]
        login = student_data['login']
        body_celkem = student_data['bodove_hodnoceni']

        points_all = []
        for termin_id in terminy_ids:
            hq = hodnoceni_query_template.format(args.predmet_id, termin_id, el_index_id)
            r = session.get(hq)

            try:
                student_data = r.json()['data']['studenti'][0]
                body = student_data['pocet_bodu']
            except KeyError:
                body = None

            points_all.append(body)

        print(login, body_celkem, points_all)


if __name__ == '__main__':
    main()
