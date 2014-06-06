from __future__ import unicode_literals
from collections import namedtuple

SegmentRank = namedtuple("SegmentRank", ["segment", "rank"])

class ExpandedAnnotation(object):
    # __slots__ = ("sentence_id", "source_segment", "system_indexed", "segment_indexed")
    def __init__(self, sentence_id, source_segment):
        self.sentence_id = sentence_id
        self.source_segment = source_segment
        self.system_indexed = dict()
        self.segment_indexed = dict()

    def add_ranked_system_segment(self, system, segment, rank):
        segment_rank = SegmentRank(segment=segment, rank=rank) 
        self.segment_indexed[segment] = segment_rank
        self.system_indexed[system] = segment_rank

    def add_ranked_segment(self, segment, rank):
        segment_rank = SegmentRank(segment=segment, rank=rank) 
        self.segment_indexed[segment] = segment_rank
    
    def add_system_segment(self, system, segment):
        try:
            segment_rank = self.segment_indexed[segment]
            self.system_indexed[system] = segment_rank
            return True
        except KeyError:
            return False

    def better_worse_system_comparisons(self):
        for index1, (system1, segment_rank1) in enumerate(self.system_indexed.items()):
            for index2, (system2, segment_rank2) in enumerate(self.system_indexed.items()):
                if segment_rank1.rank < segment_rank2.rank:
                    yield system1, system2
    
    def better_worse_without(self, system):
        try:
            system_rank = self.system_indexed[system]
            if len(list(filter(lambda x: x==system_rank, self.system_indexed.values()))) > 1:
                return True, self.better_worse_system_comparisons()
        except KeyError:
            pass
        
        return False, []
