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
import json
from flask import Flask, request, render_template, session, flash, redirect, \
    url_for, jsonify, abort
from flasgger import Swagger
import logging
from logging.handlers import RotatingFileHandler
import requests
import uuid
import re
from celery.result import AsyncResult
from celery_worker import *

app = Flask(__name__)
swagger = Swagger(app)
app.config['SECRET_KEY'] = 'top-secret!'

URL_CCDS = os.environ['URL_CCDS']
URL_SITE_CONFIG = os.environ['URL_SITE_CONFIG']


@app.route('/invoketask', methods=['POST'])
def index():
    """Example endpoint returning a list of  task Id's.
    This is using docstrings for specifications.
    ---

    definitions:
      invoketask:
        type: string
    responses:
      200:
        description: A dict of progress
        schema:
          $ref: '#/definitions/task_ids'
        examples:
          task_id: ['9a95c16a-b87c-4ba0-8cba-b078032e36e1', 'daff6c52-2744-45e4-89ba-c791dcba1619']
    """
    if not request.json:
        abort(400)

    task = {
        'solutionId': request.json["solutionId"],
        'revisionId': request.json["revisionId"],
        'visibility': request.json['visibility'],
        'artifactValidations': request.json['artifactValidations']
    }

    get_metadata_url = task['artifactValidations'][-1]['url']
    json1 = requests.get(get_metadata_url)

    with open('metadata.py', 'w') as outfile:
        json.dump(json1, outfile, ensure_ascii=False)

    module_name = json1.json()['name']
    module_runtime = json1.json()['runtime']

    # Realtime site config
    keyword_to_scan = requests.get(URL_CCDS, auth=('ccds_client', 'ccds_client'))
    keywords = json.loads(keyword_to_scan.json()['configValue'])['fields'][-1]['data'].encode()

    # temporary database in a listshape
    keyword_dict = []
    keyword_dict.append(keywords)
    # dict_security = ['verizon', 'AT&T']
    dict_license = ["PSFL", "MIT", "MIT (X11)", "New BSD", "ISC", "Apache", "LGPL", "GPL", "GPLv2", "GPLv3"]

    # Getting ignore list from development server
    admin_workflow_validation_url = '/'.join((URL_SITE_CONFIG, "local_validation_workflow"))
    admin_workflow_validation_res = requests.get(admin_workflow_validation_url, auth=('ccds_client', 'ccds_client'))    
    response = admin_workflow_validation_res.json()
    json_data = json.loads(response.text)
    config_val_array = json_data["configValue"]
    validation_ignore_array = json.loads(config_val_array)
    ignore_lst = []

    for element in validation_ignore_array['ignore_list']:
        ignore_lst.append(element)

    res = dict()
    if "Security scan" not in ignore_lst:
        virus_task = virus_scan_task.apply_async()
        res['virus_task_id'] = virus_task.id

    if "License scan" not in ignore_lst:
        license_task = license_task.apply_async(module_runtime, dict_license)
        res['license_task_id'] = license_task.id

    if "Text Check" not in ignore_lst:
        keyword_task = keyword_scan_task.apply_async(module_name, keyword_dict)
        res['text_task_id'] = keyword_task.id

    principle_task_id = uuid.uuid4()
    res['principle_task_id'] = principle_task_id

    return jsonify(res), 202


@app.route('/status/<task_name>/<task_id>')
def taskstatus(task_name, task_id):
    """Example endpoint returning a list of status by task Id's
    This is using docstrings for specifications.
    ---
    parameters:
      - name: task_name
        in: path
        required: true
        description: The name of the task, try securityScan!
        type: string
      - name: task_id
        in: path
        required: true
        description: The ID of the task, try 42!
        type: string

    responses:
      200:
        description: The task data
        schema:
          id: task
          properties:
            task_id:
              type: string

    """
    if task_name == 'securityScan':
        task = virus_scan_task.AsyncResult(task_id)
    elif task_name == 'licenseComp':
        task = license_task.AsyncResult(task_id)
    elif task_name == 'keywordScan':
        task = text_search_task.AsyncResult(task_id)
    else:
        abort(404)

    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'task_id': task_id,
            'total': 1,
            'status': 'Pending...',
            'result': 'Not completed!'
        }
    elif task.state != 'FAILURE':
        response1 = {
            'state': task.state,
            'task_id': task_id,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response1['result'] = task.info['result']
        else:
            response1['result'] = ''
        response = response1
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
            'result': 'Failed!'
        }
    return jsonify(response)


if __name__ == '__main__':
    formatter = logging.Formatter("%(asctime)s | %(pathname)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s")
    logHandler = RotatingFileHandler('info.log', maxBytes=1000, backupCount=1)
    logHandler.setLevel(logging.DEBUG)
    logHandler.setFormatter(formatter)
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(logHandler)

    app.run(host="0.0.0.0", port=9605, debug=True)
