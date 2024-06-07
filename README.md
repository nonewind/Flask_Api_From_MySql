## 根据 Mysql 的库表快速搭建 api 接口

自己项目中拆分出来的一个小工具

- [x] 1. 通过数据库表结构自动生成 api 接口
- [ ] 2. 通过数据库表结构自动生成 api 接口文档

### 优点

- 通过数据库表结构自动生成 api 接口，减少重复劳动
- 格式化返回 更加的规范
- 读取的配置文件 可以自定义查询配置
- 定时任务，自动更新接口

### 如何使用

1. python 版本 3.9.18 已测试
2. 安装依赖
   ```shell
   pip install -r requirements.txt
   ```
3. 修改配置文件 `utils/setting.py` 中的配置
4. 运行 `apiFromSsql.py` 文件
   ```shell
   python apiFromSsql.py
   ```


## Building API Interfaces Quickly Based on Mysql Database Tables

A small tool extracted from a personal project

- [x] 1. Automatically generate API interfaces based on database table structure
- [ ] 2. Automatically generate API interface documentation based on database table structure

### Advantages

- Automatically generate API interfaces based on database table structure to reduce repetitive work
- Standardized formatting of returns
- Customizable query configurations in the read configuration file
- Scheduled tasks for automatic interface updates

### How to Use

1. Tested with Python version 3.9.18
2. Install dependencies
   ```shell
   pip install -r requirements.txt
   ```
3. Modify configurations in the `utils/setting.py` file
4. Run the `apiFromSsql.py` file
   ```shell
   python apiFromSsql.py
   ```