import configparser
import logging
from module.connectivity import *
from datetime import datetime

logging.basicConfig(level=logging.INFO)

config = configparser.ConfigParser()
config.read('config.ini')

order_date = str(datetime.today().strftime('%Y-%m-%d'))

for medication in sql_medication_by_date(order_date):
    logging.info(str(medication))

    transaction_id = medication[0]
    member_id = medication[1]
    queue = medication[2]
    session = medication[3]
    order_type = medication[4]

    order = []

    for medication_order in (get_sql_medication_detail_by_id(transaction_id)):
        order.append({'medicine_id': medication_order[0], 'amount': medication_order[1], 'add_amount': medication_order[2], 'special': medication_order[3]})

    variables = {
        "member_id": member_id,
        "order": str(json.dumps(order)),
        "order_date": order_date,
        "queue": queue,
        "session": session,
        "type": order_type
    }

    logging.debug("member_id: {}, order: {}, order_date: {}, queue: {}, session: {}, type: {}".format(member_id, order, order_date, queue, session, order_type))

    response = gql_insert_medication(variables)

    logging.info("[INSERT MEDICATION GQL] : " + str(response))