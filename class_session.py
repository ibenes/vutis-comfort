import datetime
import logging


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


class ClassSession:
    def __init__(self, butis_session, predmet_id):
        self.session = butis_session
        self.predmet_id = predmet_id

    def get_termin_points(self, termin_id, el_index_id):
        hodnoceni_query_template = 'https://api.vut.cz/api/fit/aktualni_predmet/{}/termin/{}/el_index/{}/v3'
        hq = hodnoceni_query_template.format(self.predmet_id, termin_id, el_index_id)
        r = self.session.get(hq)

        try:
            student_data = r.json()['data']['studenti'][0]
            body = student_data['pocet_bodu']
        except KeyError:
            body = None

        return body

    def get_termin_students(self, termin_id, key='per_id'):
        query = f'https://api.vut.cz/api/fit/aktualni_predmet/{self.predmet_id}/termin/{termin_id}/studenti/v3'
        r = self.session.get(query)

        students = r.json()['data']['studenti']
        return [s[key] for s in students]

    def get_termins(self):
        terminy_query = f'https://api.vut.cz/api/fit/aktualni_predmet/{self.predmet_id}/terminy/v3'
        r = self.session.get(terminy_query)
        this_class = r.json()['data']['predmety'][0]['aktualni_predmety'][0]
        assert this_class['aktualni_predmet_id'] == self.predmet_id

        terminy_ids = []
        for classification_item in this_class['zkousky']:
            for instance in classification_item['terminy']:
                terminy_ids.append(instance['termin_id'])
                logging.info(f"{classification_item['zkouska_projekt_nazev']}, {instance['termin_nazev']}, instance['zacatek_zkousky'], {instance['termin_id']}")

        return terminy_ids

    def get_zadani_points(self, zadani_id, el_index_id):
        query = f'https://api.vut.cz/api/fit/aktualni_predmet/{self.predmet_id}/zadani/{zadani_id}/el_index/{el_index_id}/v4'
        r = self.session.get(query)

        try:
            student_data = r.json()['data']['studenti'][0]
            body = student_data['pocet_bodu']
        except KeyError:
            body = None

        return body

    def get_zadanis(self):
        query = f'https://api.vut.cz/api/fit/aktualni_predmet/{self.predmet_id}/zadani/v3'
        r = self.session.get(query)

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
        if predmet['aktualni_predmet_id'] != self.predmet_id:
            raise ValueError(f'Unexpectedly, class {predmet["aktualni_predmet_id"]} was returned')

        zadanis = predmet['zkousky']

        zadani_ids = []
        for zadani in zadanis:
            for instance in zadani['zadani']:
                zadani_ids.append(instance['zadani_id'])
                print(zadani['zkouska_projekt_nazev'], instance['zadani_nazev'])

        return zadani_ids

    def get_students(self):
        studeni_query = f'https://api.vut.cz/api/fit/aktualni_predmet/{self.predmet_id}/studenti/zapsani/v3'
        r = self.session.get(studeni_query)
        studenti = r.json()['data']['studenti']

        return studenti

    def get_student_details(self, el_index_id):
        detail_query = f'https://api.vut.cz/api/fit/aktualni_predmet/{self.predmet_id}/el_index/{el_index_id}/v3'
        r = self.session.get(detail_query)
        student_data = r.json()['data']['student'][0]
        login = student_data['login']
        body_celkem = student_data['bodove_hodnoceni']

        return login, body_celkem
