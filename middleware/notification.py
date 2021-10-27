import json
import logging


class Notifications:

    def __init__(self, snsClient, topicArn):
        self.snsClient = snsClient
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
                print("Published SNS Topic: USER POSTED")
                return response

            return False
        except Exception as e:
            print("Issue with publishing SNS topic:")
            print(str(e))
            return
