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
import time
from flasgger import Swagger


app = Flask(__name__)
swagger = Swagger(app)


tasks = []

# Definition of URLs
URL_INVOKE_TASK = os.environ.get('URL_INVOKE_TASK', None)

data = {
    'status': None,
    'artifactValidationStatus': [
        {'artifactTaskId': None,
         'status': None,
         'artifactId': None}
    ],
    'taskId': None
}


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
        'artifactValidations': request.json['artifactValidations'],
        'trackingId': request.json['trackingId'],
        'userId': request.json['userId']
    }
    res = requests.post(URL_INVOKE_TASK, json.dumps(task), headers={"Content-type": "application/json; charset=utf8"})
    task_details = res.json()
    task['task_details'] = task_details
    tasks.append(task)

    return jsonify({'task': task}), 201


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
    handler = RotatingFileHandler('validation_client.log', maxBytes=1024*1024*100, backupCount=3)
    logger = logging.getLogger('__name__')
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)

    app.run(host="0.0.0.0", port=9603)
