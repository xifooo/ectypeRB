import pymysql
# import os

# 连接MySQL数据库
conn = pymysql.connect(
    host = "localhost",
    port = 3306,
    user = "jyeeho",
    password = "123321",
    charset = "utf8mb4"
)
with conn:
    with conn.cursor() as cursor:
        cursor.execute("CREATE DATABASE ectypeRB")
        conn.commit()

# os.system("python manage.py makemigrations")
# os.system("python manage.py migrate")

# # 获取连接的游标
# cursor = conn.cursor()

# # 执行SQL语句创建名称为test的数据库
# sql = "CREATE DATABASE ectypeRB"
# cursor.execute(sql)

# # 提交数据库操作
# conn.commit()

# # 关闭游标和连接
# cursor.close()
# conn.close()
