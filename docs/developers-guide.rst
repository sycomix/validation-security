.. ===============LICENSE_START=======================================================
.. Acumos
.. ===================================================================================
.. Copyright (C) 2017-2018 AT&T Intellectual Property & Tech Mahindra. All rights reserved.
.. ===================================================================================
.. This Acumos documentation file is distributed by AT&T and Tech Mahindra
.. under the Creative Commons Attribution 4.0 International License (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..  
..      http://creativecommons.org/licenses/by/4.0
..  
.. This file is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.
.. ===============LICENSE_END=========================================================
=================
Developer's Guide
=================

Scope and Definitions
=====================

The Validation Process includes:

-  Security Scan - virus scan, vulnerability scan, and threat assessment
-  Verification - license compliance and keyword search

The Validation Process may be invoked by publishing a model - a Modeler submits
a request to publish a model from a Private Catalog to a Local or Public one.

Features and Functionality
==========================

-  Workflow: scan navigation and routing approvals
-  Scanner Toolkits: Open Source
-  Validation APIs
-  Admin GUI Dashboard
-  Validation State Management: state assignment to a model and validation
   result notification to the requester

Components
==========

The Validation and Security (V&S) is a microservice written in Python and
packaged as Docker images.

Asynchronous REST APIs
----------------------

The V&S microservice uses the `Flask <http://flask.pocoo.org/>`__
microframework and `Flassger <https://github.com/rochacbruno/flasgger>`__ to
implement REST APIs.

validation_client API
~~~~~~~~~~~~~~~~~~~~~

The validation_client service listens for communication from the Portal back end.

validation_middleware API
~~~~~~~~~~~~~~~~

The validation_middleware service sends communications to the Portal back end.

validation_engine API
~~~~~~~~~~~~~~~~~~~~~

The validation_engine service is the brains, facilitating the distributed computing of the
business rules. This is where the license checking and keyword search
functionality resides.

Task Management Middleware
--------------------------

`Celery <http://www.celeryproject.org/>`__ is used for asynchronous task
management.

Message Queue and Database
--------------------------

`Redis <https://redis.io/>`__ is used as the back end for Celery to provide
in-memory data structure storage, caching, and message queue functionality.

