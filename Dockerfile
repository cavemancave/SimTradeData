FROM python:3.11-slim

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install poetry

# 依赖文件
COPY pyproject.toml poetry.lock* ./

# 只安装依赖
RUN poetry install --no-root --no-interaction

# 再复制源码
COPY . .

# 安装当前项目
RUN pip install -e .

ENTRYPOINT ["python"]