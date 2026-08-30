import schedule
import time
from datetime import datetime
from app import RULES ,run_inspection,build_html
import smtplib
from email.mime.text import MIMEText
def send_email(subject,body):
    sender = "2700129591@qq.com"
    auth_code ="zboijgtafqrpdgdd"
    receiver = "2700129591@qq.com"
    msg = MIMEText(body,"plain","utf-8")
    msg["Subject"]=subject
    msg["From"]=sender
    msg["To"]=receiver
    server=smtplib.SMTP_SSL("smtp.qq.com",465)
    server.login(sender,auth_code)
    server.sendmail(sender,[receiver],msg.as_string())
    server.quit()
    print("邮件已发送")
def job():
    print(f"[{datetime.now()}]开始巡检...")
    results = run_inspection()
    with open ("report.txt","w",encoding="utf-8") as f:
        f.write("HIS 巡检报告\n")
        for r in results:
            f.write(f"[{r['name']}]命中{len(r['rows'])}条\n")
            for r in r["rows"]:
                f.write("  " + str(row) + "\n")
    with open ("report.html", "w", encoding="utf-8") as f:
        f.write(build_html(results))
        print("巡检完成，报告已更新")
send_email("HIS巡检测试", "这是一封测试邮件，邮件功能正常！")
schedule.every(1).minutes.do(job)
print("定时巡检已启动：每 1 分钟跑一次，按 Ctrl+C 停止")
while True:
    schedule.run_pending()
    time.sleep(1)

