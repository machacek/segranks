from django.views.generic import TemplateView, DetailView, ListView
from django.db.models import Count
from segranks.models import RankProject, Segment, Sentence

class ProjectListView(ListView):
    model = RankProject
    template_name = "project_list.html"

class AnnotateView(DetailView):
    template_name = "annotate.html"

    def post(self, request, *args, **kwargs):
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

        return self.get(request, *args, **kwargs)
    
    def get_object(self):
        return Segment.objects\
                .filter(sentence__project__pk = self.kwargs['pk'])\
                .annotate(num_annot=Count('annotations'))\
                .order_by('num_annot', '?')\
                .first()\
                .sentence

class AboutView(TemplateView):
    template_name = "about.html"

