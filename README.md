# FileToJsonApiRestPythonAWS
Presentation
----------------------
* This is an API which returns file data in json when a file is uploaded. 
* This is a school project of MS SIO of CentraleSupélec.
* Key words : Flask, Python, EC2, S3, Rekognition, Docker, Swagger. 

Installation
------------
* The code is deployed on an AWS EC2 using docker compose. 
* ```$ sudo docker-compose up --remove-orphans --build --scale flaskapp=6 -d```

To use the API
--------------
* ```$ curl -u "user01:user01" -F "file=@<your_file_to_upload>" http://filrouge.jma.p2021.ajoga.fr/upload```
* OpenAPI : [swagger](http://filrouge.jma.p2021.ajoga.fr/swagger/)

