from django import forms
from django.forms.models import inlineformset_factory
from .models import Course, Module

''' formset group of form and multiple form in single page
    inline formset provides an which simply works with related models
    In this module object related to course
    fields= includes in each form of the formset
    extra= Allow you to set the no of empty extra forms'''

ModuleFormSet = inlineformset_factory(Course,Module,fields=['title','description'],
                                      extra=2,can_delete=True)