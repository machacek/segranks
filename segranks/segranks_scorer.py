from __future__ import unicode_literals
import pickle
import sys

sys.path.append('/ha/home/machacek/.local/lib/python2.6/site-packages')

from nltk.align import Alignment
from collections import defaultdict, Counter

class Scorer(object):
    def __init__(self, database, source_segments, match='exact', **kwargs):
        self.load_database(database)
        self.load_source_segments(source_segments)

        assert match in ['exact', 'closest_words', 'closest_characters']
        self.match = match

        self.counter_all = 0
        self.counter_hit = 0
        self.missing_sentences = set()

        #import pprint
        #pprint.pprint(self.source_segments[39])
        # pprint.pprint(self.rank_database)
        #for (sentence_id, source_segment), value in self.rank_database.items():
        #    if sentence_id == 39:
        #        pprint.pprint(source_segment)
        #        pprint.pprint(value) 
        #raise KeyError


    def prepare_stats(self, sentence_id, sentence, alignment=None):
        sentence = sentence.split()
        alignment = Alignment(alignment)
        sentence_id += 1

        if self.match == 'exact':
            better = 0
            all = 0
            for source_segment, source_idxs in self.source_segments[sentence_id]:

                try:
                    cand_idxs = alignment.range(source_idxs)
                except IndexError:
                    print sentence_id, source_segment
                    print alignment
                    print source_idxs
                    print ""
                    continue

                cand_segment = " ".join([sentence[i] for i in cand_idxs])
                try:
                    cand_segment_better_all_counts = self.converted_database[sentence_id, source_segment]
                except KeyError:
                    self.missing_sentences.add(sentence_id)
                    continue

                try:
                    better_segment, all_segment = cand_segment_better_all_counts[cand_segment]
                    better += better_segment
                    all += all_segment
                    self.counter_hit += 1
                    self.counter_all += 1
                except KeyError:
                    self.counter_all += 1
                    # print ""
                    # print sentence_id
                    # print source_segment
                    # print cand_segment
                    # print cand_segment_better_all_counts.keys()
                    continue
            return better, all
        else:
            raise NotImplemented
    
    def calculate_score(self, comps):
        score = float(comps[0]) / comps[1]
        print "score: ", score
        return score

    def number_of_scores(self):
        return 2

    def use_alignment(self):
        return True

    def __del__(self):
        print "counter_hit: ", self.counter_hit
        print "counter_all: ", self.counter_all
        print "hit rate: ", float(self.counter_hit) / self.counter_all
        print "missing sentences: ", len(self.missing_sentences)

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

    def load_source_segments(self, source_segments):
        # indexed by sentence id, values are list of tuples (source_segment_str, source_segment_idxs
        self.source_segments = defaultdict(list) 
        with open(source_segments, 'r') as source_segments_file:
            split_lines = (line.decode('utf-8').strip().split('\t') for line in source_segments_file)
            for sentence_id, source_segment, idxs in split_lines:
                sentence_id = int(sentence_id)
                idxs = [int(item) for item in idxs.split(' ')]
                self.source_segments[sentence_id].append((source_segment, idxs))
            

    
