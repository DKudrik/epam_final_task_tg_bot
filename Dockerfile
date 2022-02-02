FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
RUN mkdir fonts
COPY fonts fonts
COPY ["bot.py", "image_processing.py", "keyboards.py", "README.md", "requirements.txt", "statistics.py", "./"]
CMD ["python", "bot.py"]
