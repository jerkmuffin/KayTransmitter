import os
import sys
import json
import time
import boto3
import logging
import requests
import playsound
import gpio_ctrl
import secret_codes


logger = logging.getLogger('Consumer_Log')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('log/consumer.log')
fh.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

fmat = logging.Formatter('%(asctime)s - %(message)s')

fh.setFormatter(fmat)

logger.addHandler(ch)
logger.addHandler(fh)


# Reflector
access="AKIAJ5CT5LR3LZDEETGA"
secret = secret_codes.secret


sqs = boto3.resource('sqs', region_name='us-east-1', aws_access_key_id=access, aws_secret_access_key=secret)
queue = sqs.get_queue_by_name(QueueName='recordings.fifo')

def download_and_write_to_disk(url):
    logger.debug("download and write: {}".format(url))
    r = requests.get(url)
    open(os.path.basename(url), 'w').write(r.content)
    logger.info("wrote file: {}".format(os.path.basename(url)))
    #play file?

def send_timestamp(uuid):
    send_url = "https://unit9:kayjewellers-beamyourlove@beam-your-love-staging.netlify.com/.netlify/functions/server/beamed"
    now = int(time.time())
    logger.info('the time is now: {}'.format(now))
    r = requests.post(send_url, json={"recordingID":uuid, "beamTimestamp":now})
    if r.status_code == 200:
        logger.info("Timestamp sent to API---file: {} | timestamp: {}".format(uuid, now))
        return
    else:
        print(r.json())
        #retry


def transmit_mp3_into_space(uuid):
    f = os.path.basename(uuid)
    logger.info("playing mp3: {}".format(f))
    gpio_ctrl.ptt_on()
    playsound.playsound(f)
    gpio_ctrl.ptt_off()

while True:
    try:
        for message in queue.receive_messages():
            json_ob = json.loads(message.body)
            logger.debug("Incoming from SQS")
            logger.info("Message: {}".format(json_ob))
            try:
                message.delete()
            except:
                queue.reload()
                logger.error("UNABLE TO DELETE MESAGE FROM QUEUE")
            #print("I have recieved data!\nfile: {}\nID: {}".format(json_ob['file'], json_ob['recordingID']))
            download_and_write_to_disk(json_ob['file'])
            status = send_timestamp(json_ob['recordingID'])
            try:
                transmit_mp3_into_space(json_ob['file'])
                logger.info("done playing file")
                logger.info("files left in queue: {}".format(len(queue.receive_messages())))
            except Exception as e:
                print(e)
    except KeyboardInterrupt:
        print('\npretty exit')
        sys.exit(1)
