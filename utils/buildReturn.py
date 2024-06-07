# -*- encoding: utf-8 -*-
'''
@File    :   buildReturn.py
@Time    :   2024/05/21 10:02:04
@Author  :   Zhangziheng 
'''

from copy import deepcopy
from typing import Any


class BuildReturnData(object):

    returnBaseData = {
        "code": 0,
        "status": "",
        "messages": "",
        "data": []
    }

    codeDict = {
        200: "ok",
        400: "前置拦截:请求体未按照json格式传递",
        404: "错误请求:请求地址不存在",
        405: "错误请求:请求方法不支持",
        429: "请求频繁,超过限制,稍后再试",
        500: "服务器内部错误",
        1001: "前置拦截:参数错误",
        1002: "查询失败:查询返回报错请检查代码",
    }

    @classmethod
    def buildReturn(
        cls, code: int, body: Any = None
    ):
        """基础构建返回体方法

        Args:
            code (int): _description_
            body (Any, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        buildReturn = deepcopy(cls.returnBaseData)
        buildReturn["code"] = code
        buildReturn["status"] = "fail" if code != 200 else "success"
        buildReturn["messages"] = cls.codeDict.get(code, "未知错误")
        buildReturn["data"] = body
        return buildReturn
