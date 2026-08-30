# HIS 数据巡检工具

基于 Python 的医院信息系统（HIS）数据质量巡检工具。自动扫描 MySQL 数据库中的脏数据（编码重复、字段为空、价格异常、外键引用失效、身份证格式错误），生成可视化报告，并支持网页实时查看、定时自动巡检和邮件告警。

## 功能特性

- 14 条巡检规则，覆盖 6 张核心业务表（药品 / 科室 / 收费项目 / 医嘱 / 患者 / 医生）
- 检测类型：编码重复、字段为空、价格 <= 0、外键引用失效（孤儿数据）、身份证格式校验
- 生成文本报告（report.txt）与可视化 HTML 报告（report.html）
- Flask 网页实时展示巡检结果
- schedule 定时自动巡检
- 发现脏数据自动发送邮件通知（SMTP）

## 技术栈

- Python 3
- PyMySQL（数据库连接）
- Flask（网页展示）
- schedule（定时任务）
- smtplib / email（邮件通知）
- MySQL 8

## 项目结构

| 文件 | 作用 |
| --- | --- |
| init_db.py | 建库建表，插入演示用的脏数据 |
| config.py | 数据库连接配置 |
| app.py | 14 条巡检规则 + Flask 网页版 |
| runner.py | 定时巡检 + 邮件通知 |
| inspector_v2.py | 命令行版巡检（生成 txt / html 报告） |
| report.txt / report.html | 生成的巡检报告 |

## 快速开始

```bash
# 1. 安装依赖（虚拟环境）
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# 2. 建库建表 + 插入演示脏数据
.venv\Scripts\python.exe init_db.py

# 3. 命令行巡检，生成 report.txt / report.html
.venv\Scripts\python.exe inspector_v2.py

# 4. 网页查看
.venv\Scripts\python.exe app.py
# 浏览器打开 http://127.0.0.1:5000

# 5. 定时巡检 + 邮件通知（需在 runner.py 配置自己的邮箱）
.venv\Scripts\python.exe runner.py
```

## 规则清单

| 表 | 规则 |
| --- | --- |
| drug | 药品编码重复 / 名称为空 / 规格为空 / 价格 <= 0 |
| department | 科室编码重复 / 上级科室不存在 |
| charge_item | 项目编码重复 / 项目价格 <= 0 |
| medical_order | 患者不存在 / 医生不存在 / 药品不存在 |
| patient | 身份证重复 / 身份证格式不对 |
| doctor | 所属科室不存在 |

## 核心实现思路

- 规则以「列表 + 字典」组织，每条规则包含规则名、表头列名、检测 SQL
- 重复检测：GROUP BY ... HAVING COUNT(*) > 1
- 孤儿检测：LEFT JOIN ... WHERE 右表主键 IS NULL
- 格式校验：NOT REGEXP
- 巡检引擎：循环执行规则 -> 汇总结果 -> 渲染 HTML -> （可选）邮件告警

## 截图

（可在此处放网页报告截图）
