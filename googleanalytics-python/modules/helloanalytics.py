"""Hello Analytics Reporting API V4."""
# https://developers.google.com/analytics/devguides/reporting/core/v4/basics?hl=ja

import argparse

from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools

import json
import pprint
import pandas as pd

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')
CLIENT_SECRETS_PATH = './client_secrets.json' # Path to client_secrets.json file.

class Analytics():
    def __init__(self, viewid):
        self.viewid = viewid
        self.initialize_analyticsreporting()

    def initialize_analyticsreporting(self):
        """Initializes the analyticsreporting service object.

        Returns:
          analytics an authorized analyticsreporting service object.
        """
        # Parse command-line arguments.
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[tools.argparser])
        flags = parser.parse_args([])

        # Set up a Flow object to be used if we need to authenticate.
        flow = client.flow_from_clientsecrets(
            CLIENT_SECRETS_PATH, scope=SCOPES,
            message=tools.message_if_missing(CLIENT_SECRETS_PATH))

        # Prepare credentials, and authorize HTTP object with them.
        # If the credentials don't exist or are invalid run through the native client
        # flow. The Storage object will ensure that if successful the good
        # credentials will get written back to a file.
        storage = file.Storage('analyticsreporting.dat')
        credentials = storage.get()
        if credentials is None or credentials.invalid:
          credentials = tools.run_flow(flow, storage, flags)
        http = credentials.authorize(http=httplib2.Http())

        # Build the service object.
        self.analytics = build('analytics', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URI)

        return self.analytics

    def get_report(self, start_date, end_date, metrics, dimensions, orders, columns):
        # Use the Analytics Service Object to query the Analytics Reporting API V4.
        self.response =  self.analytics.reports().batchGet(
            body={
              'reportRequests': [
              {
                'viewId': self.viewid,
                'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                'metrics': metrics,
                'dimensions': dimensions,
                'orderBys': orders
              }]
            }
        ).execute()
        
        df = self.print_response(self.response, columns)
        return df

    def print_response(self, response, columns):
        """Parses and prints the Analytics Reporting API V4 response"""
        tmp = list()
        a = columns
        # 第2引数はnullだった時のデフォルト値
        # pprint.pprint(response.get('reports')[0].get('data').get('rows'))
        for i in response.get('reports')[0].get('data').get('rows'):
            adr_dict = dict(zip(a, i.get('dimensions') + i.get('metrics')[0].get('values')))
            tmp.append(adr_dict)
        df = pd.io.json.json_normalize(tmp)
        return df
