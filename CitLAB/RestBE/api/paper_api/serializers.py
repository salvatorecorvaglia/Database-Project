from rest_framework import serializers
from .models import Paper

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class PaperSerializer(serializers.ModelSerializer):
        mentioned_in = RecursiveField(many=True)
        class Meta:
                model = Paper
                fields = ('id','title','abstract','type_paper','isbn','issn','publishing_company','doi','pages','site'
                ,'created_on','year','n_citation','n_version','rating','eprint','pdf','picture','added_on','mentioned_in',
                'owns_version','have_category','writers')