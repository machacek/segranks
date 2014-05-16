from django.views.generic import TemplateView, DetailView, ListView, View
from django.db.models import Count, F
from segranks.models import RankProject, Segment, Sentence
from django.shortcuts import redirect
from datetime import datetime, timedelta
from select_pdf import ProbabilityDistribution

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
                    ranks = ranks,
                    annotator = request.user,
                    )

        return redirect("segranks.views.annotateview", pk)


intra_rate = 0.3
inter_rate = 0.3
normal_rate = 1 - (intra_rate + inter_rate)

class AnnotateView(DetailView):
    template_name = "annotate.html"

    def annotated_once_by_others(self):
        return Sentence.objects\
                .filter(project__pk=self.kwargs['pk'])\
                .exclude(segments__annotations__annotator=self.request.user)\
                .annotate(n_segments=Count('segments'), n_annotations=Count('segments__annotations'))\
                .filter(n_segments=F('n_annotations'))\
                .distinct()[0]

    def annotated_once_by_me(self):
        return Sentence.objects\
                .filter(project__pk=self.kwargs['pk'], segments__annotations__annotator=self.request.user)\
                .filter(segments__annotations__created__lte=(datetime.now() - timedelta(seconds=12)))\
                .annotate(n_segments=Count('segments'), n_annotations=Count('segments__annotations'))\
                .filter(n_segments=F('n_annotations'))\
                .distinct()[0]

    def not_annotated(self):
        return Sentence.objects\
                .filter(project__pk=self.kwargs['pk'], segments__annotations__annotator=None)\
                .distinct()[0]
        
    def get_object(self):
        random_method = ProbabilityDistribution([
                (intra_rate, self.annotated_once_by_me),
                (inter_rate, self.annotated_once_by_others),
                (normal_rate, self.not_annotated),
            ]).random_choice()

        try:
            return random_method()
        except IndexError:
            return self.not_annotated()

class AboutView(TemplateView):
    template_name = "about.html"

# This is a hack to fix the bug in django-registration
from registration.backends.simple.views import RegistrationView as SimpleRegistrationView
class RegistrationView(SimpleRegistrationView):
    def get_success_url(self, request, user):
        return ('/', (), {})
