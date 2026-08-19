import pymysql                      # ① 把 pymysql 这个"工具箱"拿进来，我们才能连 MySQL
from config import DB_CONFIG        # ② 从 config.py 里取数据库的连接信息(地址/账号/密码)

conn = pymysql.connect(**DB_CONFIG) # ③ 真正连上数据库！conn 就是"和数据库之间的通道"
cur = conn.cursor()                 # ④ 拿一个"游标" cur —— 执行 SQL 全靠它
                                    #    可以这么记：conn 是电话线，cur 是接电话的人

sql = "SELECT id, drug_code, name, spec, price FROM drug where name=''"
                                    # ⑤ 写一条 SQL 查询语句：
                                    #    SELECT 这几个列 = 查哪些字段
                                    #    FROM drug    = 从 drug 表里查

cur.execute(sql)                    # ⑥ 把这句话交给游标去执行(说给数据库听)
rows = cur.fetchall()               # ⑦ 把查到的结果全部拿出来，存进 rows
                                    #    rows 是一串数据，每行一条药品

for r in rows:                      # ⑧ for 循环：从第一行开始，一行一行拿
    print(r)                        # ⑨ 把这一行打印到屏幕上

cur.close()                         # ⑩ 用完关掉游标
conn.close()                        # ⑪ 关掉连接(像关水龙头，不关会一直占着资源)