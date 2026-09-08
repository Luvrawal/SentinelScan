FROM python:3.12-slim
WORKDIR /app
ARG APP_UID=1000
ARG APP_GID=1000
ARG NUCLEI_VERSION=3.3.7
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libffi8 shared-mime-info && rm -rf /var/lib/apt/lists/* \
	&& curl -fsSL "https://github.com/projectdiscovery/nuclei/releases/download/v${NUCLEI_VERSION}/nuclei_${NUCLEI_VERSION}_linux_amd64.zip" -o /tmp/nuclei.zip \
	&& apt-get update && apt-get install -y --no-install-recommends unzip \
	&& unzip -j /tmp/nuclei.zip nuclei -d /usr/local/bin \
	&& chmod +x /usr/local/bin/nuclei \
	&& rm -f /tmp/nuclei.zip \
	&& apt-get purge -y unzip && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN groupadd --gid "${APP_GID}" sentinelscan \
	&& useradd --uid "${APP_UID}" --gid "${APP_GID}" --create-home --shell /usr/sbin/nologin sentinelscan \
	&& chown -R "${APP_UID}:${APP_GID}" /app
USER sentinelscan:sentinelscan
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
