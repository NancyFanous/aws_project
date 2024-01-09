import json
from collections import Counter
import flask
from flask import request
import os
from bot import ObjectDetectionBot
import boto3
from googletrans import Translator

app = flask.Flask(__name__)


# TODO load TELEGRAM_TOKEN value from Secret Manager
secret_name = "nancyf_telegram_token"
client = boto3.client('secretsmanager', region_name='eu-north-1')
response = client.get_secret_value(SecretId=secret_name)
response_json = json.loads(response['SecretString'])


TELEGRAM_TOKEN = response_json['TELEGRAM_TOKEN']

print(TELEGRAM_TOKEN)

TELEGRAM_APP_URL = os.environ['TELEGRAM_APP_URL']


@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'


@app.route(f'/results/', methods=['GET'])
def results():
    prediction_id = request.args.get('prediction_id')

    # TODO use the prediction_id to retrieve results from DynamoDB and send to the end-user
    dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')
    table = dynamodb.Table('nancyf_tb')

    response_item = table.get_item(
        Key={
            'prediction_id': prediction_id
        }
    )
    chat_id = request.args.get('chat_id')
    text_results = response_item
    labels_string = response_item.get('Item', {}).get('labels', [])
    labels = json.loads(labels_string)

    class_counts = Counter(item['class'] for item in labels)
    res = json.dumps(dict(class_counts))
    formatted_output = "\n".join([f"{key}: {value}" for key, value in class_counts.items()])
    translator = Translator() # google translate API (translate the result to arb and heb)
    translated_to_arabic = translator.translate(formatted_output, dest='ar').text
    translated_to_hebrew = translator.translate(formatted_output, dest='he').text

    bot.send_text(chat_id, formatted_output)
    bot.send_text(chat_id, translated_to_arabic)
    bot.send_text(chat_id, translated_to_hebrew)


   # bot.send_text(chat_id, text_results)
    return 'Ok'


@app.route(f'/loadTest/', methods=['POST'])
def load_test():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'


if __name__ == "__main__":
    bot = ObjectDetectionBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)
    app.run(host='0.0.0.0', port=8443)
