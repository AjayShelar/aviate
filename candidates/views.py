from django.shortcuts import render

# Create your views here.
from rest_framework import generics, views, status
from rest_framework.response import Response
from django.db.models import Q, Case, When, Value, IntegerField, Sum
from functools import reduce
from operator import or_
from django.db.models.functions import Lower
from .models import Candidate
from .serializers import CandidateSerializer
from .pagination import CandidatePagination
from rest_framework.exceptions import ValidationError
from .serializers import CandidateSearchSerializer
from .pagination import CandidatePagination
from .models import Candidate
from .serializers import CandidateSerializer
from .utils import format_error_response
    
from django.db.models import F, Value, IntegerField, ExpressionWrapper
from django.db.models.functions import Concat




class CandidateCreateView(generics.CreateAPIView):
    """
      create a single candidate.
    """
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer

    def create(self, request, *args, **kwargs):
        """
        Override create method to handle single candidate creation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Validate input
        self.perform_create(serializer)  # Save candidate instance
        return Response(serializer.data, status=status.HTTP_201_CREATED)




class CandidateUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer



class CandidateSearchView(views.APIView):
    """
    API View to search candidates with relevancy sorting.
    """
    def get(self, request):
        # Step 1: Validate query parameters
        search_serializer = CandidateSearchSerializer(data=request.query_params)
        search_serializer.is_valid(raise_exception=True)
        validated_data = search_serializer.validated_data

        # Extract query, page, and page_size separately
        query = validated_data.get("q", "").strip()
        page = validated_data.get("page")
        page_size = validated_data.get("page_size")


        # Step 2: Perform search and relevancy filtering
        queryset = self.perform_search(query)

        # Step 3: Apply pagination
        paginator = CandidatePagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # Step 4: Serialize and return the results
        serializer = CandidateSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)



    def perform_search(self, query):
        """
        Handles search and relevancy scoring logic for candidates.
        """
        queryset = Candidate.objects.all()

        if not query:
            return queryset

        search_terms = query.split()
        # Build relevancy conditions for each term
        conditions = [
            Case(
                When(name__icontains=term, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
            for term in search_terms
        ]

        # Calculate relevancy score by summing up the conditions
        relevancy_annotation = sum(conditions)

        # Annotate queryset with the relevancy score and order by it
        return queryset.annotate(relevancy=relevancy_annotation).order_by('-relevancy')
