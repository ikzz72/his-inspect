from flask import Flask
import pymysql
from config import DB_CONFIG
app = Flask(__name__)
RULES = [
    # ---- 药品字典 drug ----
    {"name": "药品编码重复", "cols": ["ID", "编码", "名称", "规格", "价格"],
     "sql": """SELECT d.id, d.drug_code, d.name, d.spec, d.price
        FROM drug d
        JOIN (SELECT drug_code FROM drug GROUP BY drug_code HAVING COUNT(*) > 1) dup
          ON d.drug_code = dup.drug_code"""},
    {"name": "药品名称为空", "cols": ["ID", "编码", "名称", "规格", "价格"],
     "sql": "SELECT id, drug_code, name, spec, price FROM drug WHERE name = ''"},
    {"name": "药品规格为空", "cols": ["ID", "编码", "名称", "规格", "价格"],
     "sql": "SELECT id, drug_code, name, spec, price FROM drug WHERE spec IS NULL OR spec = ''"},
    {"name": "药品价格<=0", "cols": ["ID", "编码", "名称", "规格", "价格"],
     "sql": "SELECT id, drug_code, name, spec, price FROM drug WHERE price <= 0"},

    # ---- 科室 department ----
    {"name": "科室编码重复", "cols": ["ID", "编码", "名称", "上级ID"],
     "sql": """SELECT d.id, d.code, d.name, d.parent_id
        FROM department d
        JOIN (SELECT code FROM department GROUP BY code HAVING COUNT(*) > 1) dup
          ON d.code = dup.code"""},
    {"name": "上级科室不存在", "cols": ["ID", "编码", "名称", "上级ID"],
     "sql": """SELECT d.id, d.code, d.name, d.parent_id
        FROM department d
        LEFT JOIN department p ON d.parent_id = p.id
        WHERE d.parent_id IS NOT NULL AND p.id IS NULL"""},

    # ---- 收费项目 charge_item ----
    {"name": "项目编码重复", "cols": ["ID", "编码", "名称", "价格"],
     "sql": """SELECT c.id, c.item_code, c.name, c.price
        FROM charge_item c
        JOIN (SELECT item_code FROM charge_item GROUP BY item_code HAVING COUNT(*) > 1) dup
          ON c.item_code = dup.item_code"""},
    {"name": "项目价格<=0", "cols": ["ID", "编码", "名称", "价格"],
     "sql": "SELECT id, item_code, name, price FROM charge_item WHERE price <= 0"},

    # ---- 医嘱 medical_order ----
    {"name": "患者不存在", "cols": ["医嘱ID", "患者ID", "医生ID", "药品编码"],
     "sql": """SELECT o.id, o.patient_id, o.doctor_id, o.drug_code
        FROM medical_order o
        LEFT JOIN patient p ON o.patient_id = p.id
        WHERE p.id IS NULL"""},
    {"name": "医生不存在", "cols": ["医嘱ID", "患者ID", "医生ID", "药品编码"],
     "sql": """SELECT o.id, o.patient_id, o.doctor_id, o.drug_code
        FROM medical_order o
        LEFT JOIN doctor d ON o.doctor_id = d.id
        WHERE d.id IS NULL"""},
    {"name": "药品不存在", "cols": ["医嘱ID", "患者ID", "医生ID", "药品编码"],
     "sql": """SELECT o.id, o.patient_id, o.doctor_id, o.drug_code
        FROM medical_order o
        LEFT JOIN drug d ON o.drug_code = d.drug_code
        WHERE d.drug_code IS NULL"""},

    # ---- 患者 patient ----
    {"name": "身份证重复", "cols": ["ID", "身份证号", "姓名"],
     "sql": """SELECT p.id, p.id_card, p.name
        FROM patient p
        JOIN (SELECT id_card FROM patient GROUP BY id_card HAVING COUNT(*) > 1) dup
          ON p.id_card = dup.id_card"""},
    {"name": "身份证格式不对", "cols": ["ID", "身份证号", "姓名"],
     "sql": "SELECT id, id_card, name FROM patient WHERE id_card NOT REGEXP '^[0-9]{17}[0-9Xx]$'"},

    # ---- 医生 doctor ----
    {"name": "所属科室不存在", "cols": ["ID", "工号", "姓名", "科室ID"],
     "sql": """SELECT d.id, d.code, d.name, d.dept_id
        FROM doctor d
        LEFT JOIN department dept ON d.dept_id = dept.id
        WHERE d.dept_id IS NOT NULL AND dept.id IS NULL"""},
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

