# -*- coding: utf-8 -*-
import urllib.parse
import os
import flask
from flask import abort, request, redirect
import tempfile
import requests
import logging
import json
import csv
import xmltodict
import re
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from telegram.ext import Updater, CommandHandler
from telegram import ParseMode


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

# TOKEN var for elon_bot
TOKEN = os.environ["TELEGRAM_BOT"]


@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}
    if request.method == 'POST':
        try:
            url = request.form['url']
            return redirect('csv/' + url)
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
    return print_index_table()



@app.route('/json/<video>')
def json_captions(video):
    info_url = "https://www.youtube.com/get_video_info?video_id=" + video  # fU5X0cUMHac
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
        if len(captions) > 0:
            response_xml = requests.get(captions[0]["baseUrl"])
            video_details["CaptionData"] = xmltodict.parse(response_xml.text)
            return video_details
        return flask.jsonify(response.text)
    return response.status_code


def get_video(videoId):
    info_url = "https://www.youtube.com/get_video_info?video_id=" + videoId  # fU5X0cUMHac
    response = requests.get(info_url)
    if response.status_code == 200:
        parsed = urllib.parse.parse_qs(response.text)
        player_response = json.loads(parsed["player_response"][0])
        video_details = player_response["videoDetails"]
        if "captions" in player_response:
            captions = player_response["captions"]["playerCaptionsTracklistRenderer"]["captionTracks"]
            video_details["captions"] = captions
            if len(captions) > 0:
                response_xml = requests.get(captions[0]["baseUrl"])
                video_details["CaptionData"] = json.dumps(xmltodict.parse(response_xml.text))
        else:
            video_details["captions"] = {}
            video_details["CaptionData"] = {}
        return video_details
    else:
        return None


@app.route('/csv/<video>')
def csv_captions(video):
    video_details = []
    if "," in video:
        videos = video.split(",")
        for vid in video.split(","):
            if vid is not None and len(vid) > 4:
                dets = get_video(vid)
                if dets is not None:
                    video_details.append(dets)
        file_name = "data.csv"
    else:
        tmp = get_video(video)
        if tmp is None:
            abort(404)
        file_name = tmp["videoId"] + ".csv"
        video_details.append(tmp)

    try:
        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tmp")
        file_path = os.path.join(dir_path, file_name)
        fields = list(video_details[0].keys())
        if "keywords" not in fields:
            fields.append("keywords")
        if "isLowLatencyLiveStream" not in fields:
            fields.append("isLowLatencyLiveStream")
        if "latencyClass" not in fields:
            fields.append("latencyClass")
        with open(os.path.join(dir_path, file_name), 'w', encoding='utf-8-sig', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields, quotechar='"', quoting=csv.QUOTE_NONNUMERIC )
            writer.writeheader()
            for vid_det in video_details:
                writer.writerow(vid_det)
        return flask.send_from_directory(directory=dir_path, filename=file_name, as_attachment=True)
    except Exception as e:
        print("I/O error:" + str(e))
        abort(500)

    return abort(400)


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def print_index_table():
    return ('<table>' +
            '<tr><td><a href="/csv/dKHlY_grLDM,EQHb-ydSAV8,CFmM-vXH5F4,i1H8tuBLuWc,wMhex3CKC9c,0OksvP4nqek,p06YWEY36Jg,OcqC86vIwDs,TObXX28aE1M,lm-w7hVQpM4,hh9ktcnX5gg,oiDxmQEoS-g,sonx24bvMOo,etJkpBlElZI,ngBRRS6Sf0c,20_3BxUjXJo,_-9m0P0KuP8,Uxx5_QyXIKE,AeA5A6tb5Uk,nTJhNnfnsgI,LNHychYJ-6s,3f-q_yFsD1A,tTG4etv5Gi8,vY36Hxbafzo,lkKR4cz6nts,ODhRubWiPnQ,dW04jBwvZ9g,SB2KcJqejPM,SZD57UbsopA,S2KimmWo7Gc,pEOcAhWuTiE,za9rvKM3EE4,Wp7j7UfDJFM,Rn5a_ZPXKDM,VWFkW8G0YUI,H4I4YrfByp8,Yu_TQGMU60E,EZYtNOBw_58,9Au8a9FwZ48,PZyd4wWLp4w,ES1VD1E5I70,UrHhCsful4c,qTtzj8RF_V0,jjcvLH30RXI,N6nbQozepIQ,GSIUJVoXzSU,7IzaFW1jZ6o,LrykUOeuPfc,FYKheujTqE4,UFwyoYOPzLQ,ge1Nm5KNV4A,-FRJ38E7Ioo,E2aXOSJEc6M,IYQcULqe798,v1hmFu_61iM">Get a CSV of Captions</a></td>' +
            '<td>Add Your Own To Test, Change Url to /csv/<video_id>.</td></tr>' +
            '<tr><td><a href="/csv/dKHlY_grLDM,EQHb-ydSAV8,CFmM-vXH5F4,fU5X0cUMHac">Get a CSV of Captions</a></td>' +
            '<td>Add Your Own To Test, Change Url to /csv/<video_id>.</td></tr>' +
            '<tr><td><a href="/json/CFmM-vXH5F4">Get a JSON of Captions</a></td>' +
            '<td>Add Your Own To Test, Change Url to /json/<video_id>.</td></tr>' +
            '<div style="padding:50px"><form method="post">'
            '<textarea name="url" style="width:600px; height: 200px; maxlength="4000"; display:none;" placeholder="dKHlY_grLDM,EQHb-ydSAV8,CFmM-vXH5F4,i1H8tuBLuWc,wMhex3CKC9c">' +
            '</textarea></br>' +
            '<input type="submit" name="comment101" value="Get CSV" />' +
            '</form></div>' +
            '</table>')

def getUrl():
    #obtain a json object with image details
    #extract image url from the json object
    contents = requests.get('https://api.thecatapi.com/v1/images/search')
    js = contents.json()
    print(js)
    url = js[0]["url"]
    return url

def sendImage(update, context):
    url = getUrl()
    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id=chat_id, photo=url)

def sendTable(update, context):
    name = update.effective_user.first_name
    if "josh" in name.lower():
        update.message.reply_text(f'Hello {update.effective_user.first_name}, you are Jelly Hands')
    else:
        update.message.reply_text(f'Hello {update.effective_user.first_name}, you are HODLing strong')

def prices(update, context):
    mains = ["BTC", "ETH", "LTC", "ADA", "AAVE", "DOGE"]
    out = ""
    for l in mains:
        p, c = get_price(l)
        out = out + f"_{l}_ ${round(p,4)} {round(c,1)}% 1 hour \n"
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text=out.replace(".", "\\."), parse_mode=ParseMode.MARKDOWN_V2)

def get_price(label):
    price, change_1hr = "", ""
    logging.error("DOWNLOADING " + label)    
    try:
        url = "https://data.messari.io/api/v1/assets/" + label + "/metrics"
        resp = requests.get(url)
        js = resp.json()
        price = js["data"]["market_data"]["price_usd"]
        change_1hr = js["data"]["market_data"]["percent_change_usd_last_1_hour"]
    except Exception as e:
        logging.error(e)
    return price, change_1hr

def error_callback(bot, error):
    logging.warning(str(error))


updater = Updater(TOKEN)
#call sendImage() when the user types a command in the telegram chat
updater.dispatcher.add_handler(CommandHandler('doge',sendImage))
updater.dispatcher.add_handler(CommandHandler('me',sendTable))
updater.dispatcher.add_handler(CommandHandler('lambo',prices))
updater.dispatcher.add_handler(CommandHandler('greendildos',prices))

# Register it to the updater's dispatcher
updater.dispatcher.add_error_handler(error_callback)

#start the bot
updater.start_polling()
updater.idle()


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    app.run('localhost', 8080, debug=True)
