from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from itertools import groupby
from django.db.models import Avg, Count, F, Max, Min, Sum, Q
import random
import time

class RankProject(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ['created']

    def __unicode__(self):
        return self.name

class Sentence(models.Model):
    project = models.ForeignKey(RankProject, related_name='sentences')
    sentence_id = models.IntegerField()
    source_str = models.TextField()
    reference_str = models.TextField()

    class Meta:
        ordering = ['sentence_id']

    def __unicode__(self):
        return "%s: %s" % (self.sentence_id, short(self.source_str))

    def enumerate_segments(self):
        return enumerate(sorted(self.segments.all(), key= lambda x: int(x.segment_indexes.split(' ')[0])))

    def time_generated(self):
        return int(time.time())

    @classmethod
    def annotated_by_me(cls, project, user):
        return cls.objects\
                .filter(project=project)\
                .filter(segments__annotations__annotator=user)\
                .distinct()
    
    @classmethod
    def annotated_by_others(cls, project, user):
        others = User.objects.exclude(pk=user.pk)
        return cls.objects\
                .filter(project=project)\
                .filter(segments__annotations__annotator__in=others)\
                .distinct()
    
    @classmethod
    def annotated_only_by_me(cls, project, user):
        return cls.annotated_by_me(project, user)\
                .exclude(pk__in=cls.annotated_by_others(project, user))
    
    @classmethod
    def annotated_only_by_others(cls, project, user):
        return cls.annotated_by_others(project, user)\
                .exclude(pk__in=cls.annotated_by_me(project, user))
    
    @classmethod
    def annotated_by_me_and_others(cls, project, user):
        return cls.annotated_by_me(project, user)\
                .filter(pk__in=cls.annotated_by_others(project, user))

    @classmethod
    def annotated_by_me_at_least_twice(cls, project, user):
        return cls.annotated_by_me(project, user)\
                .annotate(n_segments=Count('segments', distinct=True), n_annotations=Count('segments__annotations', distinct=True))\
                .filter(n_annotations__gt=F('n_segments'))\
                .distinct()
    
    @classmethod
    def annotated_by_me_once(cls, project, user):
        return cls.annotated_by_me(project, user)\
                .annotate(n_segments=Count('segments', distinct=True), n_annotations=Count('segments__annotations', distinct=True))\
                .filter(n_annotations__lte=F('n_segments'))\
                .distinct()
    
    @classmethod
    def unannotated(cls, project):
        return cls.objects.filter(project__pk=project, segments__annotations__annotator=None)

    @classmethod
    def random(cls, in_query):
        return cls.objects.filter(pk__in=in_query).order_by('?')[0]



class Segment(models.Model):
    sentence = models.ForeignKey(Sentence, related_name='segments')
    segment_str = models.TextField()
    segment_indexes = models.TextField()
    candidates_str = models.TextField()

    @property
    def source_groups(self):
        segment_indexes = set(map(int,self.segment_indexes.split(' ')))
        source_sentence = self.sentence.source_str.split(' ')
        for is_segment, group in groupby(enumerate(source_sentence), key=lambda x: x[0] in segment_indexes):
            yield is_segment, ' '.join([token for _,token in group])

    @property
    def candidates(self):
        return self.candidates_str.split('\n')
    
    def enum_candidates(self):
        l = list(enumerate(self.candidates_str.split('\n')))
        random.shuffle(l)
        return l

    @property
    def avialable_ranks(self):
        return list(range(1,len(self.candidates)+1))

    def __unicode__(self):
        return short(self.segment_str)

class Annotation(models.Model):
    annotated_segment = models.ForeignKey(Segment, related_name='annotations')
    ranks_str = models.TextField()
    annotator = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)    
    time_in_seconds = models.IntegerField()

    @property
    def ranks(self):
        return list(map(int, self.ranks_str.split(' ')))

    @ranks.setter
    def ranks(self, value):
        self.ranks_str = ' '.join(map(str, map(int,value)))


def short(string):
    return string[:min(len(string), 80)]
