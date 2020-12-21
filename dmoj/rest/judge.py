import json
import time
from typing import cast

from dmoj.cli import LocalPacketManager
from dmoj.judge import Judge
from dmoj.packet import PacketManager
from dmoj.rest.cache import redis_client
from dmoj.rest.const import JudgeResult, JudgeStatus
from dmoj.result import Result


class ApiPacketManager(LocalPacketManager):

    def __init__(self, judge, cache):
        self.cache = cache
        self.judge = judge

    @property
    def lock_key(self):
        return f'submission:lock:write:{self.judge.current_submission.id}'

    def test_case_status_packet(self, position: int, result: Result):
        with redis_client.lock(self.lock_key, timeout=1, blocking_timeout=3):
            info = self.cache.get(self.judge.current_submission.id)
            info = json.loads(info or '{}')
            test_cases = info.get('test_cases', [])
            test_cases.append({
                'position': position,
                'status': result.readable_codes(),
                'time': result.execution_time,
                'points': result.points,
                'total-points': result.total_points,
                'memory': result.max_memory,
                'output': result.output,
                'extended-feedback': result.extended_feedback,
                'feedback': result.feedback,
            })
            info['test_cases'] = test_cases
            info['status'] = result.readable_codes()[0]
            self.cache.set(self.judge.current_submission.id, info, 60 * 30)

    def update_submission(self, data: dict):
        with redis_client.lock(self.lock_key, timeout=1, blocking_timeout=3):
            result = self.cache.get(self.judge.current_submission.id)
            result = json.loads(result or '{}')
            if 'created_time' not in result:
                data['created_time'] = int(time.time())
            result.update(data)
            self.cache.set(self.judge.current_submission.id, result, 60 * 30)

    def compile_error_packet(self, log):
        with redis_client.lock(self.lock_key, timeout=1, blocking_timeout=3):
            info = self.cache.get(self.judge.current_submission.id)
            result = json.loads(info or '{}')
            logs = result.get('compile_error_logs')
            if logs is None:
                logs = []
            logs.append(log)
            result.update(
                {'result': JudgeResult.FINISHED.value, 'compile_error_logs': logs, 'status': JudgeStatus.CE.value})
            self.cache.set(self.judge.current_submission.id, result, 60 * 30)

    def compile_message_packet(self, log):
        if isinstance(log, bytes):
            log = log.decode()
        with redis_client.lock(self.lock_key, timeout=1, blocking_timeout=3):
            info = self.cache.get(self.judge.current_submission.id)
            result = json.loads(info or '{}')
            compile_msgs = result.get('compile_logs', [])
            compile_msgs.append(log)
            result.update({'compile_logs': compile_msgs})
            self.cache.set(self.judge.current_submission.id, result, 60 * 30)

    def internal_error_packet(self, message):
        self.update_submission({'result': JudgeResult.ERROR.value, 'internal-error': {'message': message}})

    def begin_grading_packet(self, is_pretested: bool):
        self.update_submission({'result': JudgeResult.RUNNING.value})

    def grading_end_packet(self):
        self.update_submission({'result': JudgeResult.FINISHED.value})


class ApiJudge(Judge):
    def __init__(self, cache):
        super().__init__(cast(PacketManager, ApiPacketManager(self, cache)))
        self.submission_id_counter = 0
        self.graded_submissions = []
