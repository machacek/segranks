from __future__ import print_function, division
from django.core.management.base import BaseCommand, CommandError
from segranks.expandedannotation import ExpandedAnnotation
from segranks.models import RankProject, Annotation
from collections import defaultdict
import pickle
import pprint

class Command(BaseCommand):
    args = 'project_id file_to_be_exported'
    help = 'Pickles raw segment ranks into given file'

    def handle(self, *args, **options):
        project_pk = int(args[0])
        annotations = Annotation.objects.filter(annotated_segment__sentence__project = project_pk).select_related('annotated_segment', 'sentence')

        # Indexed by sentence id, values are lists of expanded annotations
        expanded_annotations = defaultdict(list)

        i = 0
        for annotation in annotations:
            segment = annotation.annotated_segment
            sentence = segment.sentence

            expanded_annotation = ExpandedAnnotation(sentence.sentence_id, segment.segment_str)

            for candidate, rank in zip(segment.candidates, annotation.ranks):
                expanded_annotation.add_ranked_segment(candidate, rank)

            expanded_annotations[sentence.sentence_id, segment.segment_str].append(expanded_annotation) 

            i += 1

        # No more defaultdict
        expanded_annotations = dict(expanded_annotations)

        with open(args[1], mode = 'wb') as output:
            pickle.dump(expanded_annotations, output)

        print("Pickled %s annotations" % i)




    

