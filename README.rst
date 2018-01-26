Validation and Security
=======================


The Validation and Security microservice is a real-time file scanning service.

Use cases:
----------

1. Publishing the model to various market places.

Business rules for Validation and Security
------------------------------------------

1. Software License compliance
2. Virus/threat
3. Key word search

Contents:
---------

::

    1). Rest APIs
    2). V&S module

Rest API

::

    3 APIs all together:

        1. A wrapper API.
        2. An intermediate API( A dummy rest API to facilitate the communication)
        3. Low level API (where actual stuff happens)
            - Invoking tasks.
            - Status check.

