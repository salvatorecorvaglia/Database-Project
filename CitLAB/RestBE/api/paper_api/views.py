from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from .serializers import PaperSerializer
from .models import Paper
import math
from bs4 import BeautifulSoup
import requests
import re
from selenium import webdriver
import time
import textract
from common.ncbi.ncbi_scraping import extract_title
from common.ncbi.ncbi_scraping import extract_pdf
from common.ncbi.ncbi_scraping import extract_authors
from common.ncbi.ncbi_scraping import mentioned_in
from common.ncbi.ncbi_scraping import extract_text_from_pdf
from django.db import connection

# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ncbi_scraping_view(request, *args, **kwargs):
    if request.GET.get('q', None):
        query = request.GET.get('q', None).replace(" ","+")
        PDF_FLAG = True
        SCRAPING_FLAG = False
        if SCRAPING_FLAG:
            base = "https://www.ncbi.nlm.nih.gov"
            base_api = "https://api.ncbi.nlm.nih.gov/lit/ctxp/v1/pmc/?format=citation&id="
            base_url = "https://www.ncbi.nlm.nih.gov/pmc/?term="

            html_content = requests.get(base_url+query).text
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
                counter_doc = Paper.objects.filter(title=obj['title']).count()
                if counter_doc > 0:
                    continue
                else:
                    if PDF_FLAG:
                        obj = extract_pdf(row, obj)
                    obj = extract_authors(row, obj)
                    obj = mentioned_in(obj)
                    if PDF_FLAG:
                        obj = extract_text_from_pdf(obj)
                    link_array.append(obj)

            for doc_obj in link_array:
                if Paper.objects.filter(title=doc_obj['title']).count() < 1:
                    doc = Paper.objects.create(id=(Paper.objects.all().order_by("-id")[0].id+1),title=doc_obj['title'], abstract=doc_obj['abstract'],type_paper="PDF",publishing_company=doc_obj['publishing_company'],
                        site=doc_obj['url'],created_on=doc_obj["publication_date"],year=doc_obj['year'],n_citation=len(doc_obj["mentioned_by"]),pdf=doc_obj['pdf'],pdf_text=doc_obj['pdf_text'],
                        references=str(doc_obj['references']),original_references=str(doc_obj['original_references']),writers=doc_obj["authors"])
                    doc.save()
                    parentId = doc.id
                else:
                    parentId = Paper.objects.filter(title=doc_obj['title']).values()[0]['id']

                for mention in doc_obj["mentioned_by"]:
                    if Paper.objects.filter(title=mention['title']).count() > 0:
                        childrenId = Paper.objects.filter(title=mention['title']).values()[0]['id']
                    else:
                        ment = Paper.objects.create(id=(Paper.objects.all().order_by("-id")[0].id+1),title=mention['title'], abstract=mention['abstract'],type_paper="PDF",publishing_company=mention['publishing_company'],
                            site=mention['url'],created_on=mention["publication_date"],year=mention['year'],n_citation=len(mention["mentioned_by"]),pdf=mention['pdf'],pdf_text=mention['pdf_text'],
                            references=str(mention['references']),original_references=str(mention['original_references']),writers=mention["authors"])
                        ment.save()
                        childrenId = ment.id
                    try:
                        with connection.cursor() as cursor:
                            if parentId is not childrenId:
                                cursor.execute('INSERT INTO paper_mentioned_in (from_paper_id, to_paper_id) VALUES (%s,%s)',[parentId, childrenId])
                    except Exception as error:
                        pass

        return Response(data='Successfully!', status=status.HTTP_200_OK)
    else:
        return Response(data="A problem occurred!", status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def catalog_search(request, *args, **kwargs):
    max_for_page = 5
    if request.GET.get('q', None) and request.GET.get('page', None):
        min_page = max_for_page*int(request.GET.get('page', None)) - max_for_page
        max_page = max_for_page*int(request.GET.get('page', None))

        num_papers = Paper.objects.count()
        num_max_pages = math.ceil(num_papers/max_for_page)

        if int(request.GET.get('page', None)) > num_max_pages:
            paginator = {
                'total': num_papers,
                'num_max_pages': num_max_pages,
                'items_per_page': max_for_page,
                'current_page': num_max_pages
            }

            min_page = max_for_page*num_max_pages - max_for_page
            max_page = max_for_page*num_max_pages

            papers = Paper.objects.all().order_by('-id')[min_page:max_page]
            serializer_class = PaperSerializer(papers, many=True)
        else:    
            paginator = {
                'total': num_papers,
                'num_max_pages': num_max_pages,
                'items_per_page': max_for_page,
                'current_page': request.GET.get('page', None)
            }
            papers = Paper.objects.all().order_by('-id')[min_page:max_page]
            serializer_class = PaperSerializer(papers, many=True)
        
        return Response(data={'papers': serializer_class.data, 'paginator': paginator}, status=status.HTTP_200_OK)
    else:
        return Response(data="Invalid search query!", status=status.HTTP_401_UNAUTHORIZED)

tree = []
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doc_tree(request, id):
    global tree
    tree = []
    paper = Paper.objects.get(pk=id)
    serializer_class = PaperSerializer(paper)
    dirty_tree = iterate(serializer_class.data)
    clear_tree = remove_dupes(dirty_tree)
    print(len(clear_tree))
    return Response(data=dirty_tree, status=status.HTTP_200_OK)

def iterate(object, parent_id=None):
    global tree
    if parent_id is None:
        obj = {
            "guid": "",
            "displayName": "",
            "children": []
        }
    else:
        obj = {
            "guid": "",
            "displayName": "",
            "parentId": parent_id,
            "children": []
        }
    for key, item in object.items():
            if key is 'id':
                obj['guid'] = item
            elif key is 'title':
                obj['displayName'] = item
            elif key is 'mentioned_in':
                child = []
                size = len(item)
                for i in range(size):
                    child.append(item[i]['id'])

                obj['children'] = child
                tree.append(obj)

                for i in range(size):
                    iterate(item[i],obj['guid'])
    return tree

def remove_dupes(mylist):
    newlist = [mylist[0]]
    for e in mylist:
        if e not in newlist:
            newlist.append(e)
    return newlist