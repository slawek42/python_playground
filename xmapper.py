import os
import subprocess
import re
import json
import sys
import shutil
import smtplib
from email.message import EmailMessage
from datetime import datetime



class Reporter:

        def __init__(self):
                self.inpz = []
                self.outs = {}
                self.ebody = ""
                self.ediras = ['003712345678',
                               '003712345678',
                               '003712345689']

        def white_spacer(self,inps):
            for line in inps.splitlines():
                new_line = re.sub('\s+', ' ', line).split()
                self.inpz.append(new_line)


        def nested_diff(self,obj1):
            with open (obj1, "r") as ins:
                    data = json.load(ins)
                    data2 = self.outs
                    for k,v in data.items():
                            for k1, v1 in data2.items():
                                    if k == k1:
                                            for elem, elem2 in v.items():
                                                    for elem3, elem4 in v1.items():
                                                            if elem == elem3:
                                                                    if elem2 != elem4:
                                                                            #print("The following element {} has changed from {} to {}".format(elem,elem2, elem4))
                                                                            self.ebody += "ReceivingId {} - the {} in iaddress has changed from {} to {}\n".format(k, elem, elem2, elem4)


        def eivc_json(self):
                for edira in self.ediras:
                                p = subprocess.run(["eivc-site-info", edira], universal_newlines=True, capture_output=True)
                                self.white_spacer(p.stdout)
                                comp_name=""
                                eaddr=""
                                lmc=""
                                for line in self.inpz:
                                        if 'Name:' in line:
                                                comp_name = " ".join(line[1:])
                                        if "prod" in line and "!" not in line:
                                                eaddr = line[3]
                                                lmc = line[2]
                                                self.outs[edira] = {
                                                                'name' : comp_name ,
                                                                'lmc' : lmc ,
                                                                'eaddr' : eaddr
                                                                                }



        def send_mail(self,body_for_email):
                msg = EmailMessage()
                msg.set_content(body_for_email)
                #msg.add_attachment(json.dumps(self.outs, indent=4),filename='js')
                msg['Subject'] = 'Changes in iaddress'
                msg['From'] = 'slawomir.ciszewski@posti.com'
                msg['To'] = 'slawomir.ciszewski@posti.com'
                s = smtplib.SMTP('localhost')
                print(msg)
                s.send_message(msg)
                s.quit()



def main():
        stary = "LOLER"
        if os.path.isfile(stary):
                rep = Reporter()
                new_json = rep.eivc_json()
                rep.nested_diff(stary)
                if rep.outs:
                        rep.send_mail(rep.ebody)
                        orig = '{}.orig.{}'.format(stary, datetime.now().strftime('%Y%m%d%H'))
                        shutil.copyfile(stary, orig)
                        #make na orig and mv the new json file over the old one - use date+time convention
        else:
                sys.exit(1)


if __name__ == "__main__":
        main()
