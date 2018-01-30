.. THIS FILE WAS GENERATED. DO NOT EDIT.

Scope and Definitions
=====================

The Validation Process includes:

-  Security Scan - virus scan, vulnerability scan, and threat assessment
-  Verification - license compliance and keyword search

The Validation Process may be invoked by publishing a model - a Modeler
submits a request to publish a model from a Private Catalog to a Local
or Public one.

Features and Functionality
==========================

-  Workflow: scan navigation and routing approvals
-  Scanner Toolkits: Open Source
-  Validation APIs
-  Admin GUI Dashboard
-  Validation State Management: state assignment to a model and
   validation result notification to the requester

Components
==========

The Validation and Security (V&S) is a microservice written in Python
and packaged as a Docker image.

Asynchronous REST APIs
----------------------

The V&S microservice uses the `Flask <http://flask.pocoo.org/>`__
microframework and
`Flassger <https://github.com/rochacbruno/flasgger>`__ to implement REST
APIs.

Wrapper API
~~~~~~~~~~~

The Wrapper API listens for communication from the Portal back end.

Intermediate API
~~~~~~~~~~~~~~~~

The Intermediate service sends communications to the Portal back end.

Root API
~~~~~~~~

The Root API is the brains, facilitating the distributed computing of
the business rules. This is where the license checking and keyword
search functionality resides.

Task Management Middleware
--------------------------

`Celery <http://www.celeryproject.org/>`__ is used for asynchronous task
management.

Message Queue and Database
--------------------------

`Redis <https://redis.io/>`__ is used as the back end for Celery to
provide in-memory data structure storage, caching, and message queue
functionality.

