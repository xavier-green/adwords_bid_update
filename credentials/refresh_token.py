#!/usr/bin/env python
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Generates refresh token for AdWords using the Installed Application flow."""


import argparse
import sys

from oauth2client import client

# Your OAuth2 Client ID and Secret. If you do not have an ID and Secret yet,
# please go to https://console.developers.google.com and create a set.
DEFAULT_CLIENT_ID = "600258979154-rmnptdl9b4lcr0to35t12nqlgkj96ij8.apps.googleusercontent.com"
DEFAULT_CLIENT_SECRET = "FV1ys2xKsnvsok6rZ3r_Nh06"

# The AdWords API OAuth2 scope.
SCOPES = ['https://www.googleapis.com/auth/adwords','https://www.googleapis.com/auth/spreadsheets.readonly']


def main(client_id, client_secret, scopes):
  """Retrieve and display the access and refresh token."""
  flow = client.OAuth2WebServerFlow(
      client_id=client_id,
      client_secret=client_secret,
      scope=scopes,
      user_agent='Ads Python Client Library',
      redirect_uri='urn:ietf:wg:oauth:2.0:oob')

  authorize_url = flow.step1_get_authorize_url()

  print(('Log into the Google Account you use to access your AdWords account'
         'and go to the following URL: \n%s\n' % (authorize_url)))
  print('After approving the token enter the verification code (if specified).')
  code = input('Code: ').strip()

  try:
    credential = flow.step2_exchange(code)
  except client.FlowExchangeError as e:
    print('Authentication has failed: %s' % e)
    sys.exit(1)
  else:
    print(('OAuth2 authorization successful!\n\n'
           'Your access token is:\n %s\n\nYour refresh token is:\n %s'
           % (credential.access_token, credential.refresh_token)))


if __name__ == '__main__':
  configured_scopes = SCOPES
  main(DEFAULT_CLIENT_ID, DEFAULT_CLIENT_SECRET, configured_scopes)
