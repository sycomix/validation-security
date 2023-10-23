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
import time
import glob
import json
from celery import Celery

# Initialize Celery
#appName = os.environ['APP_NAME']
#celery = Celery(appName)
#celery.conf.update(
#    BROKER_URL=os.environ.get('REDIS_HOST', None),
#    CELERY_TASK_SERIALIZER='json',
#    CELERY_RESULT_BACKEND=os.environ.get('REDIS_HOST', None)
#)
celery = Celery(os.environ.get('APP_NAME', 'ValidationAndSecurity'))
celery.config_from_object('celeryconfig')



# ================================================================
# Distributed programming
# Task definitions
# ================================================================

@celery.task(bind=True)
def virus_scan_task(self):
    """Background task that runs a security scan with progress reports."""
    verb = ['Starting up', 'Booting', 'Scanning', 'Loading', 'Checking']
    noun = ['Virus Scan']
    message = ''
    total = 100
    for i in range(5):
        if not message:
            message = '{0} {1} ...'.format(verb[i], noun[0])
        self.update_state(state='PROGRESS', meta={'current': i * 20, 'total': total, 'status': message})
        time.sleep(1)
    #result = security_check(module_runtime, dict_security)
    result = virus_scan()
    return {'current': 100, 'total': 100, 'status': 'Virus Scan completed!', 'result': result}


@celery.task(bind=True)
def license_task(self, module_runtime, dict_license):
    """Background task that runs a license check function with progress reports."""
    verb = ['Starting up', 'Booting', 'Scanning', 'Loading', 'Checking']
    noun = ['License Compliance']

    message = ''
    total = 100
    for i in range(5):
        if not message:
            message = '{0} {1} ...'.format(verb[i], noun[0])
        self.update_state(state='PROGRESS', meta={'current': i * 20, 'total': total, 'status': message})
        time.sleep(1)
    result = license_check(module_runtime, dict_license)
    return {'current': 100, 'total': 100, 'status': 'License scanning completed!', 'result': result}


@celery.task(bind=True)
def keyword_scan_task(self, module_name, keyword_dict):
    """Background task that runs a keyword scan function with progress reports."""
    verb = ['Starting up', 'Booting', 'Scanning', 'Loading', 'Checking']
    noun = ['Keyword scan']

    message = ''
    total = 100
    for i in range(5):
        if not message:
            message = '{0} {1} ...'.format(verb[i], noun[0])
        self.update_state(state='PROGRESS', meta={'current': i * 20, 'total': total, 'status': message})
        time.sleep(1)
    result = keyword_scan(module_name, keyword_dict)
    return {'current': 100, 'total': 100, 'status': 'Keyword scan completed!', 'result': result}


@celery.task(bind=True)
def verify_model_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Scanning', 'Loading', 'Checking']
    noun = ['Verify model']

    message = ''
    total = 100
    for i in range(5):
        if not message:
            message = '{0} {1} ...'.format(verb[i], noun[0])
        self.update_state(state='PROGRESS', meta={'current': i * 20, 'total': total, 'status': message})
        time.sleep(1)
    result = 'pass'
    return {'current': 100, 'total': 100, 'status': 'Verify model completed!', 'result': result}


# Keyword scan
def keyword_scan(module_name, keyword_dict):
    striptext = module_name.replace('\n\n', ' ')
    keywords_list = striptext.split()
    keywords_list = [i.lower() for i in keywords_list]
    for j in keywords_list:
        return "FAIL" if j in keyword_dict else "PASS"


# Doing license check
def license_check(module_runtime, dict_license):
    license12 = module_runtime['dependencies']['pip']['requirements']
    license_list = [j['name'] for j in license12]
    for i in dict_license:
        return "FAIL" if i in license_list else "PASS"


# Doing Security check
def security_check(module_runtime, dict_security):
    security12 = module_runtime['dependencies']['pip']['requirements']
    security_list = [j['name'] for j in security12]
    for i in dict_security:
        return "FAIL" if i in security_list else "PASS"


# The Virus Scan function
def virus_scan():
    """
    The virus scan function. It will scan the code on provided path using python's bandit library.
    :param code_path:
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
            data = json.loads(data_file)

        if data["results"][0]["issue_severity"] in ['HIGH','MEDIUM'] and data["results"][0]['issue_confidence'] in ['HIGH','MEDIUM'] :
            return 'Fail'
        else:
            return 'Pass'