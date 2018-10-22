# Lambda in Docker
Running a Lambda function in a Docker container.

## Objective
Create a Docker project where we can develop normal _Lambda_ functions, but run them in Docker instead of the AWS Lambda environment to avoid being limited to the 15 minutes. Running the Lambda function locally would not result in a failing task, but running it on AWS Lambda would fail instead. By pushing it to a Docker image combined with AWS Fargate, we can schedule the Docker container creation and crawl the data periodically.

## Steps

1. Create Lambda function in `my_module.py`
   ```python
   import json
   
   def my_handler(event, context):
        body = {
            "message": "This is the handler function",
            "input": event
        }
        response = {
                "statusCode": 200,
                "body": json.dumps(body)
            }
        return response

   ```
   
2. Test locally with `AWS SAM` or `serverless` environment 
   _Not described here._
3. Deploy to `AWS lambda` to verify if function runs within the time limit
   _Not described here._
   
If the function does not run in time, run the function locally in Docker with `lambda` image
1. Test locally from local folder
```bash
lambda-in-docker $ docker run --rm -v "$PWD":/var/task lambci/lambda:python3.6 my_module.my_handler | json_pp                                                             
START RequestId: a51593fa-4a7c-43f0-a16c-55acfe296eb0 Version: $LATEST
END RequestId: a51593fa-4a7c-43f0-a16c-55acfe296eb0
REPORT RequestId: a51593fa-4a7c-43f0-a16c-55acfe296eb0 Duration: 12 ms Billed Duration: 100 ms Memory Size: 1536 MB Max Memory Used: 18 MB
{
  "body" : "{\"message\": \"This is the handler function\", \"input\": {}}",
  "statusCode" : 200
}
```

 2. Create `docker-compose.yml` with the custom image and calling the handler.
 ```yaml
 version: '3'
   services:
     pythonlambda:
       image: lambci/lambda:python3.6
       command: my_module.my_handler
       volumes:
       - .:/var/task
 ```

 ```bash
 lambda-in-docker $ docker-compose up
 Starting lambda-in-docker_pythonlambda_1 ... done
 Attaching to lambda-in-docker_pythonlambda_1
 pythonlambda_1  | START RequestId: e475064c-d77b-45f3-a9bd-ad3d49ba00c0 Version: $LATEST
 pythonlambda_1  | END RequestId: e475064c-d77b-45f3-a9bd-ad3d49ba00c0
 pythonlambda_1  | REPORT RequestId: e475064c-d77b-45f3-a9bd-ad3d49ba00c0 Duration: 9 ms Billed Duration: 100 ms Memory Size: 1536 MB Max Memory Used: 19 MB
 pythonlambda_1  |
 pythonlambda_1  | {"statusCode": 200, "body": "{\"message\": \"This is the handler\", \"input\": {}}"}
 lambda-in-docker_pythonlambda_1 exited with code 0
 ```

3. Create `Dockerfile` and modify `docker-compose.yml`

`Dockerfile`

```Dockerfile
FROM lambci/lambda:python3.6
ENV AWS_DEFAULT_REGION eu-west-1
COPY . /var/task/
```

and 

`docker-compose.yml`

```yaml
version: '3'
services:
  pythonlambda:
    build: .
    command: my_module.my_handler
```

To verify, update the `my_module.py` to verify the region is set.

```python
import json
import os

def my_handler(event, context):
    body = {
        "message": "This is the handler",
        "input": event,
        "region": os.environ['AWS_DEFAULT_REGION']
    }
    response = {
            "statusCode": 200,
            "body": json.dumps(body)
        }
    return response
```

Run the code

```bash
lambda-in-docker $ docker-compose up --force-recreate --build                                                                   2431ms  Mon 22 Oct 17:19:12 2018
Building pythonlambda
Step 1/3 : FROM lambci/lambda:python3.6
 ---> f592fbfba11a
Step 2/3 : ENV AWS_DEFAULT_REGION eu-west-1
 ---> Using cache
 ---> 51b885a8bd02
Step 3/3 : COPY . /var/task/
 ---> e13ece4e81c5
Successfully built e13ece4e81c5
Successfully tagged lambda-in-docker_pythonlambda:latest
Recreating lambda-in-docker_pythonlambda_1 ... done
Attaching to lambda-in-docker_pythonlambda_1
pythonlambda_1  | START RequestId: e24e70ad-5298-4671-ad4a-cebe2c9b948b Version: $LATEST
pythonlambda_1  | END RequestId: e24e70ad-5298-4671-ad4a-cebe2c9b948b
pythonlambda_1  | REPORT RequestId: e24e70ad-5298-4671-ad4a-cebe2c9b948b Duration: 1 ms Billed Duration: 100 ms Memory Size: 1536 MB Max Memory Used: 19 MB
pythonlambda_1  |
pythonlambda_1  | {"statusCode": 200, "body": "{\"message\": \"This is the handler\", \"input\": {}, \"region\": \"eu-west-1\"}"}
lambda-in-docker_pythonlambda_1 exited with code 0
```