#! python
# -*- coding: utf-8 -*-
# ================================================================================
# ACUMOS
# ================================================================================
# Copyright © 2017 AT&T Intellectual Property & Tech Mahindra. All rights reserved.
# ================================================================================
# This Acumos software file is distributed by AT&T and Tech Mahindra
# under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ================================================================================
import os
from flask import Flask, jsonify
from flask import request
import requests
import json
import logging
from logging.handlers import RotatingFileHandler
from flask import abort
from flasgger import Swagger
import time
from datetime import datetime

app = Flask(__name__)
swagger = Swagger(app)

# Validation task types = SS, LS, TA, OQ

tasks = []
data = {
    'status': None,
    'artifactValidationStatus': [
        {'artifactTaskId': None,
         'status': None,
         'artifactId': None}
    ],
    'taskId': None
}

# Definition of URLs
URL_PORTAL = os.environ.get('URL_PORTAL', None)
URL_ONBOARDING_CONTROLLER = os.environ.get('URL_ONBOARDING_CONTROLLER', None)


# POST verb usage
@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json:
        abort(400)

    task = {
        'solutionId': request.json["solutionId"],
        'revisionId': request.json["revisionId"],
        'visibility': request.json['visibility'],
        'artifactValidations': request.json['artifactValidations'],
        'task_details': request.json["task_details"],
        'trackingId': request.json["trackingId"],
        'userId': request.json["userId"]
    }

    portal_base_url = (URL_PORTAL, task['task_details']['principle_task_id'])
    portal_task_url = '/'.join(portal_base_url)

    # getting virus scan task status and sending back to backend portal
    if 'virus_task_id' in task['task_details']:
        if task['task_details']["state"] != "":
            data['status'] = task['task_details']["status"]
            data['taskId'] = task['task_details']['principle_task_id']
            data['solutionId'] = task['solutionId']
            data['revisionId'] = task['revisionId']
            data['visibility'] = task['visibility']

            data['artifactValidationStatus'][0]['status'] = task['task_details']["result"]
            data['artifactValidationStatus'][0]['artifactTaskId'] = task['task_details']['virus_task_id']
            data['artifactValidationStatus'][0]['artifactId'] = task['task_details']['artifactId']
            data['artifactValidationStatus'][0]['validationTaskType'] = "SS"

            requests.put(portal_task_url, json.dumps(data), headers={"Content-type": "application/json; charset=utf8"})
            task['task_details']['name'] = 'SecurityScan'
            update_onboarding(task)

    # getting license scan task status and sending back to backend portal
    if 'license_task_id' in task['task_details']:
        if task['task_details']["state"] != "":
            data['status'] = task['task_details']["status"]
            data['taskId'] = task['task_details']['principle_task_id']
            data['solutionId'] = task['solutionId']
            data['revisionId'] = task['revisionId']
            data['visibility'] = task['visibility']

            data['artifactValidationStatus'][0]['status'] = task['task_details']["result"]
            data['artifactValidationStatus'][0]['artifactTaskId'] = task['task_details']['license_task_id']
            data['artifactValidationStatus'][0]['artifactId'] = task['task_details']['artifactId']
            data['artifactValidationStatus'][0]['validationTaskType'] = "LS"

            requests.put(portal_task_url, json.dumps(data), headers={"Content-type": "application/json; charset=utf8"})
            task['task_details']['name'] = 'LicenseCheck'
            update_onboarding(task)

    # getting keyword scan task status
    if 'text_task_id' in task['task_details']:
        if task['task_details']["state"] != "":
            data['status'] = task['task_details']["status"]
            data['taskId'] = task['task_details']['principle_task_id']
            data['solutionId'] = task['solutionId']
            data['revisionId'] = task['revisionId']
            data['visibility'] = task['visibility']

            data['artifactValidationStatus'][0]['status'] = task['task_details']["result"]
            data['artifactValidationStatus'][0]['artifactTaskId'] = task['task_details']['text_task_id']
            data['artifactValidationStatus'][0]['artifactId'] = task['task_details']['artifactId']
            data['artifactValidationStatus'][0]['validationTaskType'] = "TA"
            requests.put(portal_task_url, json.dumps(data), headers={"Content-type": "application/json; charset=utf8"})
            task['task_details']['name'] = 'TextCheck'
            update_onboarding(task)

    return "done", 201


def update_onboarding(task):
    if task['task_details']['state'] == 'STARTED':
        data['statusCode'] = 'ST'
    elif task['task_details']['state'] == 'FAILURE ':
        data['statusCode'] = 'FA'
    elif task['task_details']['state'] == 'SUCCESS ':
        data['statusCode'] = 'SU'
    else:
        data['statusCode'] = 'SU'

    data['artifactId'] = task['task_details']['artifactId']
    data['name'] = task['task_details']['name']
    data['result'] = task['task_details']['result']
    data['revisionId'] = task['revisionId']
    data['solutionId'] = task['solutionId']
    data['startDate'] = str(datetime.now().isoformat())
    data['endDate'] = str(datetime.now().isoformat())
    data['stepCode'] = 'VL'
    data['trackingId'] = task['trackingId']
    data['userId'] = task['userId']
    return requests.put(URL_ONBOARDING_CONTROLLER, json.dumps(data), headers={"Content-type": "application/json; charset=utf8"})


# Invoke the logger
@app.after_request
def after_request(response):
    if response.status_code != 500:
        ts = time.strftime('%Y-%b-%d %H:%M')
        logger.error('%s | %s | %s %s %s | %s',
                     ts,
                     request.remote_addr,
                     request.method,
                     request.scheme,
                     request.full_path,
                     response.status)
    return response


@app.errorhandler(Exception)
def exceptions(e):
    ts = time.strftime('%Y-%b-%d %H:%M')
    # tb = traceback.format_exc()
    message = [str(x) for x in e.args]
    logger.error('%s | %s | %s %s %s | %s',
                 ts,
                 request.remote_addr,
                 request.method,
                 request.scheme,
                 request.full_path,
                 message)
    success = False
    response = {
        'success': success,
        'error': {
            'type': e.__class__.__name__,
            'message': message
        }
    }
    return jsonify(response), 500, {'content-type': 'application/json'}


if __name__ == '__main__':
    # The maxBytes is set to this number, in order to demonstrate the generation of multiple log files (backupCount).
    handler = RotatingFileHandler('validation_middleware.log', maxBytes=1024*1024*100, backupCount=3)
    logger = logging.getLogger('__name__')
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)

    app.run(host="0.0.0.0", port=9604)
