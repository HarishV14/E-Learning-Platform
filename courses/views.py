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
class OwnerCourseMixin(OwnerMixin):
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


'''Uses a model form to create a new course it uses the template define in
    ownerCourseEditMixin'''
class CourseCreateView(OwnerCourseEditMixin, CreateView):   
    pass

'''Allows to edit the existing course so it is OwnerCourseEditMixin'''
class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    pass

'''uses ownerCoueseMixin for model'''
class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'


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

