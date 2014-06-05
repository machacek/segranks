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
        except:
            return False

