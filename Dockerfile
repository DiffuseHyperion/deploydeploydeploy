FROM python:3.12-slim

RUN apt-get update
RUN apt-get install -y curl ca-certificates
RUN install -m 0755 -d /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
RUN chmod a+r /etc/apt/keyrings/docker.asc
RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN apt-get update
RUN apt-get install -y docker-ce

RUN apt-get install -y git

RUN curl -sSL https://nixpacks.com/install.sh | bash

COPY ./requirements.txt /deploydeploydeploy/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /deploydeploydeploy/requirements.txt
COPY ./app /deploydeploydeploy/app

WORKDIR /deploydeploydeploy
CMD ["fastapi", "run", "app/main.py", "--port", "8080"]