from django.urls import path

from . import api_views


urlpatterns = [
    path(
        "dpcfam/metaclusters/",
        api_views.dpcfam_metaclusters,
        name="api_dpcfam_metaclusters",
    ),
    path(
        "dpcfam/metaclusters/<str:mcid>/",
        api_views.dpcfam_metacluster_detail,
        name="api_dpcfam_metacluster_detail",
    ),
    path(
        "dpcstruct/metaclusters/",
        api_views.dpcstruct_metaclusters,
        name="api_dpcstruct_metaclusters",
    ),
    path(
        "dpcstruct/metaclusters/<str:mcid>/",
        api_views.dpcstruct_metacluster_detail,
        name="api_dpcstruct_metacluster_detail",
    ),
    path("pfam/<str:pfam_id>/", api_views.pfam_detail, name="api_pfam_detail"),
]
