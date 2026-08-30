# -*- coding: utf-8 -*-
"""
runner_demo.py - 定时巡检 + 邮件告警（演示版，可安全公开）

与 runner.py 功能一致，但邮箱授权码不写死在代码里，
而是从环境变量读取，避免敏感信息泄露。

用法（Windows PowerShell）：
    $env:SMTP_SENDER = "你的邮箱@qq.com"
    $env:SMTP_AUTH_CODE = "你的16位授权码"
    $env:SMTP_RECEIVER = "收件人邮箱@qq.com"
    .venv\Scripts\python.exe runner_demo.py
"""
import os
import schedule
import time
from datetime import datetime
from app import run_inspection, build_html


def get_env(name):
    val = os.environ.get(name)
    if not val:
        print(f"[错误] 缺少环境变量 {name}，请先设置，例如：")
        print(f'  PowerShell: $env:{name} = "你的值"')
        raise SystemExit(1)
    return val


def send_mail(subject, html_body):
    import smtplib
    from email.mime.text import MIMEText
    sender = get_env("SMTP_SENDER")
    auth_code = get_env("SMTP_AUTH_CODE")
    receiver = get_env("SMTP_RECEIVER")

    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    server = smtplib.SMTP_SSL("smtp.qq.com", 465)
    server.login(sender, auth_code)
    server.sendmail(sender, [receiver], msg.as_string())
    server.quit()
    print("邮件已发送")


def build_mail_html(results):
    html = "<h2>HIS 巡检告警</h2>"
    for r in results:
        if len(r["rows"]) > 0:
            html += f"<h3>{r['name']}（命中 {len(r['rows'])} 条）</h3>"
            html += "<table border='1'>"
            html += "<tr>"
            for col in r["cols"]:
                html += f"<th>{col}</th>"
            html += "</tr>"
            for row in r["rows"]:
                html += "<tr>"
                for cell in row:
                    html += f"<td>{cell}</td>"
                html += "</tr>"
            html += "</table>"
    return html


def read_last_bad():
    try:
        with open("last_bad.txt", "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None


def write_last_bad(bad):
    with open("last_bad.txt", "w", encoding="utf-8") as f:
        f.write(str(bad))


def job():
    print(f"[{datetime.now()}]开始巡检...")
    results = run_inspection()
    bad = sum(len(r["rows"]) for r in results)

    with open("report.txt", "w", encoding="utf-8") as f:
        f.write("HIS 巡检报告\n")
        for r in results:
            f.write(f"[{r['name']}] 命中{len(r['rows'])}条\n")
            for row in r["rows"]:
                f.write("  " + str(row) + "\n")
    with open("report.html", "w", encoding="utf-8") as f:
        f.write(build_html(results))
    print(f"巡检完成，当前脏数据 {bad} 条")

    # 状态变化才发邮件：异常告警、恢复通知、无变化不打扰
    last_bad = read_last_bad()
    if bad == last_bad:
        print(f"状态没变（{bad} 条），不重复发邮件")
        return
    if bad > 0:
        send_mail("HIS巡检告警", build_mail_html(results))
    else:
        send_mail("HIS巡检恢复正常", "数据已全部恢复干净")
    write_last_bad(bad)


if __name__ == "__main__":
    schedule.every(1).minutes.do(job)
    print("定时巡检已启动（演示版）：每 1 分钟跑一次，按 Ctrl+C 停止")
    while True:
        schedule.run_pending()
        time.sleep(1)
