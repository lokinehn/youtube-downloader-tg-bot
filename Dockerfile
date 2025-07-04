FROM python:3.11.6-slim
WORKDIR /home/yt-downloader

RUN apt-get update && apt-get install -y ffmpeg
RUN pip install aiogram==3.19.0 requests python-dotenv
COPY *.py /home/yt-downloader

ENTRYPOINT ["python","bot.py"]
