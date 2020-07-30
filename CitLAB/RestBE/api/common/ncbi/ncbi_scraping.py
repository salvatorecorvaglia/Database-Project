from bs4 import BeautifulSoup
import requests
import re
from selenium import webdriver
import time
import textract
from django.conf import settings
import os

CHROMEPATH = os.path.abspath(os.path.dirname(__file__))+"/chrome_driver/chromedriver"
PANTHOMJSPATH = os.path.abspath(os.path.dirname(__file__))+"/phantomjs/bin/phantomjs"
DOWNLOADPATH = os.path.abspath(os.path.dirname(__file__))+"/PDF/"
PDF_FLAG = True
base = "https://www.ncbi.nlm.nih.gov"
base_api = "https://api.ncbi.nlm.nih.gov/lit/ctxp/v1/pmc/?format=citation&id="
base_url = "https://www.ncbi.nlm.nih.gov/pmc/?term="

def clear_text(text):
    return text.replace("\"", "'").replace("<b>", "").replace("</b>", "").replace("<span>", "").replace("</span>", "").replace("<sup>", "").replace("</sup>", "").replace("<em>", "").replace("</em>", "").rstrip()

def extract_title(doc_page, obj, cit=True):
    if doc_page.find("div", class_="title").find("a"):
        title = doc_page.find("div", class_="title").find("a").text
    else:
        title = doc_page.find("div", class_="title").text
    title = clear_text(title)
    obj["title"] = title
    return obj

def extract_pdf(doc_page, obj):
    a_links_pdf = doc_page.find("div", class_="links").find_all("a", href=True)
    for link_pdf in a_links_pdf:
        if "PDF" in link_pdf.text:
            obj["pdf"] = base + link_pdf['href']
            try:
                f = open(DOWNLOADPATH+link_pdf['href'].split("/")[-1:][0])
                f.close()
            except IOError:
                options = webdriver.ChromeOptions()
                profile = {
                    "download.default_directory": DOWNLOADPATH,
                    "plugins.always_open_pdf_externally": True
                }

                options.add_experimental_option("prefs", profile)
                driver_pdf = webdriver.Chrome(
                    CHROMEPATH,
                    #'/Users/danilogiovannico/Desktop/PROGETTO\ DATABASE/CitLAB/RestBE/api/common/ncbi/chrome_driver/chromedriver',
                    chrome_options=options)  # Optional argument, if not specified will search path.

                driver_pdf.implicitly_wait(10)
                driver_pdf.maximize_window()
                driver_pdf.get(obj["pdf"])
                time.sleep(30)
                driver_pdf.quit()
            break
            #extract_pdf_author_from_pdf(obj["pdf"])
    return obj

def extract_references(doc_page,obj):
    array_references = []
    array_original_references = []
    try:
        if doc_page.find("div", id="reference-list").find_all("div", class_="ref-cit-blk half_rhythm"):
            if doc_page.find("div", id="reference-list").find_all("div", class_="ref-cit-blk half_rhythm")[0].find_all("span",class_="element-citation"):
                references_div = doc_page.find_all("span", class_="element-citation")
                for ref in references_div:
                    ref_obj = {
                        "authors": None,
                        "title": None
                    }
                    ref_original = re.sub(' +', ' ',ref.text.replace("\n", " ").replace("\"", "'").replace("[PMC free article]", "").replace("[PubMed]", "").replace("[CrossRef]","").replace("[Google Scholar]", ""))
                    ref_array = re.sub(' +', ' ',ref.text.replace("\n", " ").replace(".,",",").replace("\"", "'").replace("[PMC free article]", "").replace("[PubMed]", "").replace("[CrossRef]","").replace("[Google Scholar]", "")).split(".")
                    ref_array = [x.strip(' ') for x in ref_array]
                    ref_array = list(filter(None, ref_array))
                    index = None
                    for i,element in enumerate(ref_array,start=0):
                        if len(element) > 50:
                            break
                        if (re.search(" [A-Z]", element[-2:]) or len(element) == 1) and len(element) <= 100:
                            index = i
                    if index is not None:
                        if len('.'.join(ref_array[0:index+1])) < 150:
                            ref_obj["authors"] = '.'.join(ref_array[0:index+1])
                            ref_obj["title"] = '.'.join(ref_array[index+1:])
                        else:
                            ref_obj["title"] = '.'.join(ref_array[0:])
                    else:
                        if ref_array[0].count(',') < 2 and ref_array[0].count('.') < 2 and len(ref_array[0]) > 50:
                            ref_obj["title"] = '.'.join(ref_array[0:])
                        else:
                            ref_obj["authors"] = ref_array[0]
                            ref_obj["title"] = '.'.join(ref_array[1:])

                    if not ref_obj["title"]:
                        ref_obj["title"] = ref_obj["authors"]
                        ref_obj["authors"] = None
                    array_references.append(ref_obj)
                    array_original_references.append(ref_original)

        if doc_page.find("div", id="reference-list").find_all("div", class_="ref-cit-blk half_rhythm"):
            if doc_page.find("div", id="reference-list").find_all("div", class_="ref-cit-blk half_rhythm")[0].find_all("span",class_="mixed-citation"):
                references_div = doc_page.find_all("div", class_="ref-list-sec sec")[0].children
                for ref in references_div:
                    ref_obj = {
                        "authors": None,
                        "title": None
                    }
                    ref_original = re.sub(' +', ' ',ref.text.replace("\n", " ").replace("\"", "'").replace("[PMC free article]", "").replace("[PubMed]", "").replace("[CrossRef]","").replace("[Google Scholar]", ""))
                    ref_array = re.sub(' +', ' ',ref.find("span", class_="mixed-citation").text.replace("\n", " ").replace(".,",",").replace("\"", "'").replace(" . ","").replace("[PMC free article]", "").replace("[PubMed]", "").replace("[CrossRef]","").replace("[Google Scholar]", "")).split(".")
                    ref_array = [x.strip(' ') for x in ref_array]
                    ref_array = list(filter(None, ref_array))
                    index = None
                    for i, element in enumerate(ref_array, start=0):
                        if len(element) > 50:
                            break
                        if (re.search(" [A-Z]", element[-2:]) or len(element) == 1) and len(element) <= 100:
                            index = i
                    if index is not None:
                        if len('.'.join(ref_array[0:index+1])) < 150:
                            ref_obj["authors"] = '.'.join(ref_array[0:index+1])
                            ref_obj["title"] = '.'.join(ref_array[index+1:])
                        else:
                            ref_obj["title"] = '.'.join(ref_array[0:])
                    else:
                        if ref_array[0].count(',') < 2 and ref_array[0].count('.') < 2 and len(ref_array[0]) > 50:
                            ref_obj["title"] = '.'.join(ref_array[0:])
                        else:
                            ref_obj["authors"] = ref_array[0]
                            ref_obj["title"] = '.'.join(ref_array[1:])

                    if not ref_obj["title"]:
                        ref_obj["title"] = ref_obj["authors"]
                        ref_obj["authors"] = None
                    array_references.append(ref_obj)
                    array_original_references.append(ref_original)

        if doc_page.find("div", id="reference-list").find_all("li"):
            references_div = doc_page.find_all("span", class_="element-citation")
            for ref in references_div:
                ref_obj = {
                    "authors": None,
                    "title": None
                }
                ref_original = re.sub(' +', ' ',ref.text.replace("\n", " ").replace("\"", "'").replace("[PMC free article]","").replace("[PubMed]","").replace("[CrossRef]", "").replace("[Google Scholar]", ""))
                ref_array = re.sub(' +', ' ',ref.text.replace("\n", " ").replace(".,",",").replace("\"", "'").replace(" . ", "").replace("[PMC free article]","").replace("[PubMed]","").replace("[CrossRef]", "").replace("[Google Scholar]", "")).split(".")
                index = None
                for i, element in enumerate(ref_array, start=0):
                    if len(element) > 50:
                        break
                    if (re.search(" [A-Z]", element[-2:]) or len(element) == 1) and len(element) <= 100:
                        index = i
                if index is not None:
                    if len('.'.join(ref_array[0:index + 1])) < 150:
                        ref_obj["authors"] = '.'.join(ref_array[0:index + 1])
                        ref_obj["title"] = '.'.join(ref_array[index + 1:])
                    else:
                        ref_obj["title"] = '.'.join(ref_array[0:])
                else:
                    if ref_array[0].count(',') < 2 and ref_array[0].count('.') < 2 and len(ref_array[0]) > 50:
                        ref_obj["title"] = '.'.join(ref_array[0:])
                    else:
                        ref_obj["authors"] = ref_array[0]
                        ref_obj["title"] = '.'.join(ref_array[1:])

                if not ref_obj["title"]:
                    ref_obj["title"] = ref_obj["authors"]
                    ref_obj["authors"] = None

                array_references.append(ref_obj)
                array_original_references.append(ref_original)
    except Exception as e:
        #print("Errore {}".format(obj['title']))
        pass
    return array_references, array_original_references


def extract_abstract(obj):
    html_content_doc = requests.get(obj["url"]).text
    soup_doc = BeautifulSoup(html_content_doc, "lxml")
    try:
        pdoc = soup_doc.find_all("p", class_="p p-first-last")
        if len(pdoc) == 0:
            #driver = webdriver.PhantomJS(executable_path="/Users/danilogiovannico/Desktop/PROGETTO\ DATABASE/CitLAB/RestBE/api/common/ncbi/phantomjs/bin/phantomjs")
            driver = webdriver.PhantomJS(executable_path=PANTHOMJSPATH)
            driver.get(obj["url"])
            p_element = driver.find_element_by_class_name('p-first-last')
            obj["abstract"] = clear_text(p_element.text)
            driver.quit()
        else:
            for j, p in enumerate(pdoc, start=0):
                if j == 0:
                    obj["abstract"] = clear_text(p.text)
                    break
    except Exception as e:
        #print("Errore {}".format(obj['title']))
        pass
    obj["references"], obj["original_references"] = extract_references(soup_doc,obj)
    return obj

def extract_authors(doc_page, obj):
    authorsdiv = doc_page.find_all("div", class_="supp")
    for i, line in enumerate(authorsdiv, start=0):
        for k, core in enumerate(line.children, start=0):
            if k == 0:
                obj["authors"] = core.text
            if k == 1:
                spans = core.find_all('span')
                obj["publishing_company"] = core.get_text().split(".")[0]
                if len(spans) == 2:
                    for count, span in enumerate(spans, start=0):
                        if count == 0:
                            d = re.findall('(\d{4})', span.text)
                            obj["year"] = d[0]
                        if count == 1:
                            if "Published online" in span.text:
                                obj["publication_date"] = span.text.rstrip()
                            if "doi" in span.text:
                                obj["doi"] = span.text.split(":")[1].rstrip()
                if len(spans) == 3:
                    for count, span in enumerate(spans, start=0):
                        if count == 0:
                            d = re.findall('(\d{4})', span.text)
                            obj["year"] = d[0]
                        if count == 1:
                            if "Published online" in span.text:
                                obj["publication_date"] = span.text.rstrip()
                            if "doi" in span.text:
                                obj["doi"] = span.text.split(":")[1].rstrip()
                        if count == 2:
                            if "Published online" in span.text:
                                obj["publication_date"] = span.text.rstrip()
                            if "doi" in span.text:
                                obj["doi"] = span.text.split(":")[1].rstrip()
                if len(spans) == 4:
                    for count, span in enumerate(spans, start=0):
                        if count == 0:
                            d = re.findall('(\d{4})', span.text)
                            obj["year"] = d[0]
                        if count == 1:
                            if "Published online" in span.text:
                                obj["publication_date"] = span.text.rstrip()
                            if "doi" in span.text:
                                obj["doi"] = span.text.split(":")[1].rstrip()
                        if count == 2:
                            if "Published online" in span.text:
                                obj["publication_date"] = span.text.rstrip()
                            if "doi" in span.text:
                                obj["doi"] = span.text.split(":")[1].rstrip()
                        if count == 3:
                            if "Published online" in span.text:
                                obj["publication_date"] = span.text.rstrip()
                            if "doi" in span.text:
                                obj["doi"] = span.text.split(":")[1].rstrip()
        obj = extract_abstract(obj)
    return obj

def extract_text_from_pdf(obj):
    try:
        text = textract.process(DOWNLOADPATH+obj['pdf'].split("/")[-1:][0]).decode("utf-8")
        obj["pdf_text"] = text.replace("\"","'").replace("{","[").replace("}","]")
    except Exception as e:
        pass
    return obj

def mentioned_in(obj):
    array_citation = []
    #print(el["title"].lstrip().split(".")[0])
    html_content = requests.get(obj["url"]+'citedby').text
    soup = BeautifulSoup(html_content, "lxml")

    separator = ', '
    link_array = []
    divs = soup.find_all("div", class_="rprt")
    for row in divs:
        obj_cit = {
            "title": None,
            "abstract": None,
            "url": base + row.find("a").get("href"),
            "authors": None,
            "year": None,
            "publishing_company": None,
            "publication_date": None,
            "doi": None,
            "pdf": None,
            "pdf_text": None,
            "mentioned_by": [],
            "references": [],
            "original_references": []
        }
        obj_cit = extract_title(row, obj_cit)
        if PDF_FLAG:
            obj_cit = extract_pdf(row, obj_cit)
        obj_cit = extract_authors(row, obj_cit)
        if PDF_FLAG:
            obj_cit = extract_text_from_pdf(obj_cit)
        array_citation.append(obj_cit)

    obj["mentioned_by"] = array_citation
    return obj

