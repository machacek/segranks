from __future__ import unicode_literals
import pickle

from collections import defaultdict, Counter

class Scorer(object):
    def __init__(self, database, **kwargs):
        self.database_file = database

    def prepare_stats(self, sentence_id, sentence, alignment=None):
        sentence_id += 1
    
    def calculate_score(self, comps):
        pass

    def number_of_scores(self):
        pass

    def set_reference_files(self, file_names):
        pass

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

