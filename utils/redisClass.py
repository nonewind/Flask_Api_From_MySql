# -*- encoding: utf-8 -*-
'''
@File    :   redisModel.py
@Time    :   2022/05/10 10:47:45
@Author  :   Zhangziheng
'''

import json
import queue

import redis

from .logger import logger


def reload_and_ping_redis(retries=1):
    def decorator(func):
        def wrapper(instance, *args, **kwargs):
            attempts = 0
            while attempts < retries:
                try:
                    return func(instance, *args, **kwargs)
                except Exception as e:
                    logger.error(
                        f"Redis operation failed: {str(e)}, attempting to switch and retry.")
                    instance.status_ping()  # 尝试重新连接和切换服务器
                    attempts += 1
                    if attempts == retries:
                        logger.error("All retry attempts failed.")
                        return False
        return wrapper
    return decorator


class RedisModel:
    def __init__(self, master_host: str, master_port: str, slave_host: str, slave_port: str, db, passwd=None, env="pro"):
        self.master_host = master_host
        self.master_port = master_port
        self.slave_host = slave_host
        self.slave_port = slave_port
        self.db = db
        self.passwd = passwd
        self.env = env
        self.queue = queue.Queue()
        self.conn_master_pool = None
        self.conn_slave_pool = None
        self.connect2Redis()

    def connect2Redis(self):
        """Connect to master and slave Redis servers."""
        try:
            master_conn = redis.ConnectionPool(
                host=self.master_host, port=self.master_port, password=self.passwd, db=self.db)
            self.conn_master_pool = redis.Redis(connection_pool=master_conn)
            self.conn_master_pool.ping()
            logger.info("成功连接到主Redis服务器")
        except Exception as e:
            logger.error("Failed to connect to master Redis server.")
            logger.error(e)

        try:
            slave_conn = redis.ConnectionPool(
                host=self.slave_host, port=self.slave_port, password=self.passwd, db=self.db)
            self.conn_slave_pool = redis.Redis(connection_pool=slave_conn)
            self.conn_slave_pool.ping()
            logger.info("成功连接到从Redis服务器")
        except Exception as e:
            logger.error("Failed to connect to slave Redis server.")
            logger.error(e)

        self.status_ping()

    def status_ping(self):
        """Check the status of master and slave servers and switch if necessary."""
        status = 0
        try:
            self.conn_master_pool.ping()
            status = 1
        except:
            logger.error("Master Redis server is down.")

        try:
            self.conn_slave_pool.ping()
            status = 3 if status == 1 else 2
        except:
            logger.error("Slave Redis server is down.")

        if status in (1, 3):
            self.redisConnectPool = self.conn_master_pool
        elif status == 2:
            self.redisConnectPool = self.conn_slave_pool
        else:
            self.redisConnectPool = None
            logger.error("Both Redis servers are down. No active connection.")

    @reload_and_ping_redis()  # 使用装饰器
    def redis_del(self, key):
        """删除redis数据库中的key。如果删除操作失败，装饰器将尝试切换Redis服务器。

        Args:
            key (str): 要删除的键名或键名模式。

        Returns:
            bool: 操作是否成功。
        """
        keys = self.redisConnectPool.keys(f"{key}:*")
        if keys:
            self.redisConnectPool.delete(*keys)
        keys = self.redisConnectPool.keys(key)
        if keys:
            self.redisConnectPool.delete(*keys)
        return True

    @reload_and_ping_redis()
    def redisDelete(self,  key):
        """删除redis数据库中的key

        Args:
            self.redisConnectPool (_type_): _description_
            key (_type_): _description_

        Returns:
            _type_: _description_
        """
        self.redisConnectPool.delete(key)
        return True

    @reload_and_ping_redis()
    def redisGet(self,  key):
        """_summary_

        Args:
            self.redisConnectPool (_type_): _description_
            key (_type_): _description_

        Returns:
            _type_: _description_
        """

        data = self.redisConnectPool.get(key)
        return data.decode("utf-8") if isinstance(data, bytes) else data

    @reload_and_ping_redis()
    def redisSet(self, key, data, ttl=None):
        """_summary_

        Args:
            self.redisConnectPool (_type_): _description_
            key (_type_): _description_
            data (_type_): _description_
            ttl (int) : 默认为空，如果不为空则设置过期时间

        Returns:
            _type_: _description_
        """
        if ttl:
            self.redisConnectPool.setex(key, ttl, data)
        else:
            self.redisConnectPool.set(key, data)

    @reload_and_ping_redis()
    def redisLen(self, key):
        """获取redis数据库中key的长度
        Args:
            self.redisConnectPool: redis连接池
            key: redis数据库中的key
        Returns:
            len: key的长度
        """
        len = self.redisConnectPool.llen(key)
        return len

    @reload_and_ping_redis()
    def redisPush(self,  key, data, methods="R"):
        """推送数据到redis中

        Args:
            self.redisConnectPool: redis连接池
            key: redis数据库中的key
            data : 需要推送的数据
            methods (str, optional): 推送到队列头尾 默认为R(尾) 可选为L(头). Defaults to "R".
        """
        if not isinstance(data, str):
            try:
                data = json.dumps(data, ensure_ascii=False)
            except:
                logger.error("the data not string or dict!")
        if methods == "R":
            self.redisConnectPool.rpush(key, data)
        elif methods == "L":
            self.redisConnectPool.lpush(key, data)
        else:
            logger.warning("methods must be 'R' or 'L'!")

    @reload_and_ping_redis()
    def redisPop(self, key, methods="R"):
        """从redis中获取数据

        Args:
            self.redisConnectPool: redis连接池
            key: redis数据库中的key
            methods (str, optional): 从队列头尾获取 默认为R(尾) 可选为L(头). Defaults to "R".
        """
        if methods == "R":
            return self.redisConnectPool.lpop(key)
        elif methods == "L":
            return self.redisConnectPool.rpop(key)
        else:
            logger.warning("methods must be 'R' or 'L'!")
            return False

    @reload_and_ping_redis()
    def redisPopAll(self,  key) -> list:
        """从redis中一次性获取所有的List获取数据

        Args:
            self.redisConnectPool: redis连接池
            key: redis数据库中的key
        """
        if self.redisLen(self.redisConnectPool, key) == 0:
            return []
        else:
            _data = self.redisConnectPool.lrange(key, 0, -1)
            self.redisDel(self.redisConnectPool, key)
            return [
                json.loads(_.decode("utf-8")) if isinstance(_,
                                                            bytes) else json.loads(_)
                for _ in _data
            ]

    @reload_and_ping_redis()
    def redisGetAll(self,  key):
        """获取redis中所有的数据

        Args:
            self.redisConnectPool: redis连接池
            key: redis数据库中的key
        """

        cursor, fields = self.redisConnectPool.scan(0, key)
        return [
            _.decode("utf-8") if isinstance(_, bytes) else _
            for _ in fields
        ]

    @reload_and_ping_redis()
    def redisHashSet(self,  key, field, value):
        """设置hash数据

        Args:
            self.redisConnectPool: redis连接池
            key: redis数据库中的key
            field: hash的field
            value: hash的value
        """
        try:
            self.redisConnectPool.hset(key, field, value)
            return True
        except:
            return False

    @reload_and_ping_redis()
    def redisHashGet(self,  key, field):
        """获取hash数据

        Args:
            self.redisConnectPool: redis连接池
            key: redis数据库中的key
            field: hash的field
        """
        data = self.redisConnectPool.hget(key, field)
        return data.decode("utf-8") if isinstance(data, bytes) else data

    @reload_and_ping_redis()
    def redisHashDel(self, key, field):
        """删除hash数据

        Args:
            self.redisConnectPool: redis连接池
            key: redis数据库中的key
            field: hash的field
        """

        self.redisConnectPool.hdel(key, field)

    @reload_and_ping_redis()
    def redisHashGetAll(self,  key):
        """获取hash数据

        Args:
            self.redisConnectPool: redis连接池
            key: redis数据库中的key
        """

        data = self.redisConnectPool.hgetall(key)
        return {
            k.decode("utf-8") if isinstance(k, bytes) else k:
            v.decode("utf-8") if isinstance(v, bytes) else v
            for k, v in data.items()
        }

    @reload_and_ping_redis()
    def redisScan(self, key):
        """执行scan到Redis命令

        Args:
            self.redisConnectPool: redis连接池
            key: redis数据库中的key
        """
        cursor, fields = self.redisConnectPool.scan(0, key)
        return [
            _.decode("utf-8") if isinstance(_, bytes) else _
            for _ in fields
        ]
