from django.views.generic import TemplateView, DetailView, ListView, View
from django.db.models import Count, F
from segranks.models import RankProject, Segment, Sentence
from django.shortcuts import redirect
from datetime import datetime, timedelta
from select_pdf import ProbabilityDistribution
import os
import time

class ProjectListView(ListView):
    model = RankProject
    template_name = "project_list.html"

class SubmitView(View):
    def post(self, request, pk):
        time_generated = int(request.POST['time_generated'])
        time_now = int(time.time())
        segments_number = int(request.POST['segments_number'])
        for i in range(segments_number):
            segment_pk = int(request.POST["segment_%s_pk" % i])
            segment = Segment.objects.get(pk=segment_pk)

            ranks = [int(request.POST["segment_%s_candidate_%s_rank" % (i,j)]) for j in range(len(segment.candidates))]

            if any(rank == 0 for rank in ranks):
                raise ValueError("Rank is zero")

            segment.annotations.create(
                    ranks = ranks,
                    annotator = request.user,
                    time_in_seconds = int((time_now - time_generated) / segments_number),
                    )

        return redirect("segranks.views.annotateview", pk)


intra_rate = float(os.getenv('SEGRANKS_INTRA_RATE', 0.05))
inter_rate = float(os.getenv('SEGRANKS_INTER_RATE', 0.05))

class AnnotateView(DetailView):
    template_name = "annotate.html"
        
    def get_object(self):
        project = self.kwargs['pk']
        user = self.request.user

        annotated = Sentence.annotated_by_me(project, user).count()
        annotated_inter = Sentence.annotated_by_me_and_others(project, user).count()
        annotated_intra = Sentence.annotated_by_me_at_least_twice(project, user).count()

        if annotated_intra < int(intra_rate * annotated):
            try:
                return Sentence.random(Sentence.annotated_by_me_once(project, user))
            except IndexError:
                pass

        if annotated_inter < int(inter_rate * annotated):
            try:
                return Sentence.random(Sentence.annotated_only_by_others(project, user))
            except IndexError:
                pass

        return Sentence.random(Sentence.unannotated(project))


class AboutView(TemplateView):
    template_name = "about.html"

# This is a hack to fix the bug in django-registration
from registration.backends.simple.views import RegistrationView as SimpleRegistrationView
class RegistrationView(SimpleRegistrationView):
    def get_success_url(self, request, user):
        return ('/', (), {})
