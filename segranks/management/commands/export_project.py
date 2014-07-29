from __future__ import print_function, division
from django.core.management.base import BaseCommand, CommandError
from segranks.expandedannotation import ExpandedAnnotation
from segranks.models import RankProject, Annotation
from collections import defaultdict
import pprint
import tabulate
import codecs

class Command(BaseCommand):
    args = 'project_id file_to_be_exported'
    help = 'Pickles raw segment ranks into given file'

    def handle(self, *args, **options):
        if len(args) == 0:
            return self.print_projects()

        project_pk = int(args[0])
        file_name = args[1]
        try:
            output_format = args[2]
        except IndexError:
            output_format = "json"

        annotations = Annotation.objects.filter(annotated_segment__sentence__project = project_pk).select_related('annotated_segment', 'sentence')

        # Indexed by sentence id, values are lists of expanded annotations
        expanded_annotations = defaultdict(list)

        i = 0
        for annotation in annotations:
            segment = annotation.annotated_segment
            sentence = segment.sentence

            expanded_annotation = dict()

            for candidate, rank in zip(segment.candidates, annotation.ranks):
                expanded_annotation[candidate] = rank
        
            if output_format == "pickle":
                expanded_annotations[sentence.sentence_id, segment.segment_str].append(expanded_annotation) 
            elif output_format == "json":
                expanded_annotations[u"%s,%s" % (sentence.sentence_id, segment.segment_str)].append(expanded_annotation) 
            else:
                raise ValueError("Unknown output format: %s" % output_format)



            i += 1

        # No more defaultdict
        expanded_annotations = dict(expanded_annotations)

        if output_format == "pickle":
            with open(file_name, mode = 'wb') as output:
                import pickle
                pickle.dump(expanded_annotations, output)
        elif output_format == "json":
            with codecs.open(file_name, mode = 'w', encoding='utf-8') as output:
                import json
                print(json.dumps(expanded_annotations,
                    sort_keys=True,
                    ensure_ascii=False,
                    indent=4,
                    separators=(',', ': '),
                    encoding = 'utf-8',
                ), file=output)
        else:
            raise ValueError("Unknown output format: %s" % output_format)

        print("Exported %s annotations" % i)


    def print_projects(self):
        print("Usage: ./manage.py export_project <project_id> <out_file> {pickle|json}\n")

        projects = []

        for project in RankProject.objects.all():
            projects.append((str(project.pk), project.name, project.description))

        print(tabulate.tabulate(
                projects,
                headers=("id", "name", "description"),
                tablefmt="plain",
                ))
    

