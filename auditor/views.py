import uuid
import requests

from datetime import datetime, timezone

from bs4 import BeautifulSoup

from django.http import JsonResponse

from django.shortcuts import render

from .scoring import (
    analyze_advanced_seo,
    analyze_broken_links,
    analyze_heading_structure,
    analyze_images,
    analyze_language,
    analyze_links,
    analyze_mobile_readiness,
    analyze_nofollow_links,
    analyze_page_size,
    analyze_performance_details,
    analyze_robots_meta,
    analyze_score_categories,
    analyze_security_headers,
    analyze_structured_data,
    analyze_text_ratio,

    calculate_accessibility_score,
    calculate_enhanced_security_score,
    calculate_performance_score,
    calculate_seo_score,
    calculate_technical_seo_score,
    calculate_weighted_overall_score,

    check_favicon,
    check_robots_txt,
    check_sitemap,

    create_audit_summary,
    get_score_grade,
)


# ============================================================
# SCORE WEIGHTS
# ============================================================

SCORE_WEIGHTS = {
    "seo": 30,
    "technical_seo": 20,
    "accessibility": 15,
    "performance": 20,
    "security": 15,
}

from django.shortcuts import render

def backend_home(request):
    return render(request, 'index.html')




# ============================================================
# HEALTH CHECK
# ============================================================

def health_check(request):

    return JsonResponse({
        "status": "success",

        "message": (
            "AI Website Auditor API is running!"
        ),

        "version": "2.0.0",
    })


# ============================================================
# WEBSITE ANALYZER
# ============================================================

def analyze_website(request):

    if request.method != "GET":

        return JsonResponse({

            "status": "error",

            "message": (
                "Only GET requests are allowed."
            ),

        }, status=405)

    url = request.GET.get("url")

    if not url:

        return JsonResponse({

            "status": "error",

            "message": (
                "Please provide a website URL."
            ),

        }, status=400)

    url = url.strip()

    if not url.startswith(
        (
            "http://",
            "https://",
        )
    ):

        url = "https://" + url

    scan_id = str(
        uuid.uuid4()
    )

    try:

        # ====================================================
        # FETCH
        # ====================================================

        response = requests.get(

            url,

            timeout=15,

            headers={
                "User-Agent":
                "AI-Website-Auditor/2.0"
            },

            allow_redirects=True,
        )

        final_url = response.url

        # ====================================================
        # PARSE
        # ====================================================

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        # ====================================================
        # BASIC INFORMATION
        # ====================================================

        title_tag = soup.find(
            "title"
        )

        title = (
            title_tag.get_text(
                strip=True
            )
            if title_tag
            else ""
        )

        description_tag = soup.find(
            "meta",
            attrs={
                "name": "description"
            },
        )

        description = (
            description_tag.get(
                "content",
                "",
            ).strip()
            if description_tag
            else ""
        )

        headings = soup.find_all(
            [
                "h1",
                "h2",
                "h3",
            ]
        )

        h1_count = len(
            soup.find_all("h1")
        )

        images = soup.find_all(
            "img"
        )

        images_without_alt = [

            image

            for image in images

            if (
                image.get("alt") is None
                or not image.get(
                    "alt",
                    "",
                ).strip()
            )
        ]

        links = soup.find_all(
            "a",
            href=True,
        )

        # ====================================================
        # ADVANCED SEO
        # ====================================================

        advanced_seo = (
            analyze_advanced_seo(
                soup,
                final_url,
            )
        )

        # ====================================================
        # ROBOTS
        # ====================================================

        robots_meta = (
            analyze_robots_meta(
                soup
            )
        )

        robots = check_robots_txt(
            final_url
        )

        sitemap = check_sitemap(
            final_url,
            robots,
        )

        # ====================================================
        # LINKS
        # ====================================================

        link_analysis = analyze_links(
            soup,
            final_url,
        )

        broken_links = (
            analyze_broken_links(
                link_analysis
            )
        )

        nofollow_links = (
            analyze_nofollow_links(
                soup
            )
        )

        # ====================================================
        # TECHNICAL
        # ====================================================

        favicon = check_favicon(
            soup,
            final_url,
        )

        language = analyze_language(
            soup
        )

        structured_data = (
            analyze_structured_data(
                soup
            )
        )

        mobile_readiness = (
            analyze_mobile_readiness(
                soup
            )
        )

        heading_structure = (
            analyze_heading_structure(
                soup
            )
        )

        image_analysis = (
            analyze_images(
                soup
            )
        )

        # ====================================================
        # SIZE / CONTENT
        # ====================================================

        page_size = (
            analyze_page_size(
                response
            )
        )

        text_ratio = (
            analyze_text_ratio(
                soup,
                response,
            )
        )

        # ====================================================
        # SECURITY
        # ====================================================

        security_headers = (
            analyze_security_headers(
                response
            )
        )

        # ====================================================
        # PERFORMANCE
        # ====================================================

        performance_details = (
            analyze_performance_details(
                response
            )
        )

        # ====================================================
        # SCORES
        # ====================================================

        seo_score, seo_recommendations = (
            calculate_seo_score(
                title,
                description,
                h1_count,
            )
        )

        accessibility_score, accessibility_recommendations = (
            calculate_accessibility_score(
                len(images),
                len(images_without_alt),
            )
        )

        performance_score, performance_recommendations = (
            calculate_performance_score(
                response
            )
        )

        security_score, security_recommendations = (
            calculate_enhanced_security_score(
                final_url,
                security_headers,
            )
        )

        technical_seo_score = (
            calculate_technical_seo_score(
                advanced_seo,
                favicon,
                language,
                structured_data,
                mobile_readiness,
                robots,
                sitemap,
                robots_meta,
            )
        )

        # ====================================================
        # RECOMMENDATIONS
        # ====================================================

        recommendations = []

        recommendation_sources = [

            seo_recommendations,

            accessibility_recommendations,

            performance_recommendations,

            security_recommendations,

            advanced_seo.get(
                "recommendations",
                [],
            ),

            robots_meta.get(
                "recommendations",
                [],
            ),

            robots.get(
                "recommendations",
                [],
            ),

            sitemap.get(
                "recommendations",
                [],
            ),

            favicon.get(
                "recommendations",
                [],
            ),

            language.get(
                "recommendations",
                [],
            ),

            structured_data.get(
                "recommendations",
                [],
            ),

            mobile_readiness.get(
                "recommendations",
                [],
            ),

            page_size.get(
                "recommendations",
                [],
            ),

            text_ratio.get(
                "recommendations",
                [],
            ),

            heading_structure.get(
                "recommendations",
                [],
            ),

            image_analysis.get(
                "recommendations",
                [],
            ),

            security_headers.get(
                "recommendations",
                [],
            ),

            performance_details.get(
                "recommendations",
                [],
            ),
        ]

        for source in recommendation_sources:

            recommendations.extend(
                source
            )

        if broken_links["broken"] > 0:

            recommendations.append(
                f"Fix {broken_links['broken']} broken link(s)."
            )

        recommendations = list(
            dict.fromkeys(
                recommendation.strip()
                for recommendation
                in recommendations
                if recommendation
                and recommendation.strip()
            )
        )

        # ====================================================
        # OVERALL SCORE
        # ====================================================

        overall_score = (
            calculate_weighted_overall_score(

                seo_score=seo_score,

                technical_seo_score=(
                    technical_seo_score
                ),

                accessibility_score=(
                    accessibility_score
                ),

                performance_score=(
                    performance_score
                ),

                security_score=(
                    security_score
                ),
            )
        )

        score_grade = get_score_grade(
            overall_score
        )

        category_scores = (
            analyze_score_categories(

                seo_score=seo_score,

                technical_seo_score=(
                    technical_seo_score
                ),

                accessibility_score=(
                    accessibility_score
                ),

                performance_score=(
                    performance_score
                ),

                security_score=(
                    security_score
                ),
            )
        )

        audit_summary = (
            create_audit_summary(

                overall_score=(
                    overall_score
                ),

                score_grade=(
                    score_grade
                ),

                category_scores=(
                    category_scores
                ),

                recommendations=(
                    recommendations
                ),
            )
        )

        # ====================================================
        # DASHBOARD SUMMARY
        # ====================================================

        dashboard = {

            "score": overall_score,

            "grade": score_grade,

            "priority": audit_summary[
                "priority"
            ],

            "strongest_category": (
                audit_summary[
                    "strongest_category"
                ]
            ),

            "weakest_category": (
                audit_summary[
                    "weakest_category"
                ]
            ),

            "recommendation_count": len(
                recommendations
            ),

            "categories": {
                category: {
                    "score": data["score"],
                    "status": data["status"],
                    "weight": data["weight"],
                }

                for category, data
                in category_scores.items()
            },
        }

        # ====================================================
        # RESPONSE
        # ====================================================

        return JsonResponse({

            "status": "success",

            "scan_id": scan_id,

            "analyzed_at": (
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),

            "website": url,

            "final_url": final_url,

            "http_status": (
                response.status_code
            ),

            "page_title": title,

            "meta_description": description,

            # Counts
            "heading_count": len(
                headings
            ),

            "h1_count": h1_count,

            "image_count": len(
                images
            ),

            "images_without_alt": len(
                images_without_alt
            ),

            "link_count": len(
                links
            ),

            # Scores
            "seo_score": seo_score,

            "technical_seo_score": (
                technical_seo_score
            ),

            "accessibility_score": (
                accessibility_score
            ),

            "security_score": (
                security_score
            ),

            "performance_score": (
                performance_score
            ),

            "overall_score": (
                overall_score
            ),

            "score_grade": score_grade,

            "category_scores": (
                category_scores
            ),

            "audit_summary": (
                audit_summary
            ),

            "dashboard": dashboard,

            "score_weights": (
                SCORE_WEIGHTS
            ),

            # SEO
            "advanced_seo": (
                advanced_seo
            ),

            "robots_meta": (
                robots_meta
            ),

            # Links
            "link_analysis": (
                link_analysis
            ),

            "broken_links": (
                broken_links
            ),

            "nofollow_links": (
                nofollow_links
            ),

            # Technical
            "robots_txt": robots,

            "sitemap": sitemap,

            "favicon": favicon,

            "language": language,

            "structured_data": (
                structured_data
            ),

            "mobile_readiness": (
                mobile_readiness
            ),

            # Content
            "page_size": page_size,

            "text_ratio": text_ratio,

            "heading_structure": (
                heading_structure
            ),

            "image_analysis": (
                image_analysis
            ),

            # Security
            "security_headers": (
                security_headers
            ),

            # Performance
            "performance_details": (
                performance_details
            ),

            # Recommendations
            "recommendations": (
                recommendations
            ),
        })

    # ========================================================
    # REQUEST ERROR
    # ========================================================

    except requests.exceptions.RequestException as error:

        return JsonResponse({

            "status": "error",

            "website": url,

            "message": (
                "Unable to access the website."
            ),

            "details": str(error),

        }, status=400)

    # ========================================================
    # UNEXPECTED ERROR
    # ========================================================

    except Exception as error:

        return JsonResponse({

            "status": "error",

            "website": url,

            "message": (
                "An unexpected error occurred "
                "while analyzing the website."
            ),

            "details": str(error),

        }, status=500)

    from django.shortcuts import render

    def dashboard(request):
        return render(
        request,
        "dashboard/index.html",
    )