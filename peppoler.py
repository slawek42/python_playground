import requests
import json
import argparse
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from os import path
import sys

"""
The aim of this tool is to check if a given recipient is registered in Peppol database by utilizing public API.
The request contains general query item  'q' in order to increase the chance of finding a match.
The tool can either get the individual input from string -i 0192:123456 or a file that contains more than 1 entry.
"""


parser = argparse.ArgumentParser(description="Client for Peppol API")
parser.add_argument('-i','--inputis', help='Individual identifier')
args = parser.parse_args()


BIS3 = "urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1"
URL = "https://directory.peppol.eu/search/1.0/json"


class Peppols:

    def __init__(self):
        self.outs = {}
        self.inputs = []

    def list_distinc(self,inputs):
        if path.isfile(inputs):
            with open(inputs, 'r') as f:
                print(type(f))
                try:
                    self.inputs = list(set([x.split("=")[1].rstrip() for x in f]))
                    print(len(self.inputs))
                except Exception as e:
                    self.inputs = list(set(f))
                    print(self.inputs)
        else:
            print(type(inputs))
            self.inputs.append(inputs)


    def requestor(self,api,peppol_id):
        try:
            retries = Retry(total=10,backoff_factor=1,status_forcelist=[400,429,500])
            adapter = HTTPAdapter(max_retries=retries)
            http = requests.Session()
            http.mount("https://", adapter)
            parames = {'q':peppol_id}
            r = http.get(url = api, params = parames)
            #print(r.status_code)
            data = r.json()
            return data
        except KeyboardInterrupt:
            sys.exit(1)


    def jsonser(self):
        for id in self.inputs:
            resp = self.requestor(URL, id)
            for k,v in resp.items():
                if k == 'matches' and isinstance(v,list):
                    for e in v:
                        participantID = e.get('participantID').get('value')
                        self.outs[id] = {'participantID': participantID}
                        for elem in e.get('docTypes'):
                            if BIS3 in elem.get('value'):
                                self.outs[id].update({'BIS3' : 'Yes'})
                            else:
                                self.outs[id] = {'BIS3' : 'No'}

                            self.outs[id].update({'query_item' : id})
                else:
                    self.outs[id] = {   'participantID' : id,
                                        'BIS3' : 'Missing from database'
                                    }
                

def main():
    peps = Peppols()
    peps.list_distinc(args.inputis)
    peps.jsonser()
    print(json.dumps(peps.outs, indent=4))

if __name__ == "__main__":
        main()