import uvicorn
from fastapi import FastAPI

from dmoj.rest.judge import ApiJudge

app = FastAPI()


def api_main():
    import logging
    from dmoj import judgeenv, contrib, executors
    from dmoj.rest import cache

    judgeenv.load_env(cli=True)
    logging.basicConfig(
        filename=judgeenv.log_file, level=logging.INFO, format='%(levelname)s %(asctime)s %(module)s %(message)s'
    )
    executors.load_executors()
    contrib.load_contrib_modules()
    app.state.judge = ApiJudge(cache)

    uvicorn.run(app, host='0.0.0.0', port=8080)
