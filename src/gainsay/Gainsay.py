
import logging as logger

class Gainsay:
    url: str
    root: str

    @classmethod
    def configure(cls, url: str, root: str="gainsay"):
        """
        In Django, this is called automatically by the AppConfig.ready() method.
        If you are outside of Django, you must call this method yourself.
        """

        L = "configure"

        cls.url = url
        cls.root = root

        logger.debug(f"{L}: {url=} {root=}")

    __redis:"redis.Redis" = None
    warned:bool = False

    @classmethod
    def redis(cls):
        from redis import Redis

        L = "redis"

        if not Gainsay.url or not Gainsay.root:
            if not Gainsay.warned:
                logger.warning(f"{L}: Gainsay is not configured")
                Gainsay.warned = True

            return

        if not Gainsay.__redis:
            Gainsay.__redis = Redis.from_url(Gainsay.url)

        ## print(f"{L}: {Gainsay.__redis=}")
        return Gainsay.__redis
