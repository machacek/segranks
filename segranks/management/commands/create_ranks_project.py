from django.core.management.base import BaseCommand, CommandError
from segranks.models import RankProject
import codecs
from itertools import count, groupby
from collections import namedtuple

class Command(BaseCommand):
    args = 'name data_file description instructions'
    help = 'Creates new RanksProject and loads givet data file into database'

    def handle(self, *args, **options):
        name, data_file, description, instruction = args

        self.stdout.write("Creating project...")
        project = RankProject(
                name=name,
                description=description,
                instructions=instruction,
                )
        project.save()

        self.stdout.write("Importing sentences", ending="")
        try:
            # Group rows by sentence
            rows = rows_generator(data_file)
            grouped = groupby(rows, key=lambda x: (x.sentence_id, x.source_str, x.reference_str)) 

            # Iterate sentences
            for (sentence_id, source_str, reference_str), segments in grouped:

                # Create sentence in the database
                sentence = project.sentences.create(
                        sentence_id = sentence_id,
                        source_str = source_str,
                        reference_str = reference_str,
                        )

                # Group segments by source segment and iterate groups
                segments_grouped = groupby(segments, key=lambda x: x.segment_str)
                for segment_str, segments in segments_grouped:
                    sentence.segments.create(
                            segment_str = segment_str,
                            candidates_str = "\n".join(segment.candidate_str for segment in segments),
                            )

                self.stdout.write(".", ending="")
        except:
            project.delete()
            raise
        finally:
            self.stdout.write("")
        
        self.stdout.write("Imported %s sentences" % project.sentences.count())

RowTuple = namedtuple("RowTuple", ['sentence_id', 'source_str', 'reference_str', 'segment_str', 'candidate_str'])
def rows_generator(data_file):
    with codecs.open(data_file, 'r', 'utf-8') as data:
        for i, line in zip(count(1), data):
            # Process the line and unpack the values
            try:
                sentence_id, source_str, reference_str, segment_str, candidate_str = line.strip().split('\t')
            except ValueError:
                raise ValueError("Line %s has wrong number of fields" % i)

            # Create instance and yield it
            yield RowTuple(
                    sentence_id = int(sentence_id),
                    source_str = source_str,
                    reference_str = reference_str,
                    segment_str = segment_str,
                    candidate_str = candidate_str,
                    )

