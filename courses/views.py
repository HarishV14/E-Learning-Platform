from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Course

'''class can used for views that intract with any model that contains owner attribure
    it filter that courses or modules for given object listed 
    by the current user created courses or modules for given object'''
class OwnerMixin(object):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

''' Ensures that the owner of an object is set to the current logged-in user
    when the form is validated.'''
class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

''''Mixin that sets up the Course model with specified fields and defines
    a success URL for when the course form is successfully submitted.
    and inherit ownerMixin for query_set
    '''
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin

# this view and mixin for course
class OwnerCourseMixin(OwnerMixin,LoginRequiredMixin,
                       PermissionRequiredMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')

'''Combines both OwnerCourseMixin and OwnerEditMixin to handle course
    editing functionality with ownership assignment and form validation.
    Uses a specific template for the course form.'''
class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'
    

'''List course created by user by inherting ownerCourseMixin '''
class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'


'''Uses a model form to create a new course it uses the template define in
    ownerCourseEditMixin'''
class CourseCreateView(OwnerCourseEditMixin, CreateView):   
    permission_required = 'courses.add_course'

'''Allows to edit the existing course so it is OwnerCourseEditMixin'''
class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'

'''uses ownerCoueseMixin for model'''
class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'

# this view class for  modules of the courses
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet

'''TemplateResponseMixin: This mixin takes charge of rendering templates
and returning an HTTP response. it gives render_to_response()'''

class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None
    #creating and returning the formset for modules object current course instance
    #optional data is passed when handiling a post request
    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course,data=data)
    
    # fetch the course object and ensure the user is owner of course
    # dispatch ensures only the owner of course can acess the view 
    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course,id=pk,owner=request.user)
        return super().dispatch(request, pk)
    
    # handles the GET request to render the formset
    def get(self, request, *args, **kwargs):
        # generates empty formset (without prefilled)
        formset = self.get_formset()
        return self.render_to_response({'course': self.course,'formset': formset})
    
    # handle the POST request ie.. form submission 
    def post(self, request, *args, **kwargs):
        # binds the submitted data to the formset
        formset = self.get_formset(data=request.POST)
        # if form is valid saves updating the modules related to course
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        # if form is not valid rerender the formset with validation error
        return self.render_to_response({'course': self.course,'formset': formset})

# this view class for content of the modules
from django.forms.models import modelform_factory
from django.apps import apps
from .models import Module, Content
'''
Modelform_factory-- to dynamically generate forms based on the model being used 
app.get_model()-- to dynamically load based on content type 
'''
class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'
    
    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses',model_name=model_name)
        return None
    
    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner','order','created','updated'])
        # passed to the form constructor for intializing form
        return Form(*args, **kwargs)
    
    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module,id=module_id,course__owner=request.user)
        self.model = self.get_model(model_name)
        #if id is none it creates new object and else id of the content object is updated
        if id:
            self.obj = get_object_or_404(self.model,id=id,owner=request.user)
        return super().dispatch(request, module_id, model_name, id)
    
    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,'object': self.obj})
    
    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model,instance=self.obj,data=request.POST,files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(module=self.module,item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form,'object': self.obj})
    
class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content,id=id,
                                    module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)

class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'
    
    def get(self, request, module_id):
        module = get_object_or_404(Module,id=module_id,course__owner=request.user)
        return self.render_to_response({'module': module})


from braces.views import CsrfExemptMixin, JsonRequestResponseMixin

class ModuleOrderView(CsrfExemptMixin,JsonRequestResponseMixin,View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id,course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})

class ContentOrderView(CsrfExemptMixin,JsonRequestResponseMixin,View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id,module__course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})








# this done before mixin keep it as reference 
# class ManageCourseListView(ListView):
#     model = Course
#     template_name = 'courses/manage/course/list.html'
    
#     # retrieve only course created by current user
#     def get_queryset(self):
#         # this will store all the courses
#         qs = super().get_queryset()
#         # and it filter and send the courses
#         return qs.filter(owner=self.request.user)

