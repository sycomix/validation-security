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
import glob
from pprint import pprint
import random
import time
from flask import Flask, request, render_template, session, flash, redirect, \
    url_for, jsonify
from celery import Celery
from flasgger import Swagger
import requests
import uuid



app = Flask(__name__)
swagger = Swagger(app)
app.config['SECRET_KEY'] = 'top-secret!'





@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Scanning', 'Loading', 'Checking']
    noun = ['Virus Scan']
    message = ''
    total = 100
    for i in range(5):
        if not message:
            message = '{0} {1} ...'.format(verb[i],
                                              noun[0])
        self.update_state(state='PROGRESS',
                          meta={'current': i*(20), 'total': total, 
                                'status': message})
        result = virus_scan()
        time.sleep(1)
    return {'current': 100, 'total': 100,  'status': 'Virus Scan completed!',
            'result': result}






@celery.task(bind=True)
def long_task1(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Scanning', 'Loading', 'Checking']
    noun = ['License Compliance']

    message = ''
    total = 100
    for i in range(5):
        if not message:
            message = '{0} {1} ...'.format(verb[i],
                                              noun[0])
        self.update_state(state='PROGRESS',
                          meta={'current': i*(20), 'total': total,
                                'status': message})

        result = 'pass'
        time.sleep(1)
    return {'current': 100, 'total': 100,  'status': 'License scanning completed!',
            'result': result}

@celery.task(bind=True)
def long_task3(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Scanning', 'Loading', 'Checking']
    noun = ['Keyword search']

    message = ''
    total = 100
    for i in range(5):
        if not message:
            message = '{0} {1} ...'.format(verb[i],
                                              noun[0])
        self.update_state(state='PROGRESS',
                          meta={'current': i*(20), 'total': total,
                                'status': message})

        result = 'pass'
        time.sleep(1)
    return {'current': 100, 'total': 100,  'status': 'Keyword search completed!',
            'result': result}



@celery.task(bind=True)
def long_task4(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Scanning', 'Loading', 'Checking']
    noun = ['Verify model']

    message = ''
    total = 100
    for i in range(5):
        if not message:
            message = '{0} {1} ...'.format(verb[i],
                                              noun[0])
        self.update_state(state='PROGRESS',
                          meta={'current': i*(20), 'total': total, 
                                'status': message})

        result = 'pass'
        time.sleep(1)
    return {'current': 100, 'total': 100,  'status': 'Verify model completed!',
            'result': result}




@app.route('/invoketask', methods=['GET'])
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
    if request.method == 'GET':
        task=long_task.apply_async()
        task1=long_task1.apply_async()
        task3=long_task3.apply_async()
        task2 = uuid.uuid4()
    #    return redirect(url_for('taskstatus',task_id = task.id))
        return jsonify ({'task_id':task.id, 'task_id1':task1.id,'principle_task_id':task2, 'task_id2':task3.id})


@app.route('/longtask', methods=['POST'])
def longtask():
 #    task = long_task.apply_async()
 #   solutionId = '1234jik'
    if  request.json:
        solutionId=request.json['solutionId']
        return jsonify({'solutionId':solutionId}), 200, {'Location': url_for('taskstatus',task_id=solutionId)}
    return jsonify({'solutionId':solutionId}), 200, {'Location': url_for('taskstatus',task_id=solutionId)}



@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():




    if not request.json:
        abort(400)
    task = {
        'solutionId': request.json['solutionId'],
        'revisionId': request.json['revisionId'],
        'artifacts': request.json.get('artifacts', ""),
        'requestToPublish': request.json['requestToPublish']
    }
    tasks.append(task)
    return jsonify({'task': task}), 201





@app.route('/longtask1', methods=['POST'])
def longtask1():
    task = long_task1.apply_async()

    return jsonify({}), 200, {'Location': url_for('taskstatus',

                                                  task_id=task.id)}
@app.route('/status/<task_id>')
def taskstatus(task_id):

    """Example endpoint returning a list of status by task Id's
    This is using docstrings for specifications.
    ---
    parameters:
      - in: path
        name: task_id
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

    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
           'task_id': task_id,

            'total': 1,
            'status': 'Pending...'
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
        response = response1
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=9605, debug=True)

