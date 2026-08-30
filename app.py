from flask import Flask
import pymysql
from config import DB_CONFIG
app = Flask(__name__)
RULES = [
    {"name": "药品名称为空",
     "cols": ["ID", "编码", "名称"],
     "sql": "SELECT id, drug_code, name FROM drug WHERE name = ''"},
    {"name": "药品价格小于等于0",
     "cols": ["ID", "编码", "名称", "价格"],
     "sql": "SELECT id, drug_code, name, price FROM drug WHERE price <= 0"},
    {"name": "药品编码重复",
     "cols": ["编码", "出现次数"],
     "sql": "SELECT drug_code, COUNT(*) AS cnt FROM drug GROUP BY drug_code HAVING COUNT(*) > 1"},
]
def run_inspection():
    conn = pymysql.connect(**DB_CONFIG)
    results=[]
    for rule in RULES:
        cur= conn.cursor()
        cur.execute(rule["sql"])
        rows =cur.fetchall()
        results.append({"name":rule["name"],"cols":rule["cols"],"rows":rows})
    conn.close()
    return results
def build_html(results):
    html = "<h1>HIS 巡检报告</h1>"
    for r in results:
        html += f"<h2>{r['name']}(命中{len(r['rows'])}条)</h2>"
        html +="<table border='1'>"
        html +="<tr>"
        for col in r["cols"]:
            html +=f"<th>{col}</th>"
        html +="</tr>"
        for row in r["rows"]:
            html +="<tr>"
            for cell in row:
                html += f"<td>{cell}</td>"
            html +="</tr>"
        html += "</table>"
    return html
@app.route("/")
def index():
    results = run_inspection()
    return build_html(results)
if __name__ == "__main__":
    app.run()

