#!/usr/bin/python
#coding: utf8
# Documentation at https://github.com/monperrus/halccli.py
#
# Example (on preprod): 
# $ python halccli.py --id hal-01462980 --tei
# $ python halccli.py --id hal-01462980 --set_comment foo2

from lxml import etree,objectify
import feedgenerator
import urllib2
import os
import inspect
import cgi
import getpass
import re
import requests
import json
import random
import string
import sys
import codecs
from docopt import docopt


class TEIHalEntry:
    """
       represents a remote HAL entry
    Example:
      t = TEIHalEntry("hal-01037383")
      print t.get_title()
      t.set_title("foo bar")
      print t.put()

    """
    
    # where to GET the entries (using the /"tei" url suffix), this is the Cont-IRI of te SWORD specification
    server_get='https://hal-preprod.archives-ouvertes.fr/'
    
    # where to PUT changes
    server_put='https://api-preprod.archives-ouvertes.fr/sword/'
    
    # where to post new data
    server_post='https://api-preprod.archives-ouvertes.fr/sword/hal/'

    # HAL login data that are sent using HTTP Basic authentification
    server_user = "test_ws"
    server_password = "test"

    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

    def __init__(self):
        pass
    
    def load(self,hal_id):
        """ creates a TEIHalEntry object from it hal_id (a string, eg "hal-01037383")"""
        self.hal_id=hal_id
        self.tei_url=self.server_get+hal_id+"/tei"
        self.reload();

    def reload(self):
        """ creates a TEIHalEntry object from it hal_id (a string, eg "hal-01037383")"""
        doc = requests.get(self.tei_url).text
        doc=doc.encode('utf-8')
        self.tei = etree.XML(doc)

    def get_title(self):
        return self.tei.xpath('.//tei:analytic/tei:title', namespaces=self.ns)[0].text
    def set_title(self, title):
        #self.tei.xpath('.//tei:titleStmt/tei:title', namespaces=self.ns)[0].text = title
        self.tei.xpath('.//tei:analytic/tei:title', namespaces=self.ns)[0].text = title

    def get_pages(self):
        return self.tei.xpath(".//tei:monogr/tei:imprint/tei:biblScope[@unit='pp']", namespaces=self.ns)[0].text
    def set_pages(self, pages):
        imprint = self.tei.xpath(".//tei:monogr/tei:imprint", namespaces=self.ns)[0]
        pp=imprint.xpath("./tei:biblScope[@unit='pp']", namespaces=self.ns)
        if len(pp)>0:
            pp[0].text = pages
        else:
            pp=etree.Element('biblScope',attrib={'unit':'pp'})
            pp.text=pages
            date=imprint.xpath("./tei:date", namespaces=self.ns)
            if len(date)>0: date[0].addprevious(pp)
            else: imprint.append(pp)
        pass
    
    def get_volume(self):
        return self.tei.xpath(".//tei:monogr/tei:imprint/tei:biblScope[@unit='volume']", namespaces=self.ns)[0].text
    def set_volume(self, newvolume):
        imprint = self.tei.xpath(".//tei:monogr/tei:imprint", namespaces=self.ns)[0]
        volume=imprint.xpath("./tei:biblScope[@unit='volume']", namespaces=self.ns)
        if len(volume)>0:
            volume[0].text = newvolume
            pass
        else:
            volume=etree.Element('biblScope',attrib={'unit':'volume'})
            volume.text=newvolume
            pp=imprint.xpath("./tei:biblScope[@unit='pp']", namespaces=self.ns)
            if len(pp)>0: pp[0].addprevious(volume)
            else: imprint.append(volume)
        pass
        
    def get_license(self):
        return self.tei.xpath('.//tei:availability/tei:licence', namespaces=self.ns)[0].attrib['target']
    def get_license_text(self):
        return self.tei.xpath('.//tei:availability/tei:licence', namespaces=self.ns)[0].text

    def get_institution(self):
        return self.tei.xpath(".//tei:monogr/tei:authority[@type='institution']", namespaces=self.ns)[0].text
    def set_institution(self, newinstitution):
        parent=self.tei.xpath(".//tei:monogr", namespaces=self.ns)[0]
        institution=parent.xpath("./tei:authority[@type='institution']", namespaces=self.ns)
        if len(institution)>0:
            institution[0].text = newinstitution
            pass
        else:
            institution=etree.Element('authority',attrib={'type':'institution'})
            institution.text=newinstitution
            parent.append(institution)
        pass
    
    # <idno type="reportNumber">hal-01144026</idno>
    def get_number(self):
        return self.tei.xpath(".//tei:monogr/tei:idno[@type='reportNumber']", namespaces=self.ns)[0].text
    def set_number(self, newnumber):
        parent=self.tei.xpath(".//tei:monogr", namespaces=self.ns)[0]
        number=parent.xpath("./tei:idno[@type='reportNumber']", namespaces=self.ns)
        if len(number)>0:
            number[0].text = newnumber
            pass
        else:
            number=etree.Element('idno',attrib={'type':'reportNumber'})
            number.text=newnumber
            # number comes as first child in monogr according to aofr-sword schema
            parent.insert(0,number)
        pass
    
    def get_doi(self):
        return self.tei.xpath(".//tei:idno[@type='doi']", namespaces=self.ns)[0].text
    def set_doi(self, newdoi):
    #<idno type="doi">10.1145/2430536.2430541</idno></biblStruct></sourceDesc>
        biblStruct = self.tei.xpath(".//tei:biblStruct", namespaces=self.ns)[0]
        doi=biblStruct.xpath("./tei:idno[@type='doi']", namespaces=self.ns)
        if len(doi)>0:
            doi[0].text = newdoi
        else:
            doi=etree.Element('idno', attrib={'type':'doi'})
            doi.text=newdoi
            ref=biblStruct.xpath("./tei:ref", namespaces=self.ns)
            if len(ref)>0: ref[0].addprevious(doi)
            else: biblStruct.append(doi)
        pass

    def get_comment(self):
        return self.tei.xpath(".//tei:notesStmt/tei:note[@type='commentary']", namespaces=self.ns)[0].text
    def set_comment(self, newcomment):
        biblStruct = self.tei.xpath(".//tei:notesStmt", namespaces=self.ns)[0]
        comments=biblStruct.xpath("./tei:note[@type='commentary']", namespaces=self.ns)
        if len(comments)>0:
            comments[0].text = newcomment
            pass
        else:
            comment=etree.Element('note', attrib={'type':'commentary'})
            comment.text=newcomment
            biblStruct.append(comment)
        pass

    def is_proceedings(self):
        note = self.tei.xpath(".//tei:notesStmt/tei:note[@type='proceedings']", namespaces=self.ns)
        return len(note)>0 and note[0].text == "Yes"

    def add_missing_elements(self):
        
        # conference proceedings must have a "city"
        if self.is_proceedings():
            meeting = self.tei.xpath(".//tei:monogr/tei:meeting", namespaces=self.ns)[0]
            settlement=meeting.xpath("./tei:settlement", namespaces=self.ns)
            if len(settlement) == 0:
                settlement=etree.Element('settlement')
                settlement.text="und"
                meeting.xpath("./tei:date", namespaces=self.ns)[-1].addnext(settlement)
            
    def post(self):
        """ sends a new element to the server using the SWORD protocol 
        curl -X POST -d @art.xml -v -u test_ws:test https://api.archives-ouvertes.fr/sword/hal/ -H "Packaging:http://purl.org/net/sword-types/AOfr" -H "Content-Type:text/xml"
        """
        self.add_missing_elements()
        #print self.to_string()
        #return
        if self.server_password == '-': self.server_password = getpass.getpass('password: ')
        r = requests.post(self.server_post, auth=(self.server_user, self.server_password), data=etree.tostring(self.tei) , headers = {"Packaging": "http://purl.org/net/sword-types/AOfr", "Content-Type":"text/xml"}
#                          , proxies = { "http": "localhost:8080"} # with mitm
        ) 
        if r.status_code != 202: raise Exception("POST failed: "+r.text)
        return r

    def put(self):
        """ sends changes to the server using the SWORD protocol """
        self.add_missing_elements()
        #print self.to_string()
        #return
        if self.server_password == '-': self.server_password = getpass.getpass('password: ')
        r = requests.put(self.server_put+self.hal_id, auth=(self.server_user, self.server_password), data=etree.tostring(self.tei) , headers = {"X-Packaging": "http://purl.org/net/sword-types/AOfr", "Content-Type":"text/xml"}) # debug , proxies = { "http": "localhost:8080"} 
        if r.status_code != 200: raise Exception("PUT failed: "+r.text)
        return r
    
    def to_string(self):
        return etree.tostring(self.tei)

def cli(argv):
    arguments = docopt(open(os.path.join(os.path.dirname(__file__),'README.txt')).read(), argv=argv)
    #print arguments
    setter=[]
    getter=[]
    for k,v in arguments.items():
        if k.startswith("--set_") and arguments[k]: setter.append(k)
    for k,v in arguments.items():
        if k.startswith("--get_") and arguments[k]: getter.append(k)

    if arguments['--prod']:
        TEIHalEntry.server_get='https://hal.archives-ouvertes.fr/'    
        TEIHalEntry.server_put='https://api.archives-ouvertes.fr/sword/'

    TEIHalEntry.server_user = arguments['--user']
    TEIHalEntry.server_password = arguments['--pass']
    
    if len(getter)>0:
        t = TEIHalEntry()
        t.load(arguments['--id'])
        res={}
        for m in getter:
            #print m
            res[m[6:]]=getattr(t,m[2:])()
        return res

    if len(setter)>0:
        t = TEIHalEntry()
        t.load(arguments['--id'])
        for m in setter:
            #print m[2:],arguments[m]
            getattr(t,m[2:])(arguments[m])
        t.put()
        return "success"
    
    if arguments['--tei']:
        t = TEIHalEntry()
        t.load(arguments['--id'])
        return t.to_string()
  
def cli_pp(argv):
    r = cli(argv)
    if type(r) == str: return r
    return json.dumps(r,indent=2)

if __name__ == '__main__':
    if sys.argv[1] == "--test":
       test()
       sys.exit()       
    print cli_pp(sys.argv[1:]) 




