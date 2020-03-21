import json
import configparser
import logging
from module.connectivity import *


logging.basicConfig(filename='member.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

config = configparser.ConfigParser()
config.read('config.ini')

remote_max_member = gql_max_member()
local_max_member = sql_max_member()

if local_max_member <= remote_max_member:
    logging.info("[INFO] No new user, sync abort")
else:
    logging.info("[INFO] New local user found, do sync")
    for x in sql("SELECT * FROM member WHERE MemberID > {}".format(remote_max_member)):
        member_id = str(x[0])
        title = str(x[6])
        name = str(x[7])
        lastname = str(x[8])
        gender = str(x[5])
        date_applied = str(x[1])
        note = str(x[26])

        if date_applied == "None" or date_applied == "":
            date_applied = None

        if note == "None" or note == "":
            note = None

        if title == "None" or title == "":
            title = None

        variables = {
            'id': member_id,
            'title': title,
            'name': name,
            'lastname': lastname,
            'gender': gender,
            'date_applied': date_applied,
            'note': note
        }

        logging.debug("member_id: {}, title: {}, name: {}, lastname: {}, gender: {}, date_applied: {}, note: {}".format(member_id, title, name, lastname, gender, date_applied, note))

        response = gql_insert_member(variables)

        logging.info("[INSERT GQL] : " + str(response))
