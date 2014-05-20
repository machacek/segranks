from __future__ import print_function, division
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from segranks.models import RankProject, Sentence, Segment, Annotation
from django.db.models import Sum, Avg
from itertools import count, groupby, combinations
from collections import namedtuple
from tabulate import tabulate
import codecs
import sys
import datetime

sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

class Command(BaseCommand):
    args = 'project_name'
    help = 'Exports annotations to tsv format'

    def handle(self, *args, **options):
        project = RankProject.objects.get(pk=int(args[0]))

        print(tabulate(
            tabular_data = statistics(project),
            tablefmt = 'plain',
            headers = 'firstrow'
        ))

def statistics(project):
    yield "name", "sentences", "annot-intra", "agree-intra", "annot-inter", "agree-inter", "annotations", "time", "per-annotation"
    for user in User.objects.all():
        annotated = Sentence.annotated_by_me(project, user).count()
        annotated_inter = Sentence.annotated_by_me_and_others(project, user).count()
        annotated_intra = Sentence.annotated_by_me_at_least_twice(project, user).count()

        annotations = Annotation.objects.filter(annotated_segment__sentence__project=project, annotator=user).count()
        times = Annotation.objects\
                .filter(annotated_segment__sentence__project=project, annotator=user, time_in_seconds__lt=600)\
                .aggregate(
                        sum=Sum('time_in_seconds'),
                        avg=Avg('time_in_seconds'),
                        )
        try:
            time_sum = str(datetime.timedelta(seconds=times['sum']))
        except:
            time_sum = None
        
        time_avg = int(times['avg'])

        yield user.username, annotated, safe_div(annotated_intra,annotated), intra_agreement(project, user), safe_div(annotated_inter,annotated), inter_agreement(project, user), annotations, time_sum, time_avg
    yield overall_statistics(project)


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
    for sentence in Sentence.annotated_by_me(project, user):
        for segment in sentence.segments.all():
            for annot_1, annot_2 in combinations(segment.annotations.filter(annotator=user), 2):
                agree_inc, all_inc = agrees_all(annot_1, annot_2)
                agree += agree_inc
                all += all_inc
    return kappa(agree, all)

def overall_statistics(project):
    annotated = Sentence.objects.filter(project=project).exclude(segments__annotations=None).distinct().count()
    intra_agree, intra_all = 0, 0
    inter_agree, inter_all = 0, 0

    for segment in Segment.objects.filter(sentence__project=project).select_related('annotations').distinct():
        for annot_1, annot_2 in combinations(segment.annotations.all(), 2):
            agree_inc, all_inc = agrees_all(annot_1, annot_2)
            if annot_1.annotator == annot_2.annotator:
                intra_agree += agree_inc
                intra_all   += all_inc
            else:
                inter_agree += agree_inc
                inter_all   += all_inc

    intra_kappa = kappa(intra_agree, intra_all)
    inter_kappa = kappa(inter_agree, inter_all)
        
    annotations = Annotation.objects.filter(annotated_segment__sentence__project=project).count()
    times = Annotation.objects\
            .filter(annotated_segment__sentence__project=project, time_in_seconds__lt=600)\
            .aggregate(
                    sum=Sum('time_in_seconds'),
                    avg=Avg('time_in_seconds'),
                    )
    try:
        time_sum = str(datetime.timedelta(seconds=times['sum']))
        time_avg = str(datetime.timedelta(seconds=times['avg']))
    except:
        time_sum, time_avg = None, None

    return "total", annotated, None, intra_kappa, None, inter_kappa, annotations, time_sum, time_avg

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

def safe_div(nominator, denominator):
    try:
        return nominator / denominator
    except ZeroDivisionError:
        return None
