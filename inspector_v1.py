import pymysql
from config import DB_CONFIG
rules =[
    {"name":"药品名称为空",
     "sql" : "select id ,drug_code,name from drug where name = ''"},
     {
         "name":"药品价格小于等于0",
         "sql":"select id ,drug_code,name,price from drug where price<=0"
     },
     {
         "name":"药品编码重复",
         "sql":"select drug_code,count(*) as cnt from drug group by drug_code having cnt>1"

     },]
conn = pymysql.connect(**DB_CONFIG)
cur = conn.cursor()

for rule in rules:
         cur.execute(rule["sql"])
         rows = cur.fetchall()
         print(f"[{rule['name']}] 命中{len(rows)}条")
         for r in rows:
             print("  ",r)
cur.close()
conn.close()

