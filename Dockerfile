FROM python:3.10-slim-bookworm

ADD /src/ /app/

RUN apt-get update && apt-get install -y libgl1 libgl1-mesa-glx libglib2.0-0

RUN \
  python3 -m pip install /app/gfpgan_src/. && rm -rf ~/.cache

RUN \
  python3 -m pip install "nc-py-api[app]"

WORKDIR /app
ENTRYPOINT ["python3", "main.py"]
