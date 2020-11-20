.PHONY: all build

all: build

build:
	pip3 install -r requirements.txt
	python3 setup.py build_ext --inplace