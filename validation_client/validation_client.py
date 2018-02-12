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
import requests
import logging
from logging.handlers import RotatingFileHandler
from flask import request
from flask import abort
import json
from flasgger import Swagger


app = Flask(__name__)
swagger = Swagger(app)


tasks = []

# Definition of URLs
URL_INVOKE_TASK = os.environ['URL_INVOKE_TASK']
URL_TASK_STATUS = os.environ['URL_TASK_STATUS']
URL_TODO_TASK = os.environ['URL_TODO_TASK']

data = {
    'status': None,
    'artifactValidationStatus': [
        {'artifactTaskId': None,
         'status': None,
         'artifactId': None}
    ],
    'taskId': None
}


@app.route('/status/v1.0/tasks', methods=['GET'])
def update_task():
    virus_id = tasks[0]['task_details']['virus_task_id']
    license_id = tasks[0]['task_details']['license_task_id']
    text_search_id = tasks[0]['task_details']['text_task_id']

    virus_url = '/'.join((URL_TASK_STATUS, 'securityScan', virus_id))
    license_url = '/'.join((URL_TASK_STATUS, 'licenseComp', license_id))
    text_search_url = '/'.join((URL_TASK_STATUS, 'keywordScan', text_search_id))

    q = requests.get(virus_url)
    f = requests.get(license_url)
    z = requests.get(text_search_url)

    virus_object = q.json()
    license_object = f.json()
    text_search_object = z.json()
    task = {
        'Security Scan': virus_object,
        'License Compliance': license_object,
        'Keyword Search': text_search_object
    }
    return jsonify({'task': task})


# OST verb usage
@app.route('/status/v1.0/tasks', methods=['POST'])
def create_task():

    """
    This is an example
    ---
    tags:
      - restful
    parameters:
      - in: body
        name: body
        schema:
          $ref: '#/definitions/Task'
    responses:
       201:
        description: The task has been created
        schema:
          $ref: '#/definitions/Task'
    """

    if not request.json:
        abort(400)

    task = {
        'solutionId': request.json['solutionId'],
        'revisionId': request.json['revisionId'],
        'visibility': request.json['visibility'],
        'artifactValidations': request.json['artifactValidations']
    }
    t = requests.post(URL_INVOKE_TASK, json.dumps(task), headers={"Content-type": "application/json; charset=utf8"})
    task_details = t.json()
    task['task_details'] = task_details
    tasks.append(task)

    r = requests.get(URL_TODO_TASK)
    # POST verb on the api
    s = requests.post(URL_TODO_TASK, json.dumps(task), headers={"Content-type": "application/json; charset=utf8"})

    return jsonify({'task': task}), 201


# GET verb
@app.route("/log")
def logTest():
    app.logger.warning('testing warning log')
    app.logger.error('testing error log')
    app.logger.info('testing info log')
    return "Code Handbook !! Log testing."


if __name__ == '__main__':
    # formatter = logging.Formatter("%(asctime)s | %(pathname)s:%(lineno)d | %(levelname)s | %(module)s | %(funcName)s | %(message)s ")
    formatter = logging.Formatter("%(asctime)s | %(pathname)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s")
    logHandler = RotatingFileHandler('info.log', maxBytes=1000, backupCount=1)
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(logHandler)

    app.run(host="0.0.0.0",port=9603 ,debug=True)

