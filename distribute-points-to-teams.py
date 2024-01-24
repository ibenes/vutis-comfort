#!/usr/bin/env python3

import argparse
import logging


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('teams_file')
    parser.add_argument('points_file')
    args = parser.parse_args()

    points_dict = {}
    with open(args.points_file) as f:
        for i, line in enumerate(f):
            try:
                fields = line.split()
                points_dict[fields[0]] = float(fields[1])
            except Exception:
                logging.error(f'Failed to parse line {i+1} of the points file: "{line}"')
                raise

    with open(args.teams_file) as f:
        for line in f:
            fields = line.split()
            for member in fields[1:]:
                try:
                    print(member, points_dict[fields[0]])
                except Exception:
                    logging.warning(f'Could not assign points to {member} of team {fields[0]}')


if __name__ == '__main__':
    main()
