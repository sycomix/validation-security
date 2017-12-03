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

data = {'status': 'Pass', 'artifactValidationStatus': [{'artifactTaskId': '4ab4fcb8-fd91-4885-be7c-163acd683ee7', 'status': 'Pass', 'artifactId': '38daf266-cd85-4bb0-a4db-5b3263defa7b'}], 'taskId': '38daf266-cd85-4bb0-a4db-5b3263defa7b'}

#GET verb usage

#@app.route('/status/v1.0/tasks', methods=['GET'])
#def get_tasks():
   # return jsonify({"virus": q.json(),"license":f.json()})
#    return jsonify({'tasks': tasks})

@app.route('/status/v1.0/tasks', methods=['GET'])
def update_task():
    taskid = tasks[0]['task_details']['task_id']
    base_url = ('http://localhost:9000/status',taskid)
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
    t = requests.get('http://localhost:9605/invoketask')
    l= t.json()
    task = {
        'solutionId': request.json['solutionId'],
        'revisionId': request.json['revisionId'],
        'visibility': request.json['visibility'],
        'artifactValidations':request.json['artifactValidations'],
        'task_details': l
    }
    tasks.append(task)
    r = requests.get('http://localhost:9605/todo/api/v1.0/tasks')
# POST verb on the api
    s = requests.post('http://localhost:9604/todo/api/v1.0/tasks',json.dumps(task),headers={"Content-type":"application/json; charset=utf8"})

# Process Id's
    virus_id = l['task_id']
    license_id = l['task_id1']
    textSearch_id = l['task_id2']

# Creating the base URLs
    virus_base_url = ('http://localhost:9605/status',virus_id)
    license_base_url = ('http://localhost:9605/status',license_id)
    textSearch_base_url = ('http://localhost:9605/status',textSearch_id)

# Creating the full URLs
    virus_url =  '/'.join(virus_base_url)
    license_url =  '/'.join(license_base_url)
    textSearch_url =  '/'.join(textSearch_base_url)

    q = requests.get(virus_url)
    f = requests.get(license_url)
    z = requests.get(textSearch_url)
    base_url2 = ('http://cognita-ist2-vm01-core:8083/validation',l['principle_task_id'])
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

