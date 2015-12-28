# -*- coding: utf-8 -*-

import smtplib
import os
import ConfigParser
from email.mime.text import MIMEText

class mail:

    cf = None
    server = None
    instance = None
    configFile = ''

    def __init__(self, file=''):
        if file == '' or False == os.path.exists(file):
            self.configFile = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+'/config.ini'
        else:
            self.configFile = file

        self.connect()

    def connect(self):
        if self.server is not None:
            return self.server

        self.server = smtplib.SMTP_SSL(self.getConfig('host'), int(self.getConfig('port')))
        #self.server.set_debuglevel(1)
        self.server.login(self.getConfig('user'), self.getConfig('pass'))
        return self.server

    def getConfig(self, key):
        if self.cf is None:
            self.cf = ConfigParser.ConfigParser()
            self.cf.read(self.configFile)

        return self.cf.get('email', key)

    def send(self,  content=' ', subject='Python邮件中心', emails=[]):
        if len(emails) == 0:
            emails = self.getConfig('toemails').split(',')
        msg = MIMEText(content)
        msg['Subject'] = subject
        msg['To'] = ','.join(emails)
        msg['From'] = 'SERVER'

        return self.server.sendmail(self.getConfig('user'), emails, msg.as_string())

    def close(self):
        return self.server.quit()

    @staticmethod
    def sendMail(msg, subject='Python邮件中心', emails=[]):
        m = mail()
        m.send(msg, subject, emails)
        m.close()

#############################
#mail.sendMail('sfsfs')
#############################
