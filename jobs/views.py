from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from jobs.forms import ApplicationForm
from jobs.models import Job
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.db.models import Q 

class JobList(ListView):
    model = Job
    context_object_name ='jobs'
    paginate_by = 5
    page_limit = 25
    
    def get_queryset(self): 
        return Job.objects.all()
  
class Index(TemplateView):    
    def get(self, request, *args, **kwargs):
        return render(request, 'jobs/index.html')
    
    
class JobsResultsView(ListView):
    model = Job
    template_name = 'job_list.html' 
    context_object_name ='jobs'
    paginate_by = 5
    page_limit = 25
    
    def get_queryset(self): 
        search_query = self.request.GET.get("search",None)
        selected_job_type = self.request.GET.get('job_types', None)  
        selected_location = self.request.GET.get('locations', None)  

    

        object_list = Job.objects.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )
        
        return object_list
   
    
class JobDetailView(DetailView):
    model = Job
    context_object_name ='job'
    
    def get_context_data(self, *args, **kwargs):
        context = super(JobDetailView,
             self).get_context_data(*args, **kwargs)
        # add extra field
        context["form"] =  ApplicationForm()      
        return context
    
class JobCreate(CreateView):
    model = Job
    fields = '__all__'
    success_url = reverse_lazy('jobs')
    
class JobUpdate(UpdateView):
    model = Job
    fields = '__all__'
    success_url = reverse_lazy('jobs')
    
class JobDelete(DeleteView):
    model = Job
    context_object_name ='job'
    success_url = reverse_lazy('jobs')



