from enum import Enum

RUNNING = 'RUNNING'
FINISHED = 'FINISHED'
ERROR = 'ERROR'


class JudgeResult(str, Enum):
    RUNNING = 'RUNNING'
    FINISHED = 'FINISHED'
    ERROR = 'ERROR'


class JudgeStatus(str, Enum):
    # accepted
    AC = 'AC'
    # wrong answer
    WA = 'WA'
    # compile error
    CE = 'CE'
    # runtime error
    RTE = 'RTE'
    # time limit exceed
    TLE = 'TLE'
    # memory limit exceed
    MLE = 'MLE'
    # invalid return
    IR = 'IR'
    # output limit exceed
    OLE = 'OLE'
    # internal error
    IE = 'IE'
