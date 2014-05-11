from django.db import models
from django.contrib.auth.models import User
from itertools import groupby
import random

class RankProject(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()
    instructions = models.TextField()
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.name

class Sentence(models.Model):
    project = models.ForeignKey(RankProject, related_name='sentences')
    sentence_id = models.IntegerField()
    source_str = models.TextField()
    reference_str = models.TextField()

    class Meta:
        ordering = ['sentence_id']

    def __str__(self):
        return "%s: %s" % (self.sentence_id, short(self.source_str))

    def enumerate_segments(self):
        return enumerate(sorted(self.segments.all(), key= lambda x: int(x.segment_indexes.split(' ')[0])))

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
        l = list(enumerate(self.candidates_str.split('\n')))
        random.shuffle(l)
        return l

    @property
    def avialable_ranks(self):
        return list(range(1,len(self.candidates)+1))

    def __str__(self):
        return short(self.segment_str)

class Annotation(models.Model):
    annotated_segment = models.ForeignKey(Segment, related_name='annotations')
    ranks = models.TextField()
    annotator = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)    

def short(str):
    return str[:min(len(str), 80)]
