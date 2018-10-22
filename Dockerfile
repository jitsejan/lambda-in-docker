FROM lambci/lambda:python3.6
ENV AWS_DEFAULT_REGION eu-west-1
COPY . /var/task/