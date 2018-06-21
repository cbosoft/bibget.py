import requests
from bs4 import BeautifulSoup

def getBibStr(data : dict):
    # assumes article right now
    bibStr = "@article{"
    year = data['date'][:4]
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
    

    
def getBibData(doi):
    r = requests.get("https://doi.org/"+doi)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(str(r.text), 'html.parser')
    metas = soup.find_all('meta')
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
    test_dois = [
        "10.1103/PhysRevLett.112.098302",
        "10.1103/PhysRevLett.75.2148"
    ]
    for doi in test_dois:
        bibData = getBibData(doi)

        #for k, v in bibData.items():
        #    print(k, v)

        print(getBibStr(bibData))
