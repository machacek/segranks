from __future__ import print_function
from django.core.management.base import BaseCommand, CommandError
from segranks.models import RankProject, Sentence, Segment
from itertools import count, groupby
from collections import namedtuple
from tabulate import tabulate

class Command(BaseCommand):
    args = 'project_name'
    help = 'Exports annotations to tsv format'

    def handle(self, *args, **options):
        if not args:
            fields = ["id", "name", "created", "description"]
            print(tabulate(
                    RankProject.objects.values_list(*fields),
                    headers = fields,
                    ))
            return
        
        project_pk = args[0]
        for sentence in Sentence.objects.filter(project=project_pk)\
                                        .exclude(segments__annotations=None)\
                                        .prefetch_related('segments', 'segments__annotations'):
            for segment in sentence.segments.all():
                for annotation in segment.annotations.all():

                    print("Segment:",segment.segment_str)
                    print("Annotator:",annotation.annotator.username)

                    key_func = lambda x: x[0]
                    grouped_segments = groupby(sorted(zip(annotation.ranks, segment.candidates), key=key_func), key=key_func)
                    for rank, group in grouped_segments:
                        print(rank, "-", *["<%s>" % cand for rank, cand in group])
                    print()


                

