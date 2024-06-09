# Answer-Detected
一个可以自动检测USB中答案的Windows服务。每隔5秒钟检测是否有USB设备插入，每隔35分钟自动将带有“答案”“参考”字样的文件发送至指定邮箱。
## 使用教程
1.将answer_detected.py下载到一个指定的目录（最好单独存放在一个文件夹）  
2.右键以记事本打开，修改如下三行：  
lf.email_address = '你的QQ邮箱地址'   
        self.email_password = '你的QQ邮箱授权码'    
        self.to_email = '你想要发送的邮箱'
将你自己的信息分别替换，QQ邮箱授权码的获得可以参考https://jingyan.baidu.com/article/ac6a9a5eb439f36b653eacc0.html  
3.打开一个管理员命令提示符！注意是管理员！然后cd到你存放这个文件的目录，输入：python answer_detected.py install  
4.提示安装完成，然后在输入：python answer_detected.py start  
5.Enjoy!
