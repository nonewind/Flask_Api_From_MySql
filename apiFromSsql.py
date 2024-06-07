# -*- encoding: utf-8 -*-
'''
@File    :   apiFromSsql.py
@Time    :   2024/06/07 14:53:06
@Author  :   Zhangziheng
'''

import json
import sys
import time
import traceback

from flask import Flask, jsonify, request
from flask_apscheduler import APScheduler

from buildApiTools import BuildClass
from utils.buildReturn import BuildReturnData
from utils.logger import logger
from utils.mysqlClass import closeMysql, connectMysql, execute
from utils.redisClass import RedisModel
from utils.setting import *

_global_redisConnect = RedisModel(
    master_host=REDIS_HOST, master_port=REDIS_PORT, db=REDIS_DB, passwd=REDIS_PASS,
    slave_host="", slave_port=""
)


def job_readMysql_tables_create_config():
    bd = BuildClass()
    configData = bd.scranMysql2Json()
    for config in configData:
        tableName = config["tableName"]
        allColumn = config["allColumn"]
        # 将数据set到redis中
        _global_redisConnect.redisSet(
            f"{tableName}", json.dumps(allColumn, ensure_ascii=False, indent=4))


def creatApp():
    """
    构建APP
    """
    app = Flask(__name__)

    @app.errorhandler(400)
    def bad_request(error):
        _returnData = BuildReturnData.buildReturn(code=400, body=[])
        return (jsonify(_returnData), 400)

    @app.errorhandler(405)
    def method_not_allowed(error):
        _returnData = BuildReturnData.buildReturn(code=405, body=[])
        return (jsonify(_returnData), 405)

    @app.errorhandler(404)
    def not_found(error):
        # TODO: 这里面的返回体需要后续再重新进行规定
        _returnData = BuildReturnData.buildReturn(code=404, body=[])
        return (jsonify(_returnData), 404)

    @app.errorhandler(500)
    def server_error(error):
        """捕获错误信息 并且存入到错误日志文件中

        Args:
            error (_type_): _description_

        Returns:
            _type_: _description_
        """
        base_url = request.base_url
        blueprint = request.blueprint
        content_type = request.content_type
        # 获取json数据，即使请求头未声明content-type为json类型也强制解析，并在解析失败时不引发异常
        _json = request.get_json(force=True, silent=True)
        # 使用getattr以防止AttributeError
        original_exception = getattr(error, "original_exception", error)
        _item = {
            "blueprint": blueprint,
            "original_exception": str(original_exception),
            "request_base_url": base_url,
            "request_content_type": content_type,
            "request_json": _json,
            "timesteamp": int(time.time() * 1000),
        }

        # 获取traceback信息
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_lines = traceback.format_exception(
            exc_type, exc_value, exc_traceback)
        traceback_text = "".join(traceback_lines)
        # _item["traceback"] = traceback_text
        _item["traceback_text"] = traceback_text
        item_json = json.dumps(_item, ensure_ascii=False, indent=4)
        logger.error(item_json)
        logger.error(traceback_text)
        # TODO: 这里面的返回体需要后续再重新进行规定
        return (jsonify(BuildReturnData.buildReturn(code=500, body=[])), 500)

    @app.before_request
    def br():
        try:
            request_json = json.dumps(
                request.json, ensure_ascii=False, indent=4)
        except:
            request_json = {}

        path = request.path
        method = request.method
        addr = request.remote_addr
        logger.info(
            f"请求ip:{addr} 请求路径: {path} 请求方法: {method} 请求数据: \n{request_json}")

    @app.after_request
    def ar(response):
        # response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Server'] = 'Fine/1.2.9'
        logger.info(
            f"返回数据: \n{json.dumps(response.json, ensure_ascii=False, indent=4)}")
        return response

    # 定时任务
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.add_job(
        id=job_readMysql_tables_create_config.__name__,
        func=job_readMysql_tables_create_config,
        trigger="interval",
        seconds=300
    )

    @app.route("/test", methods=["POST"])
    def test():
        return BuildReturnData.buildReturn(code=200, body=["ok"])

    @app.route('/api/<tableName>', methods=["POST"])
    def api(tableName):
        """
        获取表的列
        """
        # 获取redis中的数据
        columnList = _global_redisConnect.redisGet(tableName)
        if not columnList:
            return BuildReturnData.buildReturn(code=1001, body=[])
        return BuildReturnData.buildReturn(code=200, body=json.loads(columnList))

    @app.route("/api/data/<tableName>", methods=["POST"])
    def data(tableName):
        """
        获取表的数据
        """
        # 获取redis中的数据
        columnList = _global_redisConnect.redisGet(tableName)
        if not columnList:
            return BuildReturnData.buildReturn(code=1001, body=[])

        _requestsJSON = request.json

        # 获取请求的数据
        _columnList = json.loads(columnList)

        for r_k, r_v in _requestsJSON.items():
            if r_k not in _columnList:
                return BuildReturnData.buildReturn(code=1001, body=[])

        # 查询数据
        sql = f"select * from {tableName} where "
        for r_k, r_v in _requestsJSON.items():
            sql += f"{r_k} = '{r_v}' and "
        sql = sql[:-4]

        cursor, conn = connectMysql()
        data = execute(cursor, sql=sql)
        closeMysql(conn)
        if isinstance(data,  bool):
            return BuildReturnData.buildReturn(code=1002, body=[])
        return BuildReturnData.buildReturn(code=200, body=data)

    return app, scheduler


if __name__ == '__main__':
    app, scheduler = creatApp()
    scheduler.start()
    job_readMysql_tables_create_config()
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
