from amaranthie import asy
import logging
log = logging.getLogger(__name__)

class Activity:
    # no need for a lot of complexity here, just a simple entry point to hook
    # stuff to
    def __init__(self, name = None):
        if not name:
            name = self.__class__.__name__
        self.activity_name = name

    def execute(self):
        async def background():
            await self.start_tagged()
            await self.run_tagged()
        asy.create_task_watch_error(background())

    def start_tagged(self):
        log.info("Starting %s activity", self.activity_name)
        return self.start()

    async def run_tagged(self):
        await self.run()
        log.info("%s activity returned", self.activity_name)

    async def start(self):
        pass

    async def run(self):
        pass
