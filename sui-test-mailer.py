#!/usr/bin/env python3
import smtplib
from email.message import EmailMessage
import logging
import sys

import time


HEADER = '\n'.join((
    'Dobry den,',
    'nize najdete body z jednotlivych otazek na pulsemestralce. Zadani je v Moodlu ve Starych zadanich.',
    'Otazku prvni a druhou opravovala doc. Burget, treti dr. Hradis, ostatni moje malickost. Burget.',
    'Kazda otazka byla hodnocena na skale 0--4 body, prepocet na cilovou hodnotu vidite az jako post-processing.',
    '',
    'S pozdravem,',
    'Karel Benes',
))


def load_datafile(f):
    dataset = {}

    for line in f:
        fields = line.strip().split('\t')

        login = fields[0]

        if len(login) not in [8, 9]:
            raise ValueError(f"Login {login} doesn't have exactly 8 or 9 characters")

        if login in dataset:
            raise ValueError(f'Login {login} duplicated in dataset')

        try:
            df = [fields[id] for id in [0, 1, 2, 3, 4, 5, 6, 7, 10, 11]]
            dataset[login] = f'{df[0]}, sk {df[7]}: {df[1]} {df[2]} {df[3]} {df[4]} {df[5]} {df[6]}. Suma {df[8]}, normalizovano {float(df[9]):.2f}.'
        except Exception:
            logging.warning(f'Skipping login {login}: {line.strip()}')

    return dataset


def get_email_body(login, line):
    body = HEADER + '\n\n' + line

    return body


def main():
    data = load_datafile(sys.stdin)
    myself = 'ibenes@fit.vutbr.cz'

    for i, login in enumerate(data):
        print('login', login)
        msg = EmailMessage()
        msg['Subject'] = '[SUI] Body z pulsemestralky po otazkach'
        msg['From'] = myself
        msg['To'] = f'{login}@stud.fit.vutbr.cz'
        msg['Cc'] = myself
        msg.set_content(get_email_body(login, data[login]))

        print(msg)

        with smtplib.SMTP('kazi.fit.vutbr.cz') as s:
            s.send_message(msg)
        time.sleep(10)

if __name__ == '__main__':
    main()
