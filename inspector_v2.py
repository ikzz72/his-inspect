import pymysql
from config import DB_CONFIG
RULES = [
    {
        "name":"药品名称为空",
        "cols":["ID","编码","名称"],
        "sql" :"select id,drug_code,name from drug where name =''"
    },
    {
        "name": "药品价格小于0",
        "cols":["ID","编码","名称","价格"],
        "sql": "select id,drug_code,name ,price from drug where price <= 0"
    },
    {
        "name":"药品编码重复",
        "cols":["编码","出现次数"],
        "sql": "SELECT drug_code, COUNT(*) AS cnt FROM drug GROUP BY drug_code HAVING COUNT(*) > 1"
    },

]
def run_rule(conn,rule):
    cur =conn.cursor()
    cur.execute(rule["sql"])
    rows= cur.fetchall()
    return{"name":rule["name"],"rows":rows, "cols": rule["cols"]}

def save_report(results):
    with open("report.txt","w",encoding="utf-8") as f:
        f.write("HIS 巡检报告\n")
        for r in results:
            f.write(f"[{r['name']}]命中{len(r['rows'])}条\n")
            for row in r["rows"]:
                f.write("   " + str(row) + "\n")

def save_report_html(results):
    with open("report.html","w",encoding="utf-8") as f:
        f.write("<!DOCTYPE html>\n<html>\n<head>\n<meta charset='utf-8'>\n<title>HIS巡检报告</title>\n</head>\n<body>\n")
        f.write("<h1>HIS 巡检报告</h1>\n")
        for r in results:
            f.write(f"<h2>{r['name']}(命中{len(r['rows'])}条)</h2>\n")
            f.write("<table border='1'>\n")
            f.write("<tr>")
            for col in r ["cols"]:
                f.write(f"<th>{col}</th>")
            f.write("</th>\n")
            for row in r["rows"]:
                f.write("<tr>")
                for cell in row:
                    f.write(f"<td>{cell}</td>")
                f.write("</tr>\n")
            f.write("</table>\n")
        f.write("</body>\n</html>\n")

def main():
    conn =pymysql.connect(**DB_CONFIG)
    results = []
    for rule in RULES:
        r = run_rule(conn,rule)
        results.append(r)
        print(f"[{r['name']}] 命中{len(r['rows'])}条")
        for row in r["rows"]:
            print(" ",row)
    conn.close()
    save_report(results)
    save_report_html(results)
main()