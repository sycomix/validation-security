#!python
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
from __future__ import absolute_import
from celery import Celery
import glob
import json
import os
import time


# Initialize Celery
celery = Celery('validation_task_manager')
celery.conf.update(
    BROKER_URL=os.environ.get('REDIS_HOST', None),
    CELERY_RESULT_BACKEND=os.environ.get('REDIS_HOST', None),
    CELERY_RESULT_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_ENABLE_UTC=True,
    CELERY_TRACK_STARTED=True,
)


# ================================================================
# Distributed programming
# Task definitions
# ================================================================
@celery.task(bind=True, name="validation_task_manager.virusScan")
def virus_scan_task(self, metadata):
    """Background task that runs a security scan with progress reports."""
    verb = ['Starting up', 'Booting', 'Scanning', 'Loading', 'Checking']
    noun = ['Virus Scan']
    message = ''
    total = 100

    with open('metadata.py', 'w') as outfile:
        json.dump(metadata, outfile, ensure_ascii=False)

    for i in range(5):
        if not message:
            message = '{0} {1} ...'.format(verb[i], noun[0])
        self.update_state(state='PROGRESS', meta={'current': i * 20, 'total': total, 'status': message})
        time.sleep(1)

    result = virus_scan()
    return {'current': 100, 'total': 100, 'status': 'Virus Scan completed!', 'result': result}


@celery.task(bind=True, name="validation_task_manager.licenseScan")
def license_scan_task(self, module_runtime, dict_license):
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


@celery.task(bind=True, name="validation_task_manager.keywordScan")
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


# The Virus Scan function
def virus_scan():
    """
    The virus scan function. It will scan the code on provided path using python's bandit library.
    :return: Pass or Fail
    """
    try:
        os.system("bandit metadata.py -f json -o outputfile ")

        # Scan for an outputfile
        x = glob.glob('outputfile*')
        # if the file exists parse the file for the results and make a decision
        if len(x) == 1:
            with open('outputfile') as data_file:
                content = data_file.read()
                data = json.loads(content)

            if not data["results"]:
                return "PASS"
            if data["results"][0]["issue_severity"] in ['HIGH', 'MEDIUM'] and data["results"][0]['issue_confidence'] in ['HIGH', 'MEDIUM']:
                return 'FAIL - Security Scan failed.'
            else:
                return 'PASS'
    except:
        return 'FAIL - Security Scan failed.'


# Doing license check
def license_check(module_runtime, dict_license):
    try:
        if 'dependencies' not in module_runtime:
            return "FAIL - Dependencies not found in metadata"
        module_dependencies = module_runtime['dependencies']
        key = list(module_dependencies.keys())[0]
        check_list = module_dependencies[key]
        if 'requirements' not in check_list:
            return "FAIL - Requirements not found in metadata"
        license_requirements = check_list['requirements']
        license_list = [j['name'] for j in license_requirements]
        for i in dict_license:
            return "FAIL - {0} found in License".format(i) if i in license_list else "PASS"
    except:
        return "FAIL"


# Keyword scan
def keyword_scan(module_name, keyword_dict):
    try:
        striptext = module_name.replace('\n\n', ' ')
        keywords_list = striptext.split()
        keywords_list = [i.lower() for i in keywords_list]
        for j in keywords_list:
            if j in keyword_dict:
                return "FAIL - {0} found in Keyword Scan".format(j)
            else:
                return "PASS"
    except:
        return "FAIL"
