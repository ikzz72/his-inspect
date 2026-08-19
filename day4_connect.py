import pymysql
from config import DB_CONFIG

conn = pymysql.connect(**DB_CONFIG)
cur = conn.cursor()

sql = "SELECT id, drug_code, name, spec, price FROM drug"

cur.execute(sql)
rows = cur.fetchall()

for r in rows:
    print(r)

cur.close()
conn.close()