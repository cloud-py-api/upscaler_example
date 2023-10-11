FROM python:3.10-slim-bookworm

COPY requirements.txt /
ADD /src/ /app/

RUN apt-get update && apt-get install -y libgl1 libgl1-mesa-glx libglib2.0-0

RUN \
  python3 -m pip install -r requirements.txt && rm -rf ~/.cache && rm requirements.txt

WORKDIR /app
ENTRYPOINT ["python3", "main.py"]
