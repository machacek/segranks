from __future__ import unicode_literals
import pickle
import math

from collections import defaultdict, Counter

LOWERCASE = True

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
            BP = math.exp(1 - float(r) / float(c))

        return BP * base_score 

    def number_of_scores(self):
        return 2*N + 1

    def set_reference_files(self, file_names):
        self.reference_ngrams = [None]
        self.reference_lengths = [None]
        for file_name in file_names:
            self.load_reference(file_name)

    def load_reference(self, file_name):
        with open(file_name, 'r') as file:
            for sentence_id, line in enumerate(file, 1):
                
                if LOWERCASE:
                    sentence = line.strip().lower().split()
                else:
                    sentence = line.strip().split()

                if len(self.reference_ngrams) == sentence_id:
                    self.reference_ngrams.append([Counter() for _ in range(N)])
                    self.reference_lengths.append(len(sentence))

                for n in range(N):
                    c = Counter(find_ngrams(sentence, n+1)) 
                    self.reference_ngrams[sentence_id][n] |= c

    def use_alignment(self):
        return False

    def load_database(self, database):
        with open(database, 'rb') as database_file:
            rank_database = pickle.load(database_file)

        self.rank_database = rank_database

        # Indexed by (sentence_id, source_segment), values are lists of expanded annotations
        self.converted_database = dict()
        for (sentence_id, source_segment), annotations in rank_database.items():
            better = dict()
            all = dict()
            for annotation in annotations:
                for cand_segment, cand_segment_rank in annotation.segment_indexed.items():
                    if cand_segment not in all:
                        all[cand_segment] = 0
                        better[cand_segment] = 0
                    for other_cand_segment_rank in annotation.system_indexed.values():
                        if cand_segment_rank.rank < other_cand_segment_rank.rank:
                            better[cand_segment] += 1
                        if cand_segment_rank.rank != other_cand_segment_rank.rank:
                            all[cand_segment] += 1

            # Indexed by candidate segments, values are tuples (better, all)
            cand_segment_better_all_counts = dict()
            for cand_segment in all:
                cand_segment_better_all_counts[cand_segment] = (better[cand_segment], all[cand_segment])
            self.converted_database[sentence_id, source_segment] = cand_segment_better_all_counts

def find_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])
