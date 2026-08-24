from django.db import models


class WebsiteAudit(models.Model):
    url = models.URLField(max_length=2048)

    website = models.CharField(max_length=2048, blank=True, default="")
    http_status = models.PositiveIntegerField(null=True, blank=True)

    page_title = models.TextField(blank=True, default="")
    meta_description = models.TextField(blank=True, default="")

    heading_count = models.PositiveIntegerField(default=0)
    h1_count = models.PositiveIntegerField(default=0)

    image_count = models.PositiveIntegerField(default=0)
    images_without_alt = models.PositiveIntegerField(default=0)
    link_count = models.PositiveIntegerField(default=0)

    seo_score = models.FloatField(default=0)
    technical_seo_score = models.FloatField(default=0)
    accessibility_score = models.FloatField(default=0)
    security_score = models.FloatField(default=0)
    performance_score = models.FloatField(default=0)
    overall_score = models.FloatField(default=0)

    advanced_seo_score = models.FloatField(default=0)

    title_length = models.PositiveIntegerField(default=0)
    description_length = models.PositiveIntegerField(default=0)

    canonical_url = models.TextField(null=True, blank=True)
    viewport = models.TextField(blank=True, default="")

    og_title = models.BooleanField(default=False)
    og_description = models.BooleanField(default=False)
    og_image = models.BooleanField(default=False)

    recommendations = models.JSONField(default=list, blank=True)

    ai_insights = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.url} - {self.overall_score}/100"