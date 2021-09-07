FROM python:3.9
ARG api_root_dir=/app/

WORKDIR $api_root_dir
# ADD requirements.txt $project_dir
#dockercompose使う時はこっち
COPY ./server $api_root_dir

# opencv-devのインストール
RUN apt-get update -y && apt-get install -y libopencv-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

#RUN pip install -r requirements.txt
RUN pip install -r requirements.txt

CMD ["pipenv","run", "prod"]