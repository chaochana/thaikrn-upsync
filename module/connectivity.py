import mysql.connector
import requests
import logging
import json
import configparser
from retry_requests import retry


config = configparser.ConfigParser()
config.read('config.ini')


def sql(query):
    db = mysql.connector.connect(
        host=config['MySQL']['host'],
        user=config['MySQL']['username'],
        passwd=config['MySQL']['password'],
        database=config['MySQL']['database']
    )

    cursor = db.cursor()
    cursor.execute(query)

    return cursor.fetchall()


def gql(query, variables):
    url = config['GraphQL']['url']
    secret = config['GraphQL']['secret']
    headers = {'Content-Type': 'application/json', 'x-hasura-admin-secret': '%s' % secret}

    my_session = retry(retries=10)
    r = my_session.post(url, json={'query': query, 'variables': variables}, headers=headers)

    if r.status_code == 200:
        r_json = json.loads(r.text)
        logging.debug("Response" + str(r_json))
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(requests.status_code, query))

    return r.text


def gql_insert_member(variables):
    insert_query = """
        mutation insert_member (
          $id : bigint,
          $title : String,
          $name : String,
          $lastname : String,
          $gender : String,
          $note : String,
          $date_applied : date
        ) {
          insert_member (
            objects: {
              id: $id, 
              title: $title,
              name: $name, 
              lastname: $lastname,
              gender: $gender, 
              note: $note, 
              date_applied: $date_applied}) {
            returning {
              date_applied
              gender
              id
              lastname
              name
              note
              title
            }
          }
        }
    """

    return gql(insert_query, variables)


def gql_insert_medication(variables):
    insert_query = """
        mutation insert_order(
          $transaction_id: bigint,
          $member_id: bigint,
          $order: json,
          $order_date: date,
          $queue: Int,
          $session: String,
          $type: String
            ) {
          insert_order(
            objects: {
              id: $transaction_id,
              member_id: $member_id, 
              order: $order, 
              order_date: $order_date, 
              queue: $queue, 
              session: $session,
              type: $type 
            }) {
            returning {
              id
              member_id
              order
              order_date
              queue
              session
              type
              updated_at
              created_at
            }
          }
        }
    """

    return gql(insert_query, variables)


def gql_max_member():
    max_member_query = """
    query max_member {
      member_aggregate {
        aggregate {
          max {
            id
          }
        }
      }
    }
    """

    variables = {}

    response = gql(max_member_query, variables)

    r_json = json.loads(response)

    return int(r_json['data']['member_aggregate']['aggregate']['max']['id'])


def sql_max_member():
    query = "SELECT MAX(MemberID) FROM member"

    response = sql(query)

    return int(response[0][0])


def gql_max_order_by_date(date):
    max_order_query = """
      query MaxOrderQuery (
                $date: date
              ) {
        order_aggregate(where: {order_date: {_eq: $date}}) {
          aggregate {
            max {
              id
            }
          }
        }
      }
    """

    variables = { "date": date }

    response = gql(max_order_query, variables)

    r_json = json.loads(response)

    if ( r_json['data']['order_aggregate']['aggregate']['max']['id'] != None ):
      return int(r_json['data']['order_aggregate']['aggregate']['max']['id'])
    else:
      return 0


def sql_max_order_by_date(date):
    query = "SELECT MAX(Transaction_ID) FROM `medicinetransaction` WHERE DATE_IDX = '{}'".format(date.replace('-', ''))

    response = sql(query)

    return int(response[0][0])


def sql_medication_by_date(date, local_max_order):
    logging.info('{} {}'.format(date, local_max_order))
    return sql("SELECT Transaction_ID, MemberID, Queue, Queue_Session, Transaction_Type FROM `medicinetransaction` WHERE DATE_IDX = '{}' AND Transaction_ID > {} ORDER BY Transaction_ID".format(date.replace('-', ''), local_max_order))


def get_sql_medication_detail_by_id(id):
    return sql("SELECT med.MedicineID, med_order.Amount, med_order.Add_Amount, med_order.special FROM `medicineorder` med_order, `medicine` med WHERE med_order.`MedicineID` = med.`MedicineID` AND Transaction_ID = {}".format(id))
