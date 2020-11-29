# -*- coding: utf-8 -*-
import urllib.parse
import os
import flask
import requests
import json
import xmltodict
import re
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = 'sdfas2345tsrgtsdf'


@app.route('/')
def index():
  return print_index_table()

@app.route('/captions/<video>')
def test_captions(video):
    info_url = "https://www.youtube.com/get_video_info?video_id=" + video #fU5X0cUMHac
    response = requests.get(info_url)
    if response.status_code == 200:
        left_identifier = "captionTracks"
        right_identifier = "isTranslatable"
        pattern_string = re.escape(left_identifier) + "(.*?)" + re.escape(right_identifier)
        pattern = re.compile(pattern_string)
        m = pattern.search(response.text)
        parsed = urllib.parse.parse_qs(response.text)
        dd = parsed["player_response"][0]
        jj = json.loads(dd)
        captions = jj["captions"]["playerCaptionsTracklistRenderer"]["captionTracks"]
        video_details = jj["videoDetails"]
        video_details["captions"] = captions
        if len(captions) > 0 :
            response_xml = requests.get(captions[0]["baseUrl"])
            video_details["CaptionData"] = xmltodict.parse(response_xml.text)
            return video_details
        return flask.jsonify(response.text)
    return response.status_code

# @app.route('/test')
# def test_api_request():
#   if 'credentials' not in flask.session:
#     return flask.redirect('authorize')
#
#   # Load credentials from the session.
#   credentials = google.oauth2.credentials.Credentials(
#       **flask.session['credentials'])
#
#   youtube = googleapiclient.discovery.build(
#       API_SERVICE_NAME, API_VERSION, credentials=credentials)
#
#   request = youtube.channels().list(
#       part="snippet,contentDetails,statistics",
#       id="UC_x5XG1OV2P6uZZ5FSM9Ttw"
#   )
#   response = request.execute()
#
#   print(response)
#
#   # Save credentials back to session in case access token was refreshed.
#   # ACTION ITEM: In a production app, you likely want to save these
#   #              credentials in a persistent database instead.
#   flask.session['credentials'] = credentials_to_dict(credentials)
#
#   return flask.jsonify(response)
#
# @app.route('/authorize')
# def authorize():
#   # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
#   flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
#       CLIENT_SECRETS_FILE, scopes=SCOPES)
#
#   # The URI created here must exactly match one of the authorized redirect URIs
#   # for the OAuth 2.0 client, which you configured in the API Console. If this
#   # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
#   # error.
#   flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
#
#   authorization_url, state = flow.authorization_url(
#       # Enable offline access so that you can refresh an access token without
#       # re-prompting the user for permission. Recommended for web server apps.
#       access_type='offline',
#       # Enable incremental authorization. Recommended as a best practice.
#       include_granted_scopes='true')
#
#   # Store the state so the callback can verify the auth server response.
#   flask.session['state'] = state
#
#   return flask.redirect(authorization_url)
#
#
# @app.route('/oauth2callback')
# def oauth2callback():
#   # Specify the state when creating the flow in the callback so that it can
#   # verified in the authorization server response.
#   state = flask.session['state']
#
#   flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
#       CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
#   flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
#
#   # Use the authorization server's response to fetch the OAuth 2.0 tokens.
#   authorization_response = flask.request.url
#   flow.fetch_token(authorization_response=authorization_response)
#
#   # Store credentials in the session.
#   # ACTION ITEM: In a production app, you likely want to save these
#   #              credentials in a persistent database instead.
#   credentials = flow.credentials
#   flask.session['credentials'] = credentials_to_dict(credentials)
#
#   return flask.redirect(flask.url_for('test_api_request'))
#
#
# @app.route('/revoke')
# def revoke():
#   if 'credentials' not in flask.session:
#     return ('You need to <a href="/authorize">authorize</a> before ' +
#             'testing the code to revoke credentials.')
#
#   credentials = google.oauth2.credentials.Credentials(
#     **flask.session['credentials'])
#
#   revoke = requests.post('https://oauth2.googleapis.com/revoke',
#       params={'token': credentials.token},
#       headers = {'content-type': 'application/x-www-form-urlencoded'})
#
#   status_code = getattr(revoke, 'status_code')
#   if status_code == 200:
#     return('Credentials successfully revoked.' + print_index_table())
#   else:
#     return('An error occurred.' + print_index_table())
#
#
# @app.route('/clear')
# def clear_credentials():
#   if 'credentials' in flask.session:
#     del flask.session['credentials']
#   return ('Credentials have been cleared.<br><br>' +
#           print_index_table())


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/captions/fU5X0cUMHac">Test an capture request</a></td>' +
          '<td>Add Your Own To Test, Change Url to /captions/<video_id>.</td></tr>' +
          '</table>')


if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  app.run('localhost', 8080, debug=True)