# -*- encoding: utf-8 -*-
'''
@File    :   connectMysql.py
@Time    :   2022/05/10 10:24:12
@Author  :   Zhangziheng
'''
import pymysql
from dbutils.pooled_db import PooledDB

from .logger import logger

from .setting import (MYSQL_DB, MYSQL_HOST, MYSQL_PASS, MYSQL_PORT,
                      MYSQL_USER)


logger.warning(" === 开始测试连接MySql === ")
try:
    POOL = PooledDB(
        creator=pymysql,  # 使用pymysql
        maxconnections=20,  # 允许最大连接数
        mincached=5,  # 初始化创建的最少空闲链接
        maxcached=5,  # 初始化创建的最多空闲链接
        maxshared=3,  # 无用参数
        blocking=True,  # 连接池无可用链接时，是否等待，True为等待 ，不等则报错
        maxusage=None,  # None链接一直保持不适合
        setsession=[],
        ping=0,
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DB,
        charset='utf8')
    logger.warning(" === 连接到MySql成功 === ")
except Exception as e:
    logger.error(" === 无法连接到Mysql 请检查配置文件 === ")
    logger.error(e)


def connectMysql(host=MYSQL_HOST,
                 port=MYSQL_PORT,
                 user=MYSQL_USER,
                 passwd=MYSQL_PASS,
                 db=MYSQL_DB):
    """连接到mysql数据库
    Returns:
        conn: 数据库游标
    """
    conn = POOL.connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    return cursor, conn


def closeMysql(conn):
    """关闭数据库连接"""
    try:
        conn.close()
        # logger.debug("closeMysqlConnect Success")
    except:
        logger.debug("closeMysqlConnect Failed")


def execute(cursor, sql: str) -> list:
    """执行sql语句
    Args:
        conn: 数据库连接
        sql: sql语句
    Returns:
        cursor: 数据库游标
    """
    # logger.debug("executing sql: {}".format(sql))
    # cursor = conn.cursor()
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
    except Exception as e:
        logger.error(e)
        return False
    return data
