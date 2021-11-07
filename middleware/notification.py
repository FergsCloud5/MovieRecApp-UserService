import json
import logging

import boto3

from middleware.context import get_sns_info


class Notifications:

    def __init__(self):
        key, secret, topicArn = get_sns_info()
        self.snsClient = boto3.client(
            'sns',
            aws_access_key_id=key,
            aws_secret_access_key=secret,
            region_name='us-east-1'
        )
        self.topicArn = topicArn

    def publish_message(self, subject, publish_object):

        response = self.snsClient.publish(TopicArn=self.topicArn,
                                          Message=json.dumps(publish_object),
                                          Subject=subject)

        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            # log the error return NULL
            pass

        return response["ResponseMetadata"]["HTTPStatusCode"]

    def check_user_notif(self, path, method, body, response):

        try:
            if path == "/users" and method == "POST":
                res = self.publish_message(subject="USER POSTED",
                                           publish_object=body)
                if res == 200:
                    print("Published SNS Topic: USER POSTED")
                else:
                    print("Issue with publishing to SNS Topic")
                return response

            return False
        except Exception as e:
            print("Issue with publishing SNS topic:")
            print(str(e))
            return
