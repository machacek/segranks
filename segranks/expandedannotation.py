from __future__ import unicode_literals, print_function
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

    def better_worse_without_fuzzy(self, system):
        from edit_distance import edit_distance
        
        distance = 0
        rank_cmp = 0
        comparisons = []

        try:
            original_rank = self.system_indexed[system].rank

            system_segment = self.system_indexed[system].segment
            system_indexed_copy = dict(self.system_indexed)
            del system_indexed_copy[system]
            closest_system = min(system_indexed_copy, key=lambda x: edit_distance(system_segment, system_indexed_copy[x].segment))
            closest_rank = system_indexed_copy[closest_system].rank
            system_indexed_copy[system] = SegmentRank(segment=system_segment, rank=closest_rank)


            closest_segment = system_indexed_copy[closest_system].segment
            distance = edit_distance(system_segment, closest_segment)

            rank_cmp = cmp(closest_rank, original_rank)
            #if closest_segment != system_segment:
            #    comp = "\\better{}" if closest_rank < original_rank else "\\worse{}" if closest_rank > original_rank else "\\equal{}"
            #    print(system_segment.encode('utf-8'), "&", closest_segment.encode('utf-8'), "&", distance, "&", comp, "\\\\")
            


            for system1, segment_rank1 in system_indexed_copy.items():
                for system2, segment_rank2 in system_indexed_copy.items():
                    if segment_rank1.rank < segment_rank2.rank:
                        comparisons.append((system1, system2))


        except KeyError:
            #print("KeyError")
            pass
        except ValueError:
            #print("ValueError")
            pass

        rank_cmp = -1 if rank_cmp < 0 else 1 if rank_cmp > 0 else 0
        return rank_cmp, distance, comparisons
        
        

    
