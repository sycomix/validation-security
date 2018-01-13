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
tasks = [
    {
        'solutionId': 1,
        'revisionId': '2',
        'artifacts': "",
        'requestToPublish': 'Organization'
    },
    {
        'solutionId': 42,
        'revisionId': '3',
        'artifacts': "",
        'requestToPublish': 'Public'
    }
]

app = Flask(__name__)
swagger = Swagger(app)
app.config['SECRET_KEY'] = 'top-secret!'




# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://redis:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379/0'
app.config['CELERY_TASK_SERIALIZER'] = 'json'


# Initialize Celery
celery = Celery(app.name,serializer=app.config['CELERY_TASK_SERIALIZER'], backend=app.config['CELERY_RESULT_BACKEND'],broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)









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
                          meta={'current': i*(20), 'total': total, 'solutionId':'12jkh12jkh',
                                'status': message})
        result = virus_scan()
        time.sleep(1)
    return {'current': 100, 'total': 100,'solutionId':'12jkh12jkh',  'status': 'Virus Scan completed!',
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
                          meta={'current': i*(20), 'total': total, 'solutionId':'12jkh12jkh',
                                'status': message})

        result = 'pass'
        time.sleep(1)
    return {'current': 100, 'total': 100,'solutionId':'12jkh12jkh',  'status': 'License scanning completed!',
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
                          meta={'current': i*(20), 'total': total, 'solutionId':'12jkh12jkh',
                                'status': message})

        result = 'pass'
        time.sleep(1)
    return {'current': 100, 'total': 100,'solutionId':'12jkh12jkh',  'status': 'Keyword search completed!',
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
                          meta={'current': i*(20), 'total': total, 'solutionId':'12jkh12jkh',
                                'status': message})

        result = 'pass'
        time.sleep(1)
    return {'current': 100, 'total': 100,'solutionId':'12jkh12jkh',  'status': 'Verify model completed!',
            'result': result}


# The Virus Scan function

def virus_scan():

 #   List1.append(task1)
   # jsonstr = json.dumps(List1)
    os.system("bandit blog_ex.py -f json -o outputfile ")

#Scan for an outputfile
    x = glob.glob('outputfile*')
    #if the file exists parse the file for the results and make a decision
    if len(x) == 1:
        with open('outputfile') as data_file:
            data = json.load(data_file)

        if data["results"][0]["issue_severity"] in ['HIGH','MEDIUM'] and data["results"][0]['issue_confidence'] in ['HIGH','MEDIUM'] :
            return 'Fail'
        else:
            return 'Pass'

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

