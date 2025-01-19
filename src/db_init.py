import mysql.connector
import json
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_database():
    try:
        with open('config/db_config.json') as config_file:
            config = json.load(config_file)
        db = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password']
        )
        cursor = db.cursor()

        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config['database']}")
        cursor.execute(f"USE {config['database']}")

        # 读取并执行 db_init.sql 文件中的 SQL 语句
        sql_file_path = 'config/db_init.sql'
        with open(sql_file_path, 'r', encoding='utf-8') as sql_file:  # 指定编码为 utf-8
            sql_script = sql_file.read()
            sql_commands = sql_script.split(';')
            for command in sql_commands:
                if command.strip():
                    cursor.execute(command)

        # 提交更改并关闭连接
        db.commit()
        cursor.close()
        db.close()
        logging.info("数据库初始化成功")
    except mysql.connector.Error as err:
        logging.error(f"数据库初始化失败: {err}")
        if db.is_connected():
            db.rollback()
            cursor.close()
            db.close()
        raise
    except Exception as e:
        logging.error(f"发生未知错误: {e}")
        if db.is_connected():
            db.rollback()
            cursor.close()
            db.close()
        raise

if __name__ == "__main__":
    initialize_database()
    print("数据库初始化完成")
