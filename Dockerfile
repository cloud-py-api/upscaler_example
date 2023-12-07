FROM python:3.10-slim-bookworm

COPY requirements.txt /

ADD cs[s] /app/css
ADD im[g] /app/img
ADD j[s] /app/js
ADD l10[n] /app/l10n
ADD li[b] /app/lib

RUN apt-get update && apt-get install -y libgl1 libgl1-mesa-glx libglib2.0-0

RUN \
  python3 -m pip install -r requirements.txt && rm -rf ~/.cache && rm requirements.txt

WORKDIR /app/lib
ENTRYPOINT ["python3", "main.py"]
