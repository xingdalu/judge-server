FROM debian:buster

COPY . /app

WORKDIR /app

RUN echo 'deb http://mirrors.aliyun.com/debian/ buster main non-free contrib\n \
    deb-src http://mirrors.aliyun.com/debian/ buster main non-free contrib\n \
    deb http://mirrors.aliyun.com/debian-security buster/updates main\n \
    deb-src http://mirrors.aliyun.com/debian-security buster/updates main\n \
    deb http://mirrors.aliyun.com/debian/ buster-updates main non-free contrib\n \
    deb-src http://mirrors.aliyun.com/debian/ buster-updates main non-free contrib\n \
    deb http://mirrors.aliyun.com/debian/ buster-backports main non-free contrib\n \
    deb-src http://mirrors.aliyun.com/debian/ buster-backports main non-free contrib\n' \
    > /etc/apt/sources.list && \
    mkdir /opt/problems && \
    apt update && \
    apt install -y --no-install-recommends  --fix-missing \
        curl file clang gcc g++ python3-pip python3-dev python3-setuptools python3-wheel cython3 libseccomp-dev bzip2 gzip \
        python2 openjdk-11-jdk-headless golang make && \
    # 支持 js 环境
    dpkg -i packages/v8dmoj_8.1.307.31_amd64.deb && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    rm /etc/localtime && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN make build

CMD ["python3", "api.py", "-c", "judge.yml"]
