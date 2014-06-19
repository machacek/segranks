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

        compute_P_E(project)
        compute_reward_per_annotation(project)

        print(tabulate(
            tabular_data = statistics(project),
            tablefmt = 'plain',
            headers = 'firstrow'
        ))

def statistics(project):
    yield "name", "e-mail", "sentences", "annotations", "time", "reward/Kc", "annotatin-time", "kappa-intra", "kappa-inter"
    for user in User.objects.all():
        annotated = Sentence.annotated_by_me(project, user).count()

        if annotated == 0:
            continue

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
            time_avg = int(times['avg'])
        except:
            time_sum, time_avg = None, None

        reward = int(annotations * reward_per_annotation)

        yield user.username, user.email, annotated, annotations, time_sum, reward, time_avg, intra_agreement(project, user), inter_agreement(project, user)
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
        time_avg = int(times['avg'])
    except:
        time_sum, time_avg = None, None

    reward = int(annotations * reward_per_annotation)

    return "total", None, annotated, annotations, time_sum, reward, time_avg, intra_kappa, inter_kappa

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



P_E = None        
def compute_P_E(project):
    equal = 0
    unequal = 0
    for annotation in Annotation.objects.filter(annotated_segment__sentence__project=project):
        for rank1, rank2 in combinations(annotation.ranks, 2):
            if rank1 == rank2:
                equal += 1
            else:
                unequal += 1
    
    prob_equal = equal / (equal + unequal)
    prob_better = (unequal / 2) / (equal + unequal)
    prob_worse = prob_better
    global P_E
    P_E = prob_equal**2 + prob_better**2 + prob_worse**2
    print("P(E) = ", P_E)

average_reward_per_hour = 150
reward_per_annotation = None
def compute_reward_per_annotation(project):
    avg_time_per_annotation = Annotation.objects\
            .filter(annotated_segment__sentence__project=project, time_in_seconds__lt=600)\
            .aggregate(avg=Avg('time_in_seconds'))['avg']
    global reward_per_annotation
    reward_per_annotation = avg_time_per_annotation * average_reward_per_hour / 3600
    print("Annotation cost: %.2f Kc" % reward_per_annotation)



def kappa(agree, all):
    try:
        P_A = agree / all
        return (P_A - P_E) / (1 - P_E)
    except ZeroDivisionError:
        return None

def safe_div(nominator, denominator):
    try:
        return nominator / denominator
    except ZeroDivisionError:
        return None
