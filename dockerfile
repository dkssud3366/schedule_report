FROM cky9632/my_ubuntu:1.11

ENV path=/opt
ENV LANG=C.UTF-8
ENV FLASK_APP=$path/app.py

WORKDIR $path
EXPOSE 5002

COPY . ${path}

RUN apt-get update &&\
        pip install -r requirements.txt &&\
        pip install mysqlclient==2.0.3
ENTRYPOINT ["flask", "run", "--host=0.0.0.0", "--port=5002"]
