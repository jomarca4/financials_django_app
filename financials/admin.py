from django.contrib import admin

# Register your models here.
from .models import Section, Tag, Post, Comment,companies, quarters, financial_statements, market_data, financial_statement_items,financial_ratios,analyst_estimates

admin.site.register(companies)
admin.site.register(quarters)
admin.site.register(market_data)
admin.site.register(financial_statements)
admin.site.register(financial_statement_items)
admin.site.register(Section)
admin.site.register(Tag)
# Register other models similarly

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    list_filter = ('created_at', 'section')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    # Updated fields attribute
    fields = ['title', 'author', 'first_paragraph', 'img_url', 'content', 'section', 'slug']
    # Exclude auto-generated fields from the form
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
    search_fields = ('post', 'content')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)