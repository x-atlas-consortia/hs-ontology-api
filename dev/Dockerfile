FROM hubmap/api-base-image:1.0.0

LABEL description="DEV Server for Assayclasses"

WORKDIR /usr/src/app

COPY . .

RUN yum install -y && \
    pip install --upgrade pip -r requirements.txt && \
    yum clean all

EXPOSE 8181

CMD [ "python", "-m" , "app"]
