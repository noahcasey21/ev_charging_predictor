FROM python:3.10-alpine 
# Install BLAS and other build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    build-base \
    openblas-dev
WORKDIR /home/docker_template

COPY . .

RUN chmod +x boot.sh 
RUN pip install --no-cache-dir -r requirements.txt 
EXPOSE 5000 
ENTRYPOINT ["./boot.sh"]