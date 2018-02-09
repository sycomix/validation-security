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
from flask import Flask, jsonify
import requests
import logging
from logging.handlers import RotatingFileHandler
from flask import request
from flask import abort
import uuid
import json
from flasgger import Swagger


app = Flask(__name__)
swagger = Swagger(app)


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


@app.route('/status/v1.0/tasks', methods=['GET'])
def update_task():
    taskid = tasks[0]['task_details']['task_id']
    base_url = (URL_TASK_STATUS,taskid)
    new_url =  '/'.join(base_url)
    q = requests.get(new_url)

    return jsonify({'task': q.json()})

#POST verb usage
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

#    if not request.json:
#`       abort(400)
#    tasks = []
    t = requests.get(URL_INVOKE_TASK)
    l= t.json()
    task = {
        'solutionId': request.json['solutionId'],
        'revisionId': request.json['revisionId'],
        'visibility': request.json['visibility'],
        'artifactValidations':request.json['artifactValidations'],
        'task_details': l
    }
    tasks.append(task)
    r = requests.get(URL_TASK_STATUS)
# POST verb on the api
    s = requests.post(URL_TASK_STATUS,json.dumps(task),headers={"Content-type":"application/json; charset=utf8"})

# Process Id's
    virus_id = l['virus_task_id']
    license_id = l['license_task_id']
    textSearch_id = l['text_task_id']

# Creating the base URLs
    virus_base_url = (URL_TASK_STATUS,virus_id)
    license_base_url = (URL_TASK_STATUS,license_id)
    textSearch_base_url = (URL_TASK_STATUS,textSearch_id)

# Creating the full URLs
    virus_url =  '/'.join(virus_base_url)
    license_url =  '/'.join(license_base_url)
    textSearch_url =  '/'.join(textSearch_base_url)

    q = requests.get(virus_url)
    f = requests.get(license_url)
    z = requests.get(textSearch_url)
    base_url2 = (URL_PORTAL,l['principle_task_id'])
    new_url2 =  '/'.join(base_url2)

    virus_object = q.json()
    license_object = f.json()



#    return jsonify({'task': task,"virus": q.json(),"license":f.json(), "textSearch":z.json()}), 201
    return jsonify({'task': task}), 201


# GET verb
@app.route("/log")
def logTest():
    app.logger.warning('testing warning log')
    app.logger.error('testing error log')
    app.logger.info('testing info log')
    return "Code Handbook !! Log testing."

if __name__ == '__main__':

    logHandler = RotatingFileHandler('info.log', maxBytes=1000, backupCount=1)
    logHandler.setLevel(logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(logHandler)

    app.run(host="0.0.0.0",port=9603 ,debug=True)

