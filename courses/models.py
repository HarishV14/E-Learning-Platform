from django.db import models
from .fields import OrderField

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    
    class Meta:
        ordering = ['title']
    def __str__(self):
        return self.title

class Course(models.Model):
    owner = models.ForeignKey(User,related_name='courses_created',on_delete=models.CASCADE)
    # one subjec as multiple courses
    subject = models.ForeignKey(Subject,related_name='courses',on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(User,related_name='courses_joined',blank=True)
    
    class Meta:
        ordering = ['-created']
    def __str__(self):
        return self.title
    
class Module(models.Model):
    # one couese as multiple module
    course = models.ForeignKey(Course,related_name='modules',on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # this custom modified poistiveInteger to orderField 
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return f'{self.order}. {self.title}'
    
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Content(models.Model):
    module = models.ForeignKey(Module,related_name='contents',on_delete=models.CASCADE)
    # it will limit only model name with text video image file
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE,
                                     limit_choices_to={'model__in':('text',
                                                                    'video',
                                                                    'image',
                                                                    'file')})
    object_id = models.PositiveIntegerField()
    '''related object combaining the two previous field
      create the instance and relate the both field 
     example if image have object id 1 and text as object id 1
     combine and create the instance and store in item'''
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])
    
    class Meta:
        ordering = ['order']


class ItemBase(models.Model):
    # reverse relationship for child models ex text_related file_related
    owner = models.ForeignKey(User,related_name='%(class)s_related',on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
    def __str__(self):
        return self.title

# abstract=true so we can use itembased class
# In itembased model contains the common fields for other four branch class
# if it text it will contain text as content it file then it should store as fike

class Text(ItemBase):
    content = models.TextField()
    
class File(ItemBase):
    file = models.FileField(upload_to='files')
    
class Image(ItemBase):
    file = models.FileField(upload_to='images')
class Video(ItemBase):
    url = models.URLField()