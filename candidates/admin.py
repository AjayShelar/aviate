from django.contrib import admin

from .models import Candidate

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'gender', 'email', 'phone_number')
    
    list_filter = ('gender', 'age')
    
    search_fields = ('name', 'email', 'phone_number')
    
    list_display_links = ('name', 'email')
    
    ordering = ('name',)