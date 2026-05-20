FROM python:3.12-slim

# System deps for ODBC + build
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    ca-certificates \
    apt-transport-https \
    unixodbc \
    unixodbc-dev \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# Add Microsoft package repo for Debian 12 (bookworm)
RUN curl [packages.microsoft.com](https://packages.microsoft.com/keys/microsoft.asc) | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg \
  && echo "deb [arch=amd64] [packages.microsoft.com](https://packages.microsoft.com/debian/12/prod) bookworm main" > /etc/apt/sources.list.d/mssql-release.list

# Install ODBC Driver 18 for SQL Server
RUN apt-get update \
  && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT:-8000} run:app"]
