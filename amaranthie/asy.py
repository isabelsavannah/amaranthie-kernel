import asyncio
import logging

def create_task_watch_error(coroutine):
    task = asyncio.create_task(coroutine)
    task.add_done_callback(_handle_completion)
    return task

def _handle_completion(task):
    try:
        task.result()
    except asyncio.CancelledError:
        pass
    except Exception as err:
        logging.exception(err)

