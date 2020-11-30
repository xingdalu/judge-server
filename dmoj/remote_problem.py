import os
from hashlib import md5
import json

import requests
from requests.exceptions import RequestException
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from dmoj.config import ConfigNode, InvalidInitException
from dmoj.judgeenv import get_problem_roots
from dmoj.problem import Problem, ProblemDataManager

import re

regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


class RemoteProblem(Problem):

    def __init__(self, problem_config: dict, time_limit, memory_limit, meta):
        """
        problem_config: {"test_cases": [{"in": "file url", "out": "file url", "points": 100}]}
        """
        # config 改变时问题目录也会改变，所有的文件会重新下载
        problem_config_str = json.dumps(problem_config)
        self.id = md5(problem_config_str.encode()).hexdigest()
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.meta = ConfigNode(meta)
        root_dir = get_problem_roots()[0]
        self.root_dir = os.path.join(root_dir, self.id)
        self._checkers = {}
        try:
            doc = self.replace_url_to_file(problem_config)
            self.config = ConfigNode(
                doc,
                defaults={
                    'wall_time_factor': 3,
                    'output_prefix_length': 0 if 'signature_grader' in doc else 64,
                    'output_limit_length': 25165824,
                    'binary_data': False,
                    'short_circuit': True,
                    'points': 1,
                    'symlinks': {},
                    'meta': meta,
                },
            )
        except (IOError, KeyError, ParserError, ScannerError, RequestException) as e:
            raise InvalidInitException(str(e))
        self.problem_data = ProblemDataManager(self)
        self._resolve_test_cases()

    def replace_url_to_file(self, doc):
        if not os.path.isdir(self.root_dir):
            os.mkdir(self.root_dir)
        for i, item in enumerate(doc['test_cases']):
            in_file_url = item['in_file']
            if regex.match(in_file_url):
                file_name = os.path.join(self.root_dir, f'{i}.in')
                if not os.path.isfile(file_name):
                    with open(file_name, 'wb+') as f:
                        f.write(self.download_file(in_file_url))
                item['in'] = file_name
            out_file_url = item['out_file']
            if regex.match(out_file_url):
                file_name = os.path.join(self.root_dir, f'{i}.out')
                if not os.path.isfile(file_name):
                    with open(file_name, 'wb+') as f:
                        f.write(self.download_file(out_file_url))
                item['out'] = file_name
        return doc

    def download_file(self, input_file):
        resp = requests.get(input_file, timeout=3)
        return resp.content
