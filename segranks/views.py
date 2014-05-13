from django.views.generic import TemplateView, DetailView, ListView, View
from django.db.models import Count
from segranks.models import RankProject, Segment, Sentence
from django.shortcuts import redirect
import random

class ProjectListView(ListView):
    model = RankProject
    template_name = "project_list.html"

class SubmitView(View):
    def post(self, request, pk):
        for i in range(int(request.POST['segments_number'])):
            segment_pk = int(request.POST["segment_%s_pk" % i])
            segment = Segment.objects.get(pk=segment_pk)

            ranks = [int(request.POST["segment_%s_candidate_%s_rank" % (i,j)]) for j in range(len(segment.candidates))]

            if any(rank == 0 for rank in ranks):
                raise ValueError("Rank is zero")

            segment.annotations.create(
                    ranks = " ".join(map(str, ranks)),
                    annotator = request.user,
                    )

        return redirect("segranks.views.annotateview", pk)

class AnnotateView(DetailView):
    template_name = "annotate.html"

    def get_intra_object(self):
        pass

    def get_inter_object(self):
        pass
    
    def get_object(self):
        return Segment.objects\
                .filter(sentence__project__pk = self.kwargs['pk'])\
                .annotate(num_annot=Count('annotations'))\
                .order_by('num_annot', '?')\
                .first()\
                .sentence

class AboutView(TemplateView):
    template_name = "about.html"

# This is a hack to fix the bug in django-registration
from registration.backends.simple.views import RegistrationView as SimpleRegistrationView
class RegistrationView(SimpleRegistrationView):
    def get_success_url(self, request, user):
        return ('/', (), {})
