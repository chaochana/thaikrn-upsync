import requests
import json
import mysql.connector
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

mydb = mysql.connector.connect(
  host=config['MySQL']['host'],
  user=config['MySQL']['username'],
  passwd=config['MySQL']['password'],
  database=config['MySQL']['database']
)

mycursor = mydb.cursor()

mycursor.execute("SELECT * FROM member WHERE MemberID=1")

myresult = mycursor.fetchall()

for x in myresult:
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

    # print(member_id)
    # print(title)
    # print(name)
    # print(lastname)
    # print(gender)
    # print(date_applied)
    # print(note)

    query = """
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

    variables = {
        "id": member_id,
        "title": title,
        "name": name,
        "lastname": lastname,
        "gender": gender,
        "note": note,
        "date_applied": date_applied
    }

    url = config['GraphQL']['url']
    secret = config['GraphQL']['secret']
    headers = {'Content-Type': 'application/json', 'x-hasura-admin-secret': '%s' % secret}

    r = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)

    if r.status_code == 200:
        r_json = json.loads(r.text)
        print(str(r_json))
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(requests.status_code, query))