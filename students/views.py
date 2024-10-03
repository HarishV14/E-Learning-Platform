from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login

class StudentRegistrationView(CreateView):
    template_name = 'students/student/registration.html'
    # this is used to create the registration form
    form_class = UserCreationForm
    success_url = reverse_lazy('student_course_list')
    
    def form_valid(self, form):
        result = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['username'],password=cd['password1'])
        login(self.request, user)
        return result

from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CourseEnrollForm

class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm
    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('student_course_detail',args=[self.course.id])


from django.views.generic.list import ListView
from courses.models import Course
class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'
    
    def get_queryset(self):
        # this parent class of get_queryset method which retrieves the intial list of course
        qs = super().get_queryset()
        # print(qs)
        #in that checking the users in the students field of the course then list the course
        return qs.filter(students__in=[self.request.user])


from django.views.generic.detail import DetailView

class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'students/course/detail.html'
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])
    
    # this add extra context to template in addition to course data
    def get_context_data(self, **kwargs):
        # call the parent class's get_context_data method and get the initial context data for the view
        context = super().get_context_data(**kwargs)
        # get course object
        course = self.get_object()
        # if the module id is passed or present in url
        if 'module_id' in self.kwargs:
            # get current module
            try:
                context['module'] = course.modules.get(id=self.kwargs['module_id'])
            except Module.DoesNotExist:
                context['module'] = None
        else:
            # get first module
            modules = course.modules.all()
            if modules.exists():
                # Safely get the first module
                context['module'] = modules.first()
            else:
                context['module'] = None 
        return context