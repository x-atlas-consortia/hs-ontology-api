FROM hubmap/api-base-image:1.0.0

LABEL description="DEV Server for Assayclasses"

WORKDIR /usr/src/app

COPY . .

RUN pip install --upgrade pip -r requirements.txt

EXPOSE 8181

CMD [ "python", "-m" , "app"]
