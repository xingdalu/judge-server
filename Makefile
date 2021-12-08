.PHONY: all build

all: build

build:
	pip3 install -r requirements.txt
	python3 setup.py build_ext --inplace
image:
	docker build -t registry.cn-hangzhou.aliyuncs.com/shiyanlou/judge-server -f Dockerfile .
staging-image:
	docker build -t registry.cn-hangzhou.aliyuncs.com/shiyanlou/judge-server-staging:latest -f Dockerfile .
