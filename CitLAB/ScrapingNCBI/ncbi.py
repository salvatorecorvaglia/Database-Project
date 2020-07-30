from bs4 import BeautifulSoup
import requests
import re
from selenium import webdriver
import time
import textract
import psycopg2
import json

SCRAPING_FLAG = False

driver = webdriver.PhantomJS(executable_path="/Users/danilogiovannico/Desktop/PROGETTO DATABASE/CitLAB/ScrapingNCBI/phantomjs/bin/phantomjs")

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
                f = open("./PDF/"+link_pdf['href'].split("/")[-1:][0])
                f.close()
            except IOError:
                options = webdriver.ChromeOptions()

                profile = {
                    "download.default_directory": "/Users/danilogiovannico/Desktop/PROGETTO DATABASE/CitLAB/ScrapingNCBI/PDF",
                    "plugins.always_open_pdf_externally": True
                }
                options.add_experimental_option("prefs", profile)
                driver_pdf = webdriver.Chrome(
                    '/Users/danilogiovannico/Desktop/PROGETTO DATABASE/CitLAB/ScrapingNCBI/chrome_driver/chromedriver',
                    chrome_options=options)  # Optional argument, if not specified will search path.

                driver_pdf.implicitly_wait(10)
                driver_pdf.maximize_window()
                driver_pdf.get(obj["pdf"])
                time.sleep(5)
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
            driver.get(obj["url"])
            p_element = driver.find_element_by_class_name('p-first-last')
            obj["abstract"] = clear_text(p_element.text)
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

def mentioned_in(obj):
    array_citation = []

    #print(el["title"].lstrip().split(".")[0])
    html_content = requests.get(obj["url"]+'citedby').text
    soup = BeautifulSoup(html_content, "lxml")

    separator = ', '
    link_array = []
    divs = soup.find_all("div", class_="rprt")[1:]
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
        obj_cit = extract_pdf(row, obj_cit)
        obj_cit = extract_authors(row, obj_cit)
        obj_cit = extract_text_from_pdf(obj_cit)
        array_citation.append(obj_cit)

    obj["mentioned_by"] = array_citation
    return obj

def extract_text_from_pdf(obj):
    try:
        text = textract.process("./PDF/"+obj['pdf'].split("/")[-1:][0]).decode("utf-8")
        obj["pdf_text"] = text.replace("\"","'").replace("{","[").replace("}","]")
    except Exception as e:
        pass
    return obj

if SCRAPING_FLAG:
    html_content = requests.get(base_url+"clinical+data").text
    soup = BeautifulSoup(html_content, "lxml")

    separator = ', '
    link_array = []
    divs = soup.find_all("div", class_="rslt")
    for row in divs:
        obj = {
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

        obj = extract_title(row, obj)
        obj = extract_pdf(row, obj)
        obj = extract_authors(row, obj)
        obj = mentioned_in(obj)
        obj = extract_text_from_pdf(obj)
        link_array.append(obj)
        print(obj)
else:
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="root",
            host="127.0.0.1",
            port="5432",
            database="citlabdb"
        )

        # Create a cursor connection object to a PostgreSQL instance and print the connection properties.
        cursor = connection.cursor()
        postgreSQL_select_Query = "select * from paper"

        cursor.execute(postgreSQL_select_Query)
        papers = cursor.fetchall()

        for row in papers:
            '''print("Id = ", row[0])
            print("Title = ", row[1])
            print("Abstract  = ", row[2])
            print("Type Paper = ", row[3])
            print("Isbn = ", row[4])
            print("Issn  = ", row[5])
            print("Publishing_company = ", row[6])
            print("Doi = ", row[7])
            print("Pages  = ", row[8])
            print("Site = ", row[9])
            print("Created_on = ", row[10])
            print("Year  = ", row[11])
            print("N_citation = ", row[12])
            print("N_version = ", row[13])
            print("Rating  = ", row[14])
            print("Eprint = ", row[15])
            print("Pdf = ", row[16])
            print("Picture  = ", row[17])
            print("Added_on  = ", row[18])
            print("Writers = ", row[19])
            print("Original_references = ", row[20])
            print("Pdf_text  = ", row[21])
            print("References = ", row[22])'''

            array_mentioned_id = []
            cursor = connection.cursor()
            postgreSQL_select_Query = "select * from paper_mentioned_in where from_paper_id = %s"

            cursor.execute(postgreSQL_select_Query, (row[0],))
            paper_mentioned_in = cursor.fetchall()

            for row_cit in paper_mentioned_in:
                '''print("Id = ", row_cit[0])
                print("From paper id = ", row_cit[1])
                print("To paper id  = ", row_cit[2])
                print("\n")'''
                array_mentioned_id.append(row_cit[2])

            if row[21]:
                pdf_text = row[21].replace("\n"," ").replace("\"","").replace("{","(").replace("}",")").replace("[","(").replace("]",")")
            else:
                pdf_text = ""
            intestation = {"index": {"_index": "paper", "_id": row[0]}}
            document = {
                "title": row[1],
                "abstract": row[2],
                "type_paper": row[3],
                "isbn": row[4],
                "issn": row[5],
                "publishing_company": row[6],
                "doi": row[7],
                "pages": row[8],
                "site": row[9],
                "created_on": row[10],
                "year": row[11],
                "n_citation": row[12],
                "n_version": row[13],
                "rating": row[14],
                "eprint": row[15],
                "pdf": row[16],
                "picture": row[17],
                "added_on": str(row[18]).split(" ")[0],
                "writers": row[19],
                "original_references": row[20],
                "pdf_text": pdf_text,
                "references": row[22],
                "mentioned_in": array_mentioned_id
            }
            with open('documents.json', 'a') as file:
                json.dump(intestation, file)
                file.write("\n")
                json.dump(document, file)
                file.write("\n")

        file.close()
        # Handle the error throws by the command that is useful when using python while working with PostgreSQL
    except Exception as error:
        print("Error connecting to PostgreSQL database", error)
        connection = None

    # Close the database connection
    finally:
        if (connection != None):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is now closed")