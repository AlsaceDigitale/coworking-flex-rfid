import binascii
import structlog
import logging
import sys
import requests
import time
import argparse

parser=argparse.ArgumentParser()
parser.add_argument('endpoint',default="https://coworking-flex.alsacedigitale.org/api")
args=parser.parse_args()

logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.DEBUG,
)

logger = structlog.get_logger()

mirror = open("/dev/mirror", "rb")

ENDPOINT=args.endpoint+"/rfid/{id}/detect"

while True:
    data = mirror.read(16)
    if data != b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
        rfid_id = binascii.hexlify(data)[4:]
        if data[0:2] == b'\x02\x01': # Puce posée
            logger.debug("Detected chip", rfid_id=rfid_id)

            json_data={
                "rfid_id": rfid_id
            }

            for i in range(5):
                logger.debug('post')
                resp=requests.post(ENDPOINT.format(id=rfid_id), json=json_data)
                logger.debug('request reply',status_code=resp.status_code)

                if resp.status_code<500:
                    break

                time.sleep(5)
     

        elif data[0:2] == b'\x02\x02': #Puce retirée
            logger.debug("Chip left", rfid_id=rfid_id)