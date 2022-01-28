import xml.etree.ElementTree as ET
import re
import os
import csv
import json


class Xpather:


    def __init__(self):
        self.xml_root = None
        self.xplist = []


    def preprocessor(self, xml_file):
        #https://bugs.python.org/issue18304
        tree = ET.iterparse(xml_file)
        for _, el in tree:
            prefix, has_namespace, postfix = el.tag.rpartition('}')
            if has_namespace:
                el.tag = postfix
        self.xml_root = tree.root


    def recognizer(self,element,xpath):
        try:
            text = element.text.rstrip()
            if element.attrib:
                attribs = [f'{k}={v}' for k,v in element.attrib.items()]
                absolute = f'{xpath}@{attribs}={text}'
                self.xplist.append(absolute)
            elif text:
                absolute = f'{xpath}={text}'
                self.xplist.append(absolute)
            else:
                self.xplist.append(xpath)
        except AttributeError:
            self.xplist.append(xpath)


    def depther(self,el=None,path=None):
        if el is None and path is None:
            el = self.xml_root
            path = self.xml_root.tag
        numberer = {}
        for child in el:
            tag = child.tag
            parent_xpath = f'{path}/{tag}'
            self.recognizer(child,parent_xpath)
            if tag in numberer:
                numberer[tag] += 1
                num_tag = f'{tag}[{(numberer[tag])}]'
                parent_xpath = f'{path}/{num_tag}'
                self.depther(child,parent_xpath)
            else:
                numberer[tag] = 1
                self.depther(child, parent_xpath)


def cross_diff(diffdict):
    with open('differences2.csv', 'w', newline='') as csvfile:
        for k,v in diffdict.items():
            x = [p for p in v.values()]
            diff = sorted(set(x[0]).difference(x[1]))
            diff2 = sorted(set(x[1]).difference(x[0]))
            if diff or diff2:
                writer = csv.writer(csvfile, delimiter=';',dialect='excel')
                writer.writerow([k, "\n".join(diff) , "\n".join(diff2)])
            else:
                print(f'{k} will be skipped')

#def cross_diff(ebid,diffdict):
#    x = list(diffdict.keys())
#    diff = sorted(set(diffdict[x[0]]).difference(diffdict[x[1]]))
#    diff2 = sorted(set(diffdict[x[1]]).difference(diffdict[x[0]]))
#    with open('differences2.csv', 'w', newline='') as csvfile:
#        writer = csv.writer(csvfile, delimiter=';',dialect='excel')
#        writer.writerow([ebid, "\n".join(diff) , "\n".join(diff2)])

def main():
    p = re.compile('^(BEL.{32})\.(new|old)$')
    count = {}
    differences = {}
    for f in os.listdir():
        if p.match(f):
            ebid = str((p.match(f).group(1)))
            if ebid in count:
                #differences = {}
                count[ebid].append(f)
                for v in count[ebid]:
                    xPat = Xpather()
                    xPat.preprocessor(v)
                    xPat.depther()
                    #differences[v] = xPat.xplist
                    try:
                        differences[ebid].update({v : xPat.xplist})
                    except KeyError:
                        differences[ebid] = {v : xPat.xplist}
            else:
                count[ebid] = [f]
    #print(json.dumps(differences, indent=4))
    cross_diff(differences)


if __name__ == "__main__":
        main()



"""
def main():
    p = re.compile('^(BEL.{32})\.(new|old)$')
    count = {}
    differences = {}
    for f in os.listdir():
        if p.match(f):
            ebid = str((p.match(f).group(1)))
            if ebid in count:
                count[ebid].append(f)
                for v in count[ebid]:
                    xPat = Xpather()
                    xPat.preprocessor(v)
                    xPat.depther()
                    differences[ebid].update({v : xPat.xplist})
            else:
                count[ebid] = [f]
    cross_diff(ebid,differences)
"""
