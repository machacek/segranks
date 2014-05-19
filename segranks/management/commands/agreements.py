from __future__ import print_function, division
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from segranks.models import RankProject, Sentence, Segment
from itertools import count, groupby, combinations
from collections import namedtuple
from tabulate import tabulate
import codecs
import sys

sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

class Command(BaseCommand):
    args = 'project_name'
    help = 'Exports annotations to tsv format'

    def handle(self, *args, **options):
        project = RankProject.objects.get(pk=int(args[0]))

        print(tabulate(
            tabular_data = user_statistics(project),
            tablefmt = 'plain',
            headers = 'firstrow'
        ))

def user_statistics(project):
    yield "name", "annotated", "rate-intra", "agr-intra", "rate-inter", "agr-inter"
    for user in User.objects.all():
        annotated = Sentence.annotated_by_me(project, user).count()
        annotated_inter = Sentence.annotated_by_me_and_others(project, user).count()
        annotated_intra = Sentence.annotated_by_me_at_least_twice(project, user).count()
        yield user.username, annotated, annotated_intra/annotated, intra_agreement(project, user), annotated_inter/annotated, inter_agreement(project, user)

def inter_agreement(project, user):
    agree, all = 0, 0
    for sentence in Sentence.annotated_by_me_and_others(project, user):
        for segment in sentence.segments.all():
            for my_annot in segment.annotations.filter(annotator=user):
                for their_annot in segment.annotations.exclude(annotator=user):
                    agree_inc, all_inc = agrees_all(my_annot, their_annot)
                    agree += agree_inc
                    all += all_inc
    return kappa(agree, all)

def intra_agreement(project, user):
    agree, all = 0, 0
    return kappa(agree, all)

def agrees_all(annot_1, annot_2):
    all = 0
    agree = 0
    assert len(annot_1.ranks) == len(annot_2.ranks)
    for cand_a_idx, cand_b_idx in combinations(range(len(annot_1.ranks)), 2):
        annot_1_cmp = cmp(annot_1.ranks[cand_a_idx], annot_1.ranks[cand_b_idx])
        annot_2_cmp = cmp(annot_2.ranks[cand_a_idx], annot_2.ranks[cand_b_idx])
        if annot_1_cmp == annot_2_cmp:
            agree += 1
        all += 1
    return agree, all
        
def kappa(agree, all):
    try:
        P_A = agree / all
        P_E = 1/3 # is it?
        return (P_A - P_E) / (1 - P_E)
    except ZeroDivisionError:
        return None
