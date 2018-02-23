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
import glob
import time

app = Flask(__name__)
swagger = Swagger(app)
app.config['SECRET_KEY'] = 'top-secret!'

URL_CCDS = os.environ.get('URL_CCDS', None)
CCDS_USERNAME = os.environ.get('CCDS_USERNAME', None)
CCDS_PASSWORD = os.environ.get('CCDS_PASSWORD', None)
URL_SITE_CONFIG = os.environ.get('URL_SITE_CONFIG', None)
URL_TODO_TASK = os.environ.get('URL_TODO_TASK', None)
IGNORE_LIST_CHECK = os.environ.get('IGNORE_LIST_CHECK', 'Disable')


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
        'artifactValidations': request.json['artifactValidations'],
        'trackingId': request.json['trackingId'],
        'userId': request.json['userId'],
        'task_details': {}
    }

    # Defining the parsed json object
    def get_artifact_id():
        artifact_validation = task['artifactValidations']
        for artifact in artifact_validation:
            if artifact['artifactType'] == 'MD':
                artifactid = artifact['artifactId']
            elif artifact['artifactType'] == 'BP':
                artifactid = artifact['artifactId']

        if not artifactid:
            return artifact_validation[0]['artifactId']
        else:
            return artifactid

    artifactId = get_artifact_id()

    # Defining the parsed json object
    def get_metadata():
        artifact_validation = task['artifactValidations']
        for artifact in artifact_validation:
            if artifact['artifactType'] == 'MD':
                meta_url = artifact['url']
            elif artifact['artifactType'] == 'BP':
                meta_url = artifact['url']

        if not meta_url:
            abort(404)
        else:
            return meta_url

    metadata_res = requests.get(get_metadata())
    metadata = metadata_res.json()

    with open('metadata.py', 'w') as outfile:
        json.dump(metadata, outfile, ensure_ascii=False)

    module_name = metadata['name']
    module_runtime = metadata['runtime']

    # Realtime site config
    keyword_to_scan = requests.get(URL_CCDS, auth=('ccds_client', 'ccds_client'))
    # keywords = json.loads(keyword_to_scan.json()['configValue'])['fields'][-1]['data'].encode()
    fields = json.loads(keyword_to_scan.json()['configValue'])['fields']
    data = ''
    for item in fields:
        if item['name'] == 'validationText':
            data = item['data']
    keywords = data.encode()

    # temporary database in a listshape
    keyword_dict = []
    keyword_dict.append(keywords)
    # dict_security = ['verizon', 'AT&T']
    dict_license = ["PSFL", "MIT", "MIT (X11)", "New BSD", "ISC", "Apache", "LGPL", "GPL", "GPLv2", "GPLv3"]

    ignore_lst = []
    if IGNORE_LIST_CHECK == 'Enable':
        # Getting ignore list from development server
        admin_workflow_validation_url = '/'.join((URL_SITE_CONFIG, "local_validation_workflow"))
        admin_workflow_validation_res = requests.get(admin_workflow_validation_url, auth=(CCDS_USERNAME, CCDS_PASSWORD))
        response = admin_workflow_validation_res.json()
        config_val_array = response["response_body"]["configValue"]
        validation_ignore_array = json.loads(config_val_array)
        for element in validation_ignore_array['ignore_list']:
            ignore_lst.append(element)

    principle_task_id = uuid.uuid4()
    task['task_details']['principle_task_id'] = str(principle_task_id)
    task['task_details']['artifactId'] = artifactId
    license_task_id = ''
    virus_task_id = ''

    if "License scan" not in ignore_lst:
        license_task_id = uuid.uuid4()
        task['task_details']['license_task_id'] = str(license_task_id)
        task['task_details']['status'] = 'Started'
        task['task_details']['result'] = 'License scan - started'
        task['task_details']['state'] = 'STARTED'
        # POST verb on the api
        requests.post(URL_TODO_TASK, json.dumps(task), headers={"Content-type": "application/json; charset=utf8"})
        time.sleep(2)
        task['task_details']['status'] = 'In-progress'
        task['task_details']['result'] = 'License scan - in-progress'
        task['task_details']['state'] = 'STARTED'
        requests.post(URL_TODO_TASK, json.dumps(task), headers={"Content-type": "application/json; charset=utf8"})
        license_task = license_check(module_runtime, dict_license)
        time.sleep(5)
        if license_task == "PASS":
            task['task_details']['status'] = 'Completed'
            task['task_details']['result'] = 'License scan - success'
            task['task_details']['state'] = 'SUCCESS'
        else:
            task['task_details']['status'] = 'Completed'
            task['task_details']['result'] = license_task
            task['task_details']['state'] = 'FAILURE'
        requests.post(URL_TODO_TASK, json.dumps(task), headers={"Content-type": "application/json; charset=utf8"})

    if "Security scan" not in ignore_lst:
        virus_task_id = str(uuid.uuid4())
        if 'license_task_id' in task['task_details']:
            del task['task_details']['license_task_id']

        task['task_details']['virus_task_id'] = virus_task_id
        task['task_details']['status'] = 'Started'
        task['task_details']['result'] = 'Security scan - started'
        task['task_details']['state'] = 'STARTED'
        # POST verb on the api
        requests.post(URL_TODO_TASK, json.dumps(task), headers={"Content-type": "application/json; charset=utf8"})
        time.sleep(2)
        task['task_details']['status'] = 'In-progress'
        task['task_details']['result'] = 'Security scan - in-progress'
        task['task_details']['state'] = 'STARTED'
        requests.post(URL_TODO_TASK, json.dumps(task), headers={"Content-type": "application/json; charset=utf8"})
        virus_task = virus_scan()
        time.sleep(5)
        if virus_task == "PASS":
            task['task_details']['status'] = 'Completed'
            task['task_details']['result'] = 'Security scan - success'
            task['task_details']['state'] = 'SUCCESS'
        else:
            task['task_details']['status'] = 'Completed'
            task['task_details']['result'] = 'Security scan - failed'
            task['task_details']['state'] = 'FAILURE'
        requests.post(URL_TODO_TASK, json.dumps(task), headers={"Content-type": "application/json; charset=utf8"})

    if "Text Check" not in ignore_lst:
        text_task_id = str(uuid.uuid4())
        if 'virus_task_id' in task['task_details']:
            del task['task_details']['virus_task_id']

        task['task_details']['text_task_id'] = text_task_id
        task['task_details']['status'] = 'Started'
        task['task_details']['result'] = 'Text Check - started'
        task['task_details']['state'] = 'STARTED'
        # POST verb on the api
        requests.post(URL_TODO_TASK, json.dumps(task), headers={"Content-type": "application/json; charset=utf8"})
        time.sleep(2)
        task['task_details']['status'] = 'In-progress'
        task['task_details']['result'] = 'Text Check - in-progress'
        task['task_details']['state'] = 'STARTED'
        requests.post(URL_TODO_TASK, json.dumps(task), headers={"Content-type": "application/json; charset=utf8"})
        keyword_task = keyword_scan(module_name, keyword_dict)
        time.sleep(5)
        if keyword_task == "PASS":
            task['task_details']['status'] = 'Completed'
            task['task_details']['result'] = 'Text Check - success'
            task['task_details']['state'] = 'SUCCESS'
        else:
            task['task_details']['status'] = 'Completed'
            task['task_details']['result'] = keyword_task
            task['task_details']['state'] = 'FAILURE'
        requests.post(URL_TODO_TASK, json.dumps(task), headers={"Content-type": "application/json; charset=utf8"})

    del task['task_details']['status']
    del task['task_details']['result']
    del task['task_details']['state']
    task['task_details']['license_task_id'] = license_task_id
    task['task_details']['virus_task_id'] = virus_task_id
    return jsonify(task['task_details']), 202


# The Virus Scan function
def virus_scan():
    """
    The virus scan function. It will scan the code on provided path using python's bandit library.
    :return: Pass or Fail
    """
    os.system("bandit metadata.py -f json -o outputfile ")
    # os.system("bandit {0}/*.py -f json -o outputfile ".format(code_path))
    # os.system("bandit -r ~/{0} -f json -o outputfile ".format(code_path))

    # Scan for an outputfile
    x = glob.glob('outputfile*')
    # if the file exists parse the file for the results and make a decision
    if len(x) == 1:
        with open('outputfile') as data_file:
            content = data_file.read()
            data = json.loads(content)

        if not data["results"]:
            return "PASS"
        else:
            if data["results"][0]["issue_severity"] in ['HIGH', 'MEDIUM'] and data["results"][0]['issue_confidence'] in ['HIGH', 'MEDIUM']:
                return 'Fail'
            else:
                return 'Pass'


# Doing license check
def license_check(module_runtime, dict_license):
    license_list = []
    license_requirements = module_runtime['dependencies']['pip']['requirements']
    for j in license_requirements:
        license_list.append(j['name'])
    for i in dict_license:
        if i in license_list:
            return "FAIL - {0} found in License".format(i)
        else:
            return "PASS"


# Keyword scan
def keyword_scan(module_name, keyword_dict):
    striptext = module_name.replace('\n\n', ' ')
    keywords_list = striptext.split()
    keywords_list = [i.lower() for i in keywords_list]
    for j in keywords_list:
        if j in keyword_dict:
            return "FAIL - {0} found in Keyword Scan".format(j)
        else:
            return "PASS"


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
    handler = RotatingFileHandler('validation_engine.log', maxBytes=1024*1024*100, backupCount=3)
    logger = logging.getLogger('__name__')
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)

    app.run(host="0.0.0.0", port=9605)
