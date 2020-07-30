from django_elasticsearch_dsl import Document, Nested, fields
from django_elasticsearch_dsl.registries import registry
from .models import Paper


@registry.register_document
class CarDocument(Document):

    class Index:
        # Name of the Elasticsearch index
        name = 'papers'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Paper # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = ['id','title','abstract','type_paper','isbn','issn','publishing_company','doi','pages','site'
                ,'created_on','year','n_citation','n_version','rating','eprint','pdf','picture','added_on','writers']
