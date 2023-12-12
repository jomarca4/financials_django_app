from django.contrib.sitemaps import Sitemap
from .models import Post  # Replace with your actual blog post model

class BlogSitemap(Sitemap):
    changefreq = "monthly"  # How frequently page content is likely to change
    priority = 0.8          # Priority of this page in your website (0-1)

    def items(self):
        return Post.objects.all()  # Queryset of your blog posts

    def lastmod(self, obj):
        return obj.updated_at  # Replace 'modified' with your model's last modified date field