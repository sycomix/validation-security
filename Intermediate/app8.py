from flask import Flask, jsonify
from flask import request
import requests
import json
from flask import abort
import uuid

app = Flask(__name__)

# Validation task types = SS, LS, TA, OQ
data = {"status": 'Pass', 'artifactValidationStatus': [{'artifactTaskId': '4ab4fcb8-fd91-4885-be7c-163acd683ee7', 'validationTaskType': 'SS',  'status': 'Pass', 'artifactId': '38daf266-cd85-4bb0-a4db-5b3263defa7b'}], 'taskId': '38daf266-cd85-4bb0-a4db-5b3263defa7b','visibility':"PB", 'solutionId':'38daf266-cd85-4bb0-a4db-5b3263defa7b', 'revisionId' : '4ab4fcb8-fd91-4885-be7c-163acd683ee7'}


tasks = []

#GET verb usage
@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})

#POST verb usage
@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():

    if not request.json:
        abort(400)

    task = {
            'solutionId': request.json["solutionId"],
            'revisionId': request.json["revisionId"],
            'visibility': request.json['visibility'],
            'artifactValidations': request.json['artifactValidations'],
            'task_details': request.json["task_details"]
           }
    k = task['task_details']['task_id']
    g = task['task_details']['task_id1']
    p = task['task_details']['task_id2']

    base_url = ('http://localhost:9605/status',k)
    base_url1 = ('http://localhost:9605/status',g)
    base_url3 = ('http://localhost:9605/status',p)

    new_url =  '/'.join(base_url)
    new_url1 =  '/'.join(base_url1)
    new_url3 =  '/'.join(base_url3)

    q = requests.get(new_url)
    f = requests.get(new_url1)
    z = requests.get(new_url3)

    virus_object = q.json()
    license_object = f.json()
    textSearch_object = z.json()

    base_url2 = ('http://cognita-ist2-vm01-core:8083/validation',task['task_details']['principle_task_id'])
    new_url2 =  '/'.join(base_url2)

    if virus_object["state"]== "SUCCESS":
        data['status']=virus_object["result"]
        data['taskId']=task['task_details']['principle_task_id']
        data['solutionId']=task['solutionId']
        data['revisionId']=task['revisionId']
        data['visibility']=task['visibility']

        data['artifactValidationStatus'][0]['status']=virus_object["result"]
        data['artifactValidationStatus'][0]['artifactTaskId']= k
        data['artifactValidationStatus'][0]['artifactId']= task['artifactValidations'][0]['artifactId']
        data['artifactValidationStatus'][0]['validationTaskType']= "SS"

        r = requests.put(new_url2,json.dumps(data),headers={"Content-type":"application/json; charset=utf8"})

    if license_object["state"]== "SUCCESS":
        data['status']=license_object["result"]
        data['taskId']=task['task_details']['principle_task_id']
        data['solutionId']=task['solutionId']
        data['revisionId']=task['revisionId']
        data['visibility']=task['visibility']

        data['artifactValidationStatus'][0]['status']=license_object["result"]
        data['artifactValidationStatus'][0]['artifactTaskId']= g
        data['artifactValidationStatus'][0]['artifactId']= task['artifactValidations'][0]['artifactId']
        data['artifactValidationStatus'][0]['validationTaskType']= "LS"

        r = requests.put(new_url2,json.dumps(data),headers={"Content-type":"application/json; charset=utf8"})

    if textSearch_object["state"]== "SUCCESS":
        data['status']=textSearch_object["result"]
        data['taskId']=task['task_details']['principle_task_id']
        data['solutionId']=task['solutionId']
        data['revisionId']=task['revisionId']
        data['visibility']=task['visibility']

        data['artifactValidationStatus'][0]['status']=textSearch_object["result"]
        data['artifactValidationStatus'][0]['artifactTaskId']= p
        data['artifactValidationStatus'][0]['artifactId']= task['artifactValidations'][0]['artifactId']
        data['artifactValidationStatus'][0]['validationTaskType']= "TA"
        r = requests.put(new_url2,json.dumps(data),headers={"Content-type":"application/json; charset=utf8"})



    return ("done"), 201

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=9604 ,debug=True)

