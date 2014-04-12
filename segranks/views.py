from django.views.generic import TemplateView, DetailView, ListView
from django.db.models import Count
from segranks.models import RankProject, Segment, Sentence

class ProjectListView(ListView):
    model = RankProject
    template_name = "project_list.html"

class AnnotateView(TemplateView):
    template_name = "annotate.html"
    
    def get_sentence(self):
        sentence = Segment.objects\
                .filter(sentence__project__pk = self.kwargs['pk'])\
                .annotate(num_annot=Count('annotations'))\
                .order_by('-num_annot')\
                .first()\
                .sentence

        sentence = Sentence.objects.order_by('?')[0]

        return sentence

    def get_context_data(self, *args, **kwargs):
        context = super(AnnotateView, self).get_context_data(**kwargs)
        sentence = self.get_sentence()
        context['sentence'] = sentence

        segments = list(sentence.segments.all())
        for segment in segments:
            segment.candidates_split = segment.candidates_str.split('\n')
        context['segments'] = segments

        context['ranks'] = range(1,6)

        return context

class AboutView(TemplateView):
    template_name = "about.html"

