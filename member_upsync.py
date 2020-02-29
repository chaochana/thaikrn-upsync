import requests
import json

query = """
query {
  member {
    title,
    name,
    lastname
  }
}
"""
url = 'http://34.87.74.244:8080/v1/graphql'
secret = 'Karuna2485'
headers = {'Content-Type': 'application/json', 'x-hasura-admin-secret': '%s' % secret}

print("Hello World")

try:
    print("make a request")
    r = requests.post(url, json={'query': query}, headers=headers)
except:
    print("Cannot make a request")

if r.status_code == 200:
    print("Good")
    r_json = json.loads(r.text)
    print(str(r_json))
else:
    raise Exception("Query failed to run by returning code")