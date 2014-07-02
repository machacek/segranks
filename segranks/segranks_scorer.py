class Scorer(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            print "%s=%s" % (key, value)

    def prepare_stats(self, sentence_id, sentence):
        return (1,2)
    
    def calculate_score(self, comps):
        return float(comps[0]) / comps[1]

    def number_of_scores(self):
        return 2
