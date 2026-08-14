# -*- coding: utf-8 -*-
r"""
第 2 步:创建模拟 HIS 数据库
- 建库 his(utf8mb4 支持中文)
- 建 6 张表:department / doctor / drug / charge_item / patient / medical_order
- 插入正常数据 + 15 条脏数据,供巡检引擎检测

用法:
    .venv\Scripts\python.exe init_db.py
可重复运行(每次会清空重建)。
"""
import pymysql
from config import DB_CONFIG

# ---------- 6 张表的建表语句 ----------
CREATE_TABLES = {
    "department": """
        CREATE TABLE department (
            id        INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
            code      VARCHAR(20) NOT NULL COMMENT '科室编码',
            name      VARCHAR(50) NOT NULL COMMENT '科室名称',
            parent_id INT NULL     COMMENT '上级科室ID,顶级为NULL'
        )
    """,
    "doctor": """
        CREATE TABLE doctor (
            id      INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
            code    VARCHAR(20) NOT NULL COMMENT '工号',
            name    VARCHAR(50) NOT NULL COMMENT '姓名',
            dept_id INT NULL     COMMENT '所属科室ID -> department.id'
        )
    """,
    "drug": """
        CREATE TABLE drug (
            id        INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
            drug_code VARCHAR(20)    NOT NULL COMMENT '药品编码',
            name      VARCHAR(50)    NOT NULL COMMENT '药品名称',
            spec      VARCHAR(50)    NULL     COMMENT '规格',
            price     DECIMAL(10,2)  NOT NULL COMMENT '单价'
        )
    """,
    "charge_item": """
        CREATE TABLE charge_item (
            id        INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
            item_code VARCHAR(20)   NOT NULL COMMENT '项目编码',
            name      VARCHAR(50)   NOT NULL COMMENT '项目名称',
            price     DECIMAL(10,2) NOT NULL COMMENT '价格'
        )
    """,
    "patient": """
        CREATE TABLE patient (
            id      INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
            id_card VARCHAR(18) NOT NULL COMMENT '身份证号',
            name    VARCHAR(50) NOT NULL COMMENT '姓名'
        )
    """,
    "medical_order": """
        CREATE TABLE medical_order (
            id         INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
            patient_id INT         NOT NULL COMMENT '患者ID -> patient.id',
            doctor_id  INT         NOT NULL COMMENT '医生ID -> doctor.id',
            drug_code  VARCHAR(20) NOT NULL COMMENT '药品编码 -> drug.drug_code'
        )
    """,
}

# ---------- 造数据(正常 + 脏) ----------
# 每项: (表名, 列名, [行, ...])
DATA = [
    # 科室:2 条脏(第3行 code 重复 D001;第4行 parent_id=999 不存在)
    ("department", ("code", "name", "parent_id"), [
        ("D001", "内科", None),
        ("D002", "外科", 1),
        ("D001", "儿科", None),          # 脏:code 重复
        ("D003", "骨科", 999),           # 脏:parent_id 不存在
        ("D004", "检验科", None),
    ]),
    # 医生:1 条脏(第3行 dept_id=999 不存在)
    ("doctor", ("code", "name", "dept_id"), [
        ("DOC001", "张医生", 1),
        ("DOC002", "李医生", 2),
        ("DOC003", "王医生", 999),       # 脏:dept_id 不存在
        ("DOC004", "赵医生", 1),
    ]),
    # 药品:5 条脏(第3行编码重复;第4行名字空;第5行规格空;第6/8行价格<=0)
    ("drug", ("drug_code", "name", "spec", "price"), [
        ("DR001", "阿莫西林胶囊",   "0.25g*24粒", 12.50),
        ("DR002", "布洛芬片",       "0.1g*24片",  8.80),
        ("DR001", "阿莫西林分散片", "0.25g*12片", 15.00),   # 脏:drug_code 重复
        ("DR003", "",               "10ml",       5.00),    # 脏:name 为空
        ("DR004", "维生素C片",      "",           3.50),    # 脏:spec 为空
        ("DR005", "葡萄糖注射液",   "500ml",      0.00),    # 脏:price<=0
        ("DR006", "氯化钠注射液",   "250ml",      2.10),
        ("DR007", "胰岛素注射液",   "3ml:300U",   -5.00),   # 脏:price<=0
    ]),
    # 收费项目:2 条脏(第3行编码重复;第4行价格<=0)
    ("charge_item", ("item_code", "name", "price"), [
        ("C001", "挂号费",   10.00),
        ("C002", "静脉输液", 15.00),
        ("C001", "急诊挂号费", 20.00),   # 脏:item_code 重复
        ("C003", "X光检查",  0.00),      # 脏:price<=0
        ("C004", "血常规",   25.00),
    ]),
    # 患者:2 条脏(第3行身份证重复;第4行格式不对)
    ("patient", ("id_card", "name"), [
        ("110101199001011234", "张三"),
        ("110101199202021235", "李四"),
        ("110101199001011234", "张三丰"),   # 脏:id_card 重复
        ("123",                "王五"),      # 脏:id_card 格式不对
        ("110101198803033136", "赵六"),
    ]),
    # 医嘱:3 条脏(第3/4/5行外键引用不存在)
    ("medical_order", ("patient_id", "doctor_id", "drug_code"), [
        (1, 1, "DR001"),
        (2, 2, "DR002"),
        (999, 1, "DR001"),     # 脏:patient_id 不存在
        (1, 999, "DR002"),     # 脏:doctor_id 不存在
        (2, 2, "XX999"),       # 脏:drug_code 不存在
        (3, 4, "DR006"),
    ]),
]

def main():
    # 1) 先连到 MySQL(不指定库),建库
    conn = pymysql.connect(
        host=DB_CONFIG["host"], port=DB_CONFIG["port"],
        user=DB_CONFIG["user"], password=DB_CONFIG["password"],
        charset=DB_CONFIG["charset"],
    )
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} DEFAULT CHARACTER SET utf8mb4")
    cur.execute(f"USE {DB_CONFIG['database']}")
    print(f"[1/3] 数据库 {DB_CONFIG['database']} 就绪")

    # 2) 清空旧表,建新表(可重复运行)
    for table in reversed(list(CREATE_TABLES)):
        cur.execute(f"DROP TABLE IF EXISTS {table}")
    for table, sql in CREATE_TABLES.items():
        cur.execute(sql)
    print("[2/3] 6 张表已创建:", ", ".join(CREATE_TABLES))

    # 3) 插入数据
    total = 0
    for table, cols, rows in DATA:
        placeholders = ", ".join(["%s"] * len(cols))
        sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
        cur.executemany(sql, rows)
        total += len(rows)
        print(f"      {table}: {len(rows)} 行")

    conn.commit()
    print(f"[3/3] 共插入 {total} 行(其中脏数据 15 条)")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
