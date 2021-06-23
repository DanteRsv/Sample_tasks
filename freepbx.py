from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
import requests


class FreePBX:

    def __init__(self, base_url, client_id, client_secret):
        self.base_url = base_url
        self.token_url = self.base_url + '/admin/api/api/token'
        self.users_url = self.base_url + '/admin/api/api/rest/userman/users'
        self.gql_url = self.base_url + '/admin/api/api/gql'
        self.client_id = client_id
        self.client_secret = client_secret


    def generate_token(self):
        oauth = OAuth2Session(client=BackendApplicationClient(client_id=self.client_id))
        token = oauth.fetch_token(token_url=self.token_url, auth=HTTPBasicAuth(self.client_id, self.client_secret))
        return token.get('access_token')

    def http_request(self):
        token = self.generate_token()
        headers = {'Authorization': token}
        response = requests.get(self.users_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code

    def client_connect(self):
        token = self.generate_token()
        headers = {'Authorization': token}
        transport = AIOHTTPTransport(url=self.gql_url, headers=headers)

        client = Client(
            transport=transport,
            fetch_schema_from_transport=True
        )
        return client

    def get_entry(self, key, value):
        response = self.http_request()
        for entry in response:
            if entry.get(key) == value:
                return entry

    def get_entry_by_number(self, number):
        return self.get_entry('default_extension', number)

    def get_entry_by_displayname(self, displayname):
        return self.get_entry('displayname', displayname)

    def create_extension(self, phone, fullname, email):
        client = self.client_connect()
        query = gql(
            """mutation ($phone: ID!, $email: String!, $fullname: String!) {
                addExtension(
                    input: {
                        extensionId: $phone
                        name: $fullname
                        tech: "pjsip"
                        email: $email
                        umGroups: "1"
                        clientMutationId: "Riko"
                        }
                    )
                    {
                        status
                        message
                        clientMutationId
                    }}
                """)

        params = {'fullname': fullname,
                  'email': email,
                  'phone': phone}

        result = client.execute(query, variable_values=params)
        return result

    def update_extension(self, phone, fullname, email):
        client = self.client_connect()
        query = gql(
            """mutation ($phone: ID!, $email: String!, $fullname: String!) {
                updateExtension(
                    input: {
                        extensionId: $phone
                        name: $fullname
                        tech: "pjsip"
                        email: $email
                        umGroups: "1"
                        clientMutationId: "Riko"
                        }
                    ) {
                        status
                        message
                        clientMutationId
                    }}
                """)

        params = {'fullname': fullname,
                  'email': email,
                  'phone': phone}

        result = client.execute(query, variable_values=params)
        return result

    def delete_extension(self, phone):
        client = self.client_connect()
        query = gql(
            """mutation ($phone: ID!) {
                deleteExtension(
                    input: {
                        extensionId: $phone
                        clientMutationId: "Riko"
                        }
                    ) {
                        status
                        message
                        clientMutationId
                    }}
                """)

        params = {
                  'phone': phone
        }

        result = client.execute(query, variable_values=params)
        return result
