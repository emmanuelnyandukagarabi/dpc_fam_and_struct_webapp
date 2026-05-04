import re

from django.core.paginator import EmptyPage, Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse

from dpc.models import DpcPfamDomain
from dpcfam.models import DpcfamAlphaFoldRep, DpcfamMcsProperty
from dpcstruct.models import (
    DpcStructCath,
    DpcStructMcsProperty,
    DpcStructScop,
)


DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100


def _page_size(request):
    try:
        requested = int(request.GET.get("page_size", DEFAULT_PAGE_SIZE))
    except (TypeError, ValueError):
        requested = DEFAULT_PAGE_SIZE
    return min(max(requested, 1), MAX_PAGE_SIZE)


def _paginated_response(request, queryset, serializer):
    paginator = Paginator(queryset, _page_size(request))
    try:
        page_number = int(request.GET.get("page", 1))
    except (TypeError, ValueError):
        page_number = 1

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages or 1)

    return {
        "count": paginator.count,
        "page": page_obj.number,
        "page_size": paginator.per_page,
        "total_pages": paginator.num_pages,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "results": [serializer(obj, request=request) for obj in page_obj.object_list],
    }


def _split_pfam_architecture(pfam_da):
    if not pfam_da or pfam_da == "UNKNOWN":
        return []
    return [pfam.strip() for pfam in pfam_da.split("-") if pfam.strip()]


def _absolute_url(request, view_name, *args):
    return request.build_absolute_uri(reverse(view_name, args=args))


def _dpcfam_metacluster_summary(mc, request=None):
    data = {
        "mcid": mc.mcid,
        "size_uniref50": mc.size_uniref50,
        "avg_len": mc.avg_len,
        "std_avg_len": mc.std_avg_len,
        "lc_percent": mc.lc_percent,
        "cc_percent": mc.cc_percent,
        "dis_percent": mc.dis_percent,
        "tm": mc.tm,
        "pfam_da": mc.pfam_da,
        "pfam_architecture": _split_pfam_architecture(mc.pfam_da),
        "da_percent": mc.da_percent,
        "avg_ov_percent": mc.avg_ov_percent,
        "overlap_label": mc.overlap_label,
    }
    if request:
        data["url"] = _absolute_url(request, "api_dpcfam_metacluster_detail", mc.mcid)
    return data


def _dpcfam_sequence(sequence, request=None):
    return {
        "id": sequence.id,
        "protein_id": sequence.protein_id,
        "seq_range": sequence.seq_range,
        "seq_length": sequence.seq_length,
        "aa_seq": sequence.aa_seq,
    }


def _dpcfam_alphafold(alphafold):
    return {
        "id": alphafold.id,
        "alphafold_prot": alphafold.alphafold_prot,
        "seq_range": alphafold.seq_range,
        "hmm_coverage": alphafold.hmm_coverage,
        "avg_plddt": alphafold.avg_plddt,
    }


def _dpcstruct_metacluster_summary(mc, request=None):
    data = {
        "mc_id": mc.mc_id,
        "mc_size": mc.mc_size,
        "len_aa": mc.len_aa,
        "len_std": mc.len_std,
        "len_ratio": mc.len_ratio,
        "plddt": mc.plddt,
        "disorder": mc.disorder,
        "tmscore": mc.tmscore,
        "lddt": mc.lddt,
        "pident": mc.pident,
        "pfam_score": mc.pfam_score,
        "pfam_da": mc.pfam_da,
        "pfam_architecture": _split_pfam_architecture(mc.pfam_da),
    }
    if request:
        data["url"] = _absolute_url(request, "api_dpcstruct_metacluster_detail", mc.mc_id)
    return data


def _dpcstruct_sequence(sequence, request=None):
    return {
        "id": sequence.id,
        "protein_id": sequence.protein_id,
        "prot_range": sequence.prot_range,
        "prot_seq": sequence.prot_seq,
    }


def _dpcstruct_cath(annotation, request=None):
    return {
        "cath_query": annotation.cath_query,
        "dpc_target": annotation.dpc_target,
        "q_range": annotation.q_range,
        "t_range": annotation.t_range,
        "qlen": annotation.qlen,
        "tlen": annotation.tlen,
        "qcov": annotation.qcov,
        "tcov": annotation.tcov,
        "alnlen": annotation.alnlen,
        "qtmscore": annotation.qtmscore,
        "ttmscore": annotation.ttmscore,
        "alntmscore": annotation.alntmscore,
        "lddt": annotation.lddt,
        "pident": annotation.pident,
    }


def _dpcstruct_scop(annotation, request=None):
    return {
        "scop_query": annotation.scop_query,
        "dpc_target": annotation.dpc_target,
        "q_range": annotation.q_range,
        "t_range": annotation.t_range,
        "qlen": annotation.qlen,
        "tlen": annotation.tlen,
        "qcov": annotation.qcov,
        "tcov": annotation.tcov,
        "alnlen": annotation.alnlen,
        "qtmscore": annotation.qtmscore,
        "ttmscore": annotation.ttmscore,
        "alntmscore": annotation.alntmscore,
        "lddt": annotation.lddt,
        "pident": annotation.pident,
    }


def dpcfam_metaclusters(request):
    queryset = DpcfamMcsProperty.objects.extra(
        select={"mc_num": "CAST(SUBSTRING(mcid FROM '[0-9]+') AS INTEGER)"},
        order_by=["mc_num"],
    )

    dataset = request.GET.get("dataset")
    if dataset == "standard":
        queryset = queryset.filter(size_uniref50__gte=50)
    elif dataset == "b":
        queryset = queryset.filter(size_uniref50__lt=50)

    return JsonResponse(_paginated_response(request, queryset, _dpcfam_metacluster_summary))


def dpcfam_metacluster_detail(request, mcid):
    mc = get_object_or_404(DpcfamMcsProperty, mcid=mcid)
    sequences = mc.sequences.select_related("protein").order_by("id")
    alphafolds = DpcfamAlphaFoldRep.objects.filter(mc=mc).order_by("id")

    return JsonResponse(
        {
            "metacluster": _dpcfam_metacluster_summary(mc, request=request),
            "sequences": _paginated_response(request, sequences, _dpcfam_sequence),
            "alphafolds": [_dpcfam_alphafold(alphafold) for alphafold in alphafolds],
        }
    )


def dpcstruct_metaclusters(request):
    queryset = DpcStructMcsProperty.objects.extra(
        select={"mc_num": "CAST(SUBSTRING(mc_id FROM '[0-9]+') AS INTEGER)"}
    ).order_by("mc_num")

    search_mcid = request.GET.get("search_mcid", "").strip()
    if search_mcid:
        queryset = queryset.filter(mc_id__iexact=search_mcid)

    return JsonResponse(_paginated_response(request, queryset, _dpcstruct_metacluster_summary))


def dpcstruct_metacluster_detail(request, mcid):
    mc = get_object_or_404(DpcStructMcsProperty, mc_id=mcid)
    sequences = mc.sequences.select_related("protein").order_by("id")
    cath_annotations = DpcStructCath.objects.filter(mc=mc).order_by("cath_query")
    scop_annotations = DpcStructScop.objects.filter(mc=mc).order_by("scop_query")

    return JsonResponse(
        {
            "metacluster": _dpcstruct_metacluster_summary(mc, request=request),
            "sequences": _paginated_response(request, sequences, _dpcstruct_sequence),
            "cath_annotations": _paginated_response(request, cath_annotations, _dpcstruct_cath),
            "scop_annotations": _paginated_response(request, scop_annotations, _dpcstruct_scop),
        }
    )


def pfam_detail(request, pfam_id):
    pfam_id = pfam_id.strip().upper()
    pfam_pattern = re.escape(pfam_id)
    pfam_domain = get_object_or_404(DpcPfamDomain, pfam_id=pfam_id)

    dpcfam_matches = DpcfamMcsProperty.objects.filter(
        pfam_da__regex=rf"(^|-){pfam_pattern}(-|$)"
    ).exclude(pfam_da="UNKNOWN").extra(
        select={"mc_num": "CAST(SUBSTRING(mcid FROM '[0-9]+') AS INTEGER)"}
    ).order_by("mc_num")

    dpcstruct_matches = DpcStructMcsProperty.objects.filter(
        pfam_da__regex=rf"(^|-){pfam_pattern}(-|$)"
    ).exclude(pfam_da="UNKNOWN").extra(
        select={"mc_num": "CAST(SUBSTRING(mc_id FROM '[0-9]+') AS INTEGER)"}
    ).order_by("mc_num")

    return JsonResponse(
        {
            "pfam": {
                "pfam_id": pfam_domain.pfam_id,
                "pfam_type": pfam_domain.pfam_type,
            },
            "dpcfam_metaclusters": _paginated_response(
                request,
                dpcfam_matches,
                _dpcfam_metacluster_summary,
            ),
            "dpcstruct_metaclusters": _paginated_response(
                request,
                dpcstruct_matches,
                _dpcstruct_metacluster_summary,
            ),
        }
    )
