import xml.etree.ElementTree as ET
import re
import os
import csv


class Xpather:

    def __init__(self):
        self.obj1 = []
        self.obj2 = []
        self.differences = ""
        self.first_run = True


    def recognizer(self,element,xpath,cont):
        try:
            text = element.text.rstrip()
            if element.attrib:
                attribs = [f'{k}={v}' for k,v in element.attrib.items()]
                absolute = f'{xpath}@{attribs}={text}'
                cont.append(absolute)
            elif text:
                absolute = f'{xpath}={text}'
                cont.append(absolute)
            else:
                cont.append(xpath)
        except AttributeError:
            cont.append(xpath)


    def depther(self,el,path):
        numberer = {}
        for child in el:
            tag = child.tag
            parent_xpath = f'{path}/{tag}'
            if self.first_run:
                self.recognizer(child,parent_xpath,self.obj1)
            else:
                self.recognizer(child,parent_xpath,self.obj2)
            if tag in numberer:
                numberer[tag] += 1
                num_tag = f'{tag}[{(numberer[tag])}]'
                parent_xpath = f'{path}/{num_tag}'
                self.depther(child,parent_xpath)
            else:
                numberer[tag] = 1
                self.depther(child, parent_xpath)


    def cross_diff(self,ebid):
        diff = set(self.obj1).difference(self.obj2)
        diff2 = set(self.obj2).difference(self.obj1)
        with open('differences.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';',dialect='excel')
            writer.writerow([ebid, "\n".join(diff) , "\n".join(diff2)])


def main():
    xPat = Xpather()
    p = re.compile('^(BEL.{32})\.(new|old)$')
    count = {}
    for f in os.listdir():
        if p.match(f):
            ebid = str((p.match(f).group(1)))
            if ebid in count:
                count[ebid].append(f)
                for v in count[ebid]:
                    tree = ET.parse(v)
                    root = tree.getroot()
                    xPat.depther(root,root.tag)
                    xPat.first_run = False
            else:
                count[ebid] = [f]
        xPat.cross_diff(ebid)


if __name__ == "__main__":
        main()
