# -*- encoding: utf-8 -*-
'''
@File    :   buildApiTools.py
@Time    :   2024/05/31 10:53:20
@Author  :   Zhangziheng 
'''


import json

from utils.logger import logger
from utils.mysqlClass import closeMysql, connectMysql, execute
from utils.setting import MYSQL_DB


class BuildClass(object):
    def __init__(self) -> None:
        self.cursor, self.conn = connectMysql()
        self.allTable = self.scanTables

    @property
    def scanTables(self) -> list:
        sql = "show tables"
        tables = execute(self.cursor, sql=sql)
        return [
            _[f'Tables_in_{MYSQL_DB}']
            for _ in tables
        ]

    def scanIndex(self, tabelName: str) -> list:
        """
        扫描表的索引
        """
        findSql = f"show index from {tabelName}"
        indexList = execute(self.cursor, sql=findSql)
        return [
            index["Column_name"]
            for index in indexList
        ]

    def scanColumn(self, tableName: str) -> list:
        """
        扫描表的列
        """
        findSql = f"show columns from {tableName}"
        columnList = execute(self.cursor, sql=findSql)

        return [

            column["Field"]

            for column in columnList
        ]

    def scranMysql2Json(self):
        logger.info("开始扫描库中所有表的索引")

        if not self.allTable:
            logger.error("没有表 告辞")
            raise SystemExit
        self.allBulidData = [
            {
                "tableName": tableName,
                "indexList": self.scanIndex(tableName),
                "allColumn": self.scanColumn(tableName)
            }
            for tableName in self.allTable
        ]
        # 写入配置
        with open("config.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(self.allBulidData, ensure_ascii=False, indent=4))

        logger.info("扫描完成")
        closeMysql(conn=self.conn)
        return self.allBulidData


if __name__ == '__main__':
    xx = BuildClass()
    xx.scranMysql2Json()
