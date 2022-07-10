import json
import os
import httplib2
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets, HttpAccessTokenRefreshError
from oauth2client.file import Storage

OAUTH_SCOPE = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/fitness.activity.write',
    'https://www.googleapis.com/auth/fitness.body.write'
]
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


class google_fit_api:

    def __init__(self):
        self.oauth_file_path = '.secret/oauth2.json'
        self.credentials_file = ".secret/credentials"
        self.google_fit_service = self.authorization()

    def authorization(self):
        if os.path.exists(self.credentials_file):
            credentials = Storage(self.credentials_file).get()
        else:
            flow = flow_from_clientsecrets(
                self.oauth_file_path,
                scope=OAUTH_SCOPE,
                redirect_uri=REDIRECT_URI)

            authorize_url = flow.step1_get_authorize_url()
            print('Put below URL to the Browser.')
            print(authorize_url)

            code = input('Input Code: ').strip()
            credentials = flow.step2_exchange(code)

            if not os.path.exists(self.credentials_file):
                Storage(self.credentials_file).put(credentials)

        http = credentials.authorize(httplib2.Http())
        service = build('fitness', 'v1', http=http, cache_discovery=False)

        return service

    @staticmethod
    def execute_request(request):
        try:
            return request.execute()
        except HttpError as e:
            print(json.loads(e.content)['error']['code'])
            print(json.loads(e.content)['error']['message'])
            print(json.loads(e.content)['error']['status'])
            exit()
        except HttpAccessTokenRefreshError as e:
            print(e.__class__.__name__)
            print(e)
            exit()

    def create_data_source(self, data_name, val_type, app_name, app_version,
                           datatype_name, datatype_field_name, datatype_field_format):

        request = self.google_fit_service.users().dataSources().create(
            userId='me',
            body={
                "dataStreamName": data_name,
                "type": val_type,
                "application": {
                    "name": app_name,
                    "version": app_version
                },
                "dataType": {
                    "name": datatype_name,
                    "field": [
                        {
                            "name": datatype_field_name,
                            "format": datatype_field_format
                        }
                    ]
                },
            })

        return self.execute_request(request)

    def delete_data_source(self, dataSourceId):
        request = self.google_fit_service.users().dataSources().delete(
            userId='me',
            dataSourceId=dataSourceId
        )
        return self.execute_request(request)

    def insert_data_point(self, data_source_id, data_type_name, input_date, input_value):

        start = int(datetime(input_date.year, input_date.month, input_date.day, 0, 0, 0).timestamp() * 1000_000_000)
        end = int(datetime(input_date.year, input_date.month, input_date.day, 23, 59, 59).timestamp() * 1000_000_000)
        up = int(input_date.timestamp() * 1000000000)
        data_set = "%s-%s" % (start, end)

        request = self.google_fit_service.users().dataSources().datasets().patch(
            userId='me',
            dataSourceId=data_source_id,
            datasetId=data_set,
            body={
                "dataSourceId": data_source_id,
                "maxEndTimeNs": end,
                "minStartTimeNs": start,
                "point": [{
                    'startTimeNanos': up,
                    'endTimeNanos': up,
                    'dataTypeName': data_type_name,
                    'value': [{
                        'fpVal': input_value
                    }]
                }]
            })

        return self.execute_request(request)

    def delete_data_point(self, data_source_id, start_date, end_date):

        start = int(start_date.timestamp() * 1000_000_000)
        end = int(end_date.timestamp() * 1000_000_000)
        data_set = "%s-%s" % (start, end)

        request = self.google_fit_service.users().dataSources().datasets().delete(
            userId='me',
            dataSourceId=data_source_id,
            datasetId=data_set
        )

        return self.execute_request(request)

    def get_datasource_list(self):
        data_list_file = 'data/datasource_list.json'

        request = self.google_fit_service.users().dataSources().list(userId='me')
        data_list = self.execute_request(request)

        with open(data_list_file, 'w') as f:
            json.dump(data_list, f, indent=4)

        return data_list

    def get_data_one_day(self, data_source_id, input_date):
        start = int(datetime(input_date.year, input_date.month, input_date.day, 0, 0, 0).timestamp() * 1000000000)
        end = int(datetime(input_date.year, input_date.month, input_date.day, 23, 59, 59).timestamp() * 1000000000)
        data_set = "%s-%s" % (start, end)

        request = self.google_fit_service.users().dataSources().datasets().get(
            userId='me',
            dataSourceId=data_source_id,
            datasetId=data_set
        )

        return self.execute_request(request)

    def get_data_multi_days(self, data_source_id, data_type_name, start_day, end_day):
        start = int(datetime(start_day.year, start_day.month, start_day.day, 0, 0, 0).timestamp()) * 1000
        end = int(datetime(end_day.year, end_day.month, end_day.day, 23, 59, 59).timestamp()) * 1000

        request = self.google_fit_service.users().dataset().aggregate(
            userId="me",
            body={
                "aggregateBy": [{
                    "dataTypeName": data_type_name,
                    "dataSourceId": data_source_id
                }],
                "bucketByTime": {
                    "durationMillis": 86400000
                },
                "startTimeMillis": start,
                "endTimeMillis": end
            })

        return self.execute_request(request)
