#!/usr/env/bin python3
'''
bibget.py

Gets bibtex formatted citation data from pdf

Usage:
  bibget.py <doc>
'''

from docopt import docopt
import requests
from bs4 import BeautifulSoup
import re
import io

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage


def convertPDFToText(path):
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=0, password='', caching=True, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text


def getBibStr(data : dict):

    datekeys = [
        'date',
        'publication_date'
    ]
    
    
    # assumes article right now
    bibStr = "@article{"
    try:
        year = data['date'][:4]
    except KeyError:
        year = data['publication_date'][:4]
    key = data['author'][0].split(' ')[-1] + year
    bibStr += key
    bibStr += "\n\t"
    bibStr += "title = "
    bibStr += data['title']
    bibStr += ",\n\t"
    bibStr += "author = "
    if type(data['author']) is not list: data['author'] = [data['author']]
    for author in data['author']:
        bibStr += author + " and "
    bibStr = bibStr[:-5]
    bibStr += ",\n\t"
    bibStr += "year = " + year
    bibStr += ",\n\t"
    bibStr += "journal = " + data['journal_title']
    bibStr += ",\n\t"
    bibStr += "publisher = " + data['publisher']
    bibStr += ",\n\t"
    bibStr += "doi = " + data['doi']
    bibStr += "\n}"
    return bibStr
    

def getDOI(pdfPath : str):
    text = convertPDFToText(pdfPath)
    lines = text.split('\n')
    regex = re.compile(r"doi.org\/\d+\.\d+\/[\d\w]+")
    possible_dois = list()
    for line in lines:
        match = regex.search(line)
        if match != None: possible_dois.append(match.group())

    if len(possible_dois) == 0:
        raise Exception("No DOI found in PDF!")

    if len(possible_dois) == 1:
        return possible_dois[0]

    doi_check = dict()
    for doi in possible_dois:
        if doi not in doi_check.keys():
            doi_check[doi] = 1
        else:
            doi_check[doi] += 1

    if len(doi_check.keys()) == 1:
        return possible_dois[0]

    maxv = 0
    atk = ""
    for k, v in doi_check:
        if v > maxv:
            maxv = v
            atk = k
    return k

    
def getBibData(doi):
    r = requests.get("https://doi.org/"+doi)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(str(r.text), 'html.parser')
    metas = soup.find_all('meta')
    print(metas)
    bibdata = dict()
    for meta in metas:
        try:
            name = meta['name']
            if "citation" in name:
                k = name[9:]
                if k in bibdata.keys():
                    if type(bibdata[k]) is not list:
                        bibdata[k] = [bibdata[k]]
                    bibdata[k].append(meta['content'])
                else:
                    bibdata[k] = meta['content']
        except KeyError:
            pass
        
    return bibdata

        
if __name__ == "__main__":
    args = docopt(__doc__, version="1")
    pdfPath = args['<doc>']
    doi = getDOI(pdfPath)
    bibData = getBibData(doi)

    for k, v in bibData.items():
        print(k, v)
    #print(getBibStr(bibData))
