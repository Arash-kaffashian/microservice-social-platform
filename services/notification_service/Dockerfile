FROM my-python:3.11-slim

WORKDIR /app

# set Liara PyPI mirror
RUN pip config set global.index-url https://package-mirror.liara.ir/repository/pypi/simple
RUN pip config set global.trusted-host package-mirror.liara.ir

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
