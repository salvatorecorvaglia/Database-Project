from django.urls import path, include
from paper_api import views

urlpatterns = [
    path('search/',views.catalog_search),
    path('doc-tree/<int:id>/', views.doc_tree),
    path('ncbi/',views.ncbi_scraping_view),
]