import mysql.connector
import requests
import logging
import json
import configparser


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

    r = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)

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
