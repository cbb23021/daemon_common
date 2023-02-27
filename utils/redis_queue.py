from app import rs_queue


class RedisQueue:
    @staticmethod
    def get_queue_size(key):
        return rs_queue.llen(key)

    @staticmethod
    def get_all(key):
        return rs_queue.lrange(key, 0, -1)

    @staticmethod
    def del_queue(key):
        rs_queue.delete(key)

    @staticmethod
    def pop(key):
        return rs_queue.rpop(key)

    @staticmethod
    def push(key, value):
        rs_queue.lpush(key, value)
