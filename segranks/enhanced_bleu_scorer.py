from __future__ import unicode_literals
import pickle
import math
import codecs

from collections import defaultdict, Counter

LOWERCASE = False
N = 4

class Scorer(object):
    def __init__(self, database, **kwargs):
        self.database_file = database

    def prepare_stats(self, sentence_id, sentence, alignment=None):
        sentence_id += 1

        if LOWERCASE:
            sentence = sentence.strip().lower().split()
        else:
            sentence = sentence.strip().split()

        stats = []
        for i in range(N):
            ngrams = Counter(find_ngrams(sentence, i+1))
            clipped_ngrams = ngrams & self.reference_ngrams[sentence_id][i]

            count = sum(ngrams.values())
            clipped_count = sum(clipped_ngrams.values())

            stats.append(clipped_count)
            stats.append(count)

        stats.append(self.reference_lengths[sentence_id])
        return stats

    
    def calculate_score(self, comps):
        log_acc = 0
        for i in range(N):
            clipped_count = comps[2*i]
            count = comps[2*i + 1]
            try:
                log_acc += math.log(float(clipped_count) / float(count))
            except ZeroDivisionError:
                return 0.0
        base_score = math.exp(log_acc / N)
            
        candidate_length = comps[1]
        reference_length = comps[-1]
        if candidate_length > reference_length:
            BP = 1
        else:
            BP = math.exp(1 - float(reference_length) / float(candidate_length))

        return BP * base_score 

    def number_of_scores(self):
        return 2*N + 1

    def set_reference_files(self, file_names):
        self.reference_ngrams = [None]
        self.reference_lengths = [None]
        for file_name in file_names:
            self.load_reference(file_name)
        self.load_database()

    def load_reference(self, file_name):
        with codecs.open(file_name, 'r', 'utf-8') as file:
            for sentence_id, line in enumerate(file, 1):
                
                if LOWERCASE:
                    sentence = line.strip().lower().split()
                else:
                    sentence = line.strip().split()

                if len(self.reference_ngrams) == sentence_id:
                    self.reference_ngrams.append([Counter() for _ in range(N)])
                    self.reference_lengths.append(len(sentence))

                for n in range(N):
                    ngrams = Counter(find_ngrams(sentence, n+1)) 
                    self.reference_ngrams[sentence_id][n] |= ngrams

    def use_alignment(self):
        return False

    def load_database(self):
        with open(self.database_file, 'rb') as database_file:
            rank_database = pickle.load(database_file)

        for (sentence_id, source_segment), annotations in rank_database.items():
            for annotation in annotations:
                best_rank = min(map(lambda x: x.rank, annotation.segment_indexed.values()))
                best_segments = list(filter(
                                    lambda x: annotation.segment_indexed[x].rank == best_rank,
                                    annotation.segment_indexed
                                ))

                for segment in best_segments:
                    if LOWERCASE:
                        segment = segment.strip().lower().split()
                    else:
                        segment = segment.strip().split()

                    for i in range(N):
                        ngrams = Counter(find_ngrams(segment, i+1))
                        self.reference_ngrams[sentence_id][i] |= ngrams



def find_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])
