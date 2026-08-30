import schedule
import time
from datetime import datetime
from app import RULES, run_inspection, build_html
import smtplib
from email.mime.text import MIMEText

def send_email(subject, body):
    sender = "2700129591@qq.com"
    auth_code = "zboijgtafqrpdgdd"
    receiver = "2700129591@qq.com"
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver
    server = smtplib.SMTP_SSL("smtp.qq.com", 465)
    server.login(sender, auth_code)
    server.sendmail(sender, [receiver], msg.as_string())
    server.quit()
    print("邮件已发送")

def read_last_bad():
    """读上次的脏数据条数；没有记录返回 None"""
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

    # 统计这次一共命中多少条脏数据
    bad = 0
    for r in results:
        bad += len(r["rows"])

    # 更新报告文件
    with open("report.txt", "w", encoding="utf-8") as f:
        f.write("HIS 巡检报告")
        for r in results:
            f.write(f"[{r['name']}] 命中{len(r['rows'])}条")
            for row in r["rows"]:
                f.write("  " + str(row) + "")
    with open("report.html", "w", encoding="utf-8") as f:
        f.write(build_html(results))
    print(f"巡检完成，当前脏数据 {bad} 条")

    # 方案一：数量变了才发邮件
    last_bad = read_last_bad()
    if bad == last_bad:
        print(f"数量没变（{bad} 条），不重复发邮件")
        return

    if bad > 0:
        send_email("HIS巡检告警", f"发现 {bad} 条脏数据（上次记录 {last_bad} 条），请查看 report.html")
    else:
        send_email("HIS巡检恢复正常", "脏数据已全部清理干净！")
    write_last_bad(bad)

schedule.every(1).minutes.do(job)
print("定时巡检已启动：每 1 分钟跑一次，按 Ctrl+C 停止")
while True:
    schedule.run_pending()
    time.sleep(1)
