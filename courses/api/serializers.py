from rest_framework import serializers
from ..models import Subject

# to pass the subject data to this to serialize the data and it converts to json
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'title', 'slug']
        
from ..models import Course,Module

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['order', 'title', 'description']

class CourseSerializer(serializers.ModelSerializer):
    # keep modules as nested structure in json
    modules = ModuleSerializer(many=True, read_only=True)
    class Meta:
        model = Course
        fields = ['id', 'subject', 'title', 'slug', 'overview','created', 'owner', 'modules']  

'''this is another way of nested serializer'''     
from ..models import Content
# ItemRelatedField is way to customize how related item in objects are displayed in the API output
class ItemRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        # render method on item it provides cleaner and more user-friendly representation of item
        return value.render()
    
class ContentSerializer(serializers.ModelSerializer):
    item = ItemRelatedField(read_only=True)
    class Meta:
        model = Content
        fields = ['order', 'item']  

class ModuleWithContentsSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True)
    class Meta:
        model = Module
        fields = ['order', 'title', 'description', 'contents']
        
class CourseWithContentsSerializer(serializers.ModelSerializer):
    modules = ModuleWithContentsSerializer(many=True)
    class Meta:
        model = Course
        fields = ['id', 'subject', 'title', 'slug',
                  'overview', 'created', 'owner', 'modules']  