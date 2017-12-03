# Validation and Security(V&S)

[![Build Status](http://cognita-dev1-jenkins.eastus.cloudapp.azure.com:8080/job/acumos-python-client/badge/icon)](http://cognita-dev1-jenkins.eastus.cloudapp.azure.com:8080/job/acumos-python-client/)


   Validation& Security microservice is about a "Run time" Scaning utility that will be applied on the models for sanity check!
  
	
	
##	Use cases:

1. Publishing the model to various market places.



##	Business rules for validaition & secuirty:

1. Software License compliance.
2. Virus/threat.
3. Key word search
	
##   Contents:
    1). Rest APIs
	2). V&S module
	
Rest API
   
	3 API's all together.

		1. A wrapper API.
		2. An intermediate API( A dummy rest API to facilitate the communication)
		3. Low level API(Where actual stuff happens)
			- Invokeing tasks.
			- Status check.



