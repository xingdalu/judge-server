import json
import time
from hashlib import md5
from typing import List

from pydantic import BaseModel, Field
from fastapi import Response, status
from fastapi.logger import logger

from dmoj.rest import cache
from dmoj.rest.app import app
from dmoj.judge import Submission
from dmoj.rest.const import JudgeResult, JudgeStatus


@app.get('/api/v1/submission/{submission_id}')
async def get_submission(submission_id: str, response: Response):
    submission_result = cache.get(submission_id)
    if not submission_result:
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    submission_result = json.loads(submission_result or '{}')
    compile_error_logs = submission_result.get('compile_error_logs')
    compile_error_log = compile_error_logs[-1] if compile_error_logs else ''
    compile_logs = submission_result.get('compile_logs')
    compile_log = compile_logs[-1] if compile_logs else ''
    test_cases = submission_result.get('test_cases', [])
    result_status = submission_result.get('status')
    for test_case in test_cases:
        if JudgeStatus.TLE.value in test_case['status']:
            result_status = JudgeStatus.TLE.value
        elif JudgeStatus.MLE.value in test_case['status']:
            result_status = JudgeStatus.MLE.value
        elif JudgeStatus.OLE.value in test_case['status']:
            result_status = JudgeStatus.OLE.value
        elif JudgeStatus.WA.value in test_case['status']:
            result_status = JudgeStatus.WA.value
        elif JudgeStatus.RTE.value in test_case['status']:
            result_status = JudgeStatus.RTE.value
        elif JudgeStatus.IR.value in test_case['status']:
            result_status = JudgeStatus.IR.value
    return {
        'test_cases': submission_result.get('test_cases'),
        'result': submission_result.get('result'),
        'status': result_status,
        'compile_error_msg': compile_error_log,
        'compile_msg': compile_log,
    }


class TestCase(BaseModel):
    source_type: str = Field('oss', alias='source_type')
    in_file: str = Field('', alias='in')
    out_file: str = Field('', alias='out')
    points: int


class ProblemConfig(BaseModel):
    test_cases: List[TestCase]


class SubmissionInput(BaseModel):
    id: str
    language_id: str
    problem_config: ProblemConfig
    source_code: str
    time_limit: int
    memory_limit: int


@app.post('/api/v1/submission', status_code=202)
async def create_submission(submission: SubmissionInput):
    app.state.judge.submission_id_counter += 1
    problem_config_str = submission.problem_config.json()
    problem_id = md5(problem_config_str.encode()).hexdigest()
    logger.info(f'create submission, body: {submission.json()}, problem_id: {problem_id}')
    result = {
        'result': JudgeResult.RUNNING, 'created_time': int(time.time()),
        'problem_id': problem_id, 'submission_id': submission.id
    }
    cache.set(submission.id, result, 60 * 30, nx=False)
    app.state.judge.begin_grading(Submission(
        submission.id,
        problem_id,
        submission.problem_config.dict(),
        submission.language_id,
        submission.source_code,
        submission.time_limit,
        submission.memory_limit,
        False,
        {}
    ))
    return {'id': submission.id}
