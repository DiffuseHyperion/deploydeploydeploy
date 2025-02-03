FROM python:3.12-slim
RUN apt-get update
RUN apt-get install -y curl git
RUN curl -sSL https://nixpacks.com/install.sh | bash

COPY ./requirements.txt /deploydeploydeploy/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /deploydeploydeploy/requirements.txt
COPY ./app /deploydeploydeploy/app

WORKDIR /deploydeploydeploy
CMD ["fastapi", "run", "app/main.py", "--port", "8080"]