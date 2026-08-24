import json
import os
import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import WebsiteAudit  # <--- IMPORTED YOUR MODEL HERE

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
    get_score_status,
)


# ============================================================
# CONFIGURATION
# ============================================================

SCORE_WEIGHTS = {
    "seo": 30,
    "technical_seo": 20,
    "accessibility": 15,
    "performance": 20,
    "security": 15,
}

REQUEST_TIMEOUT = 20

USER_AGENT = "AI-Website-Auditor/3.0"

REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
}


# ============================================================
# BASIC VIEWS
# ============================================================

def backend_home(request):
    return render(request, "index.html")


def health_check(request):
    """
    Basic API health check.
    """

    ollama_url = os.environ.get(
        "OLLAMA_URL",
        "http://127.0.0.1:11434",
    )

    ollama_model = os.environ.get(
        "OLLAMA_MODEL",
        "qwen2.5:7b",
    )

    return JsonResponse({
        "status": "success",
        "message": "AI Website Auditor API is running.",
        "version": "3.0.0",
        "ai_enabled": True,
        "ollama_url": ollama_url,
        "ollama_model": ollama_model,
    })


# ============================================================
# URL HELPERS
# ============================================================

def normalize_url(value):
    """
    Normalize and validate a website URL.
    """

    value = (value or "").strip()

    if not value:
        return None

    if not value.startswith(("http://", "https://")):
        value = "https://" + value

    parsed = urlparse(value)

    if parsed.scheme not in ("http", "https"):
        return None

    if not parsed.netloc:
        return None

    return value


def request_payload(request):
    """
    Extract website URL from GET or POST request.
    """

    if request.method == "GET":
        return (
            request.GET.get("url")
            or request.GET.get("website")
        )

    try:
        body = json.loads(
            request.body.decode("utf-8") or "{}"
        )
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None

    return (
        body.get("website")
        or body.get("url")
    )


# ============================================================
# RECOMMENDATION HELPERS
# ============================================================

def unique_recommendations(items):
    """
    Remove duplicate recommendations while preserving order.
    """

    output = []
    seen = set()

    for item in items:
        if not isinstance(item, str):
            continue

        item = item.strip()

        if item and item.lower() not in seen:
            seen.add(item.lower())
            output.append(item)

    return output


# ============================================================
# WEBSITE AUDIT
# ============================================================

@csrf_exempt
def analyze_website(request):
    """
    Analyze a website and return SEO,
    accessibility, performance, security,
    and technical SEO results.
    """

    if request.method not in ("GET", "POST"):
        return JsonResponse({
            "status": "error",
            "message": "Only GET and POST requests are allowed.",
        }, status=405)

    # --------------------------------------------------------
    # GET WEBSITE URL
    # --------------------------------------------------------

    raw_url = request_payload(request)
    url = normalize_url(raw_url)

    if not url:
        return JsonResponse({
            "status": "error",
            "message": "Please provide a valid website URL.",
        }, status=400)

    scan_id = str(uuid.uuid4())

    try:

        # ----------------------------------------------------
        # FETCH WEBSITE
        # ----------------------------------------------------

        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers=REQUEST_HEADERS,
            allow_redirects=True,
        )

        final_url = response.url

        soup = BeautifulSoup(
            response.text or "",
            "html.parser",
        )

        # ----------------------------------------------------
        # BASIC PAGE DATA
        # ----------------------------------------------------

        title_tag = soup.find("title")

        title = (
            title_tag.get_text(
                " ",
                strip=True,
            )
            if title_tag
            else ""
        )

        description_tag = soup.find(
            "meta",
            attrs={"name": "description"},
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
                "h4",
                "h5",
                "h6",
            ]
        )

        h1_count = len(
            soup.find_all("h1")
        )

        images = soup.find_all("img")

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

        # ----------------------------------------------------
        # CONTENT EXTRACTION (FOR AI SEMANTIC SCORING)
        # ----------------------------------------------------
        
        # 1. Find all paragraph tags
        paragraphs = soup.find_all("p")
        
        # 2. Extract clean text, ignoring empty paragraphs
        raw_text = " ".join([
            p.get_text(" ", strip=True) 
            for p in paragraphs 
            if p.get_text(" ", strip=True)
        ])
        
        # 3. Calculate word count
        words = raw_text.split()
        word_count = len(words)
        
        # 4. Limit text to the first 1000 words 
        # (This prevents overloading the Ollama AI with massive pages)
        extracted_text = " ".join(words[:1000])

        # ----------------------------------------------------
        # SEO ANALYSIS
        # ----------------------------------------------------

        advanced_seo = analyze_advanced_seo(
            soup,
            final_url,
        )

        robots_meta = analyze_robots_meta(
            soup
        )

        robots = check_robots_txt(
            final_url
        )

        sitemap = check_sitemap(
            final_url,
            robots,
        )

        # ----------------------------------------------------
        # LINK ANALYSIS
        # ----------------------------------------------------

        link_analysis = analyze_links(
            soup,
            final_url,
        )

        broken_links = analyze_broken_links(
            link_analysis
        )

        nofollow_links = analyze_nofollow_links(
            soup
        )

        # ----------------------------------------------------
        # OTHER ANALYSIS
        # ----------------------------------------------------

        favicon = check_favicon(
            soup,
            final_url,
        )

        language = analyze_language(
            soup
        )

        structured_data = analyze_structured_data(
            soup
        )

        mobile_readiness = analyze_mobile_readiness(
            soup
        )

        heading_structure = analyze_heading_structure(
            soup
        )

        image_analysis = analyze_images(
            soup
        )

        page_size = analyze_page_size(
            response
        )

        text_ratio = analyze_text_ratio(
            soup,
            response,
        )

        security_headers = analyze_security_headers(
            response
        )

        performance_details = analyze_performance_details(
            response
        )

        # ----------------------------------------------------
        # CALCULATE SCORES
        # ----------------------------------------------------

        seo_score, seo_recommendations = calculate_seo_score(
            title,
            description,
            h1_count,
        )

        (
            accessibility_score,
            accessibility_recommendations,
        ) = calculate_accessibility_score(
            len(images),
            len(images_without_alt),
        )

        performance_score, performance_recommendations = (
            calculate_performance_score(
                response
            )
        )

        (
            security_score,
            security_recommendations,
        ) = calculate_enhanced_security_score(
            final_url,
            security_headers,
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

        # ----------------------------------------------------
        # COLLECT RECOMMENDATIONS
        # ----------------------------------------------------

        sources = [
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

        recommendations = []

        for source in sources:
            if isinstance(source, list):
                recommendations.extend(source)

        if broken_links.get(
            "broken",
            0,
        ) > 0:
            recommendations.append(
                f"Fix {broken_links['broken']} broken link(s)."
            )

        recommendations = unique_recommendations(
            recommendations
        )

        # ----------------------------------------------------
        # OVERALL SCORE
        # ----------------------------------------------------

        overall_score = calculate_weighted_overall_score(
            seo_score=seo_score,
            technical_seo_score=technical_seo_score,
            accessibility_score=accessibility_score,
            performance_score=performance_score,
            security_score=security_score,
        )

        score_grade = get_score_grade(
            overall_score
        )

        category_scores = analyze_score_categories(
            seo_score=seo_score,
            technical_seo_score=technical_seo_score,
            accessibility_score=accessibility_score,
            performance_score=performance_score,
            security_score=security_score,
        )

        audit_summary = create_audit_summary(
            overall_score=overall_score,
            score_grade=score_grade,
            category_scores=category_scores,
            recommendations=recommendations,
        )

        # ----------------------------------------------------
        # SAVE TO POSTGRESQL 
        # ----------------------------------------------------
        audit_record = WebsiteAudit.objects.create(
            url=url,
            website=final_url,
            http_status=response.status_code,
            page_title=title,
            meta_description=description,
            heading_count=len(headings),
            h1_count=h1_count,
            image_count=len(images),
            images_without_alt=len(images_without_alt),
            link_count=len(links),
            seo_score=seo_score,
            technical_seo_score=technical_seo_score,
            accessibility_score=accessibility_score,
            security_score=security_score,
            performance_score=performance_score,
            overall_score=overall_score,
            title_length=len(title),
            description_length=len(description),
            recommendations=recommendations,
            ai_insights={}  # Starts empty until the second endpoint generates it
        )

        # ----------------------------------------------------
        # RETURN AUDIT
        # ----------------------------------------------------

        return JsonResponse(
            {
                "status": "success",
                "audit_id": audit_record.id,  # <-- NEW: Returning the DB ID
                "scan_id": scan_id,
                "analyzed_at": datetime.now(
                    timezone.utc
                ).isoformat(),

                "website": url,
                "final_url": final_url,
                "http_status": response.status_code,

                "page_title": title,
                "meta_description": description,

                "heading_count": len(headings),
                "h1_count": h1_count,

                "image_count": len(images),
                "images_without_alt": len(
                    images_without_alt
                ),

                "link_count": len(links),
                "word_count": word_count,
                "extracted_text": extracted_text,

                "seo_score": seo_score,
                "technical_seo_score": technical_seo_score,
                "accessibility_score": accessibility_score,
                "security_score": security_score,
                "performance_score": performance_score,

                "overall_score": overall_score,
                "score_grade": score_grade,

                "overall_status": get_score_status(
                    overall_score
                ),

                "category_scores": category_scores,

                "audit_summary": audit_summary,

                "score_weights": SCORE_WEIGHTS,

                "advanced_seo": advanced_seo,
                "robots_meta": robots_meta,

                "link_analysis": link_analysis,
                "broken_links": broken_links,
                "nofollow_links": nofollow_links,

                "robots_txt": robots,
                "sitemap": sitemap,

                "favicon": favicon,
                "language": language,
                "structured_data": structured_data,

                "mobile_readiness": mobile_readiness,

                "page_size": page_size,
                "text_ratio": text_ratio,

                "heading_structure": heading_structure,
                "image_analysis": image_analysis,

                "security_headers": security_headers,
                "performance_details": performance_details,

                "recommendations": recommendations,
            },
            json_dumps_params={
                "indent": 2
            },
        )

    # --------------------------------------------------------
    # WEBSITE ERRORS
    # --------------------------------------------------------

    except requests.exceptions.Timeout:

        return JsonResponse({
            "status": "error",
            "website": url,
            "message": (
                "The website took too long to respond."
            ),
        }, status=408)

    except requests.exceptions.SSLError:

        return JsonResponse({
            "status": "error",
            "website": url,
            "message": (
                "SSL certificate verification failed."
            ),
        }, status=502)

    except requests.exceptions.ConnectionError:

        return JsonResponse({
            "status": "error",
            "website": url,
            "message": (
                "Could not connect to the website."
            ),
        }, status=502)

    except requests.exceptions.RequestException as error:

        return JsonResponse({
            "status": "error",
            "website": url,
            "message": (
                "Unable to access the website."
            ),
            "details": str(error),
        }, status=502)

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


# ============================================================
# AI INSIGHTS — OLLAMA / QWEN
# ============================================================

@csrf_exempt
def ai_insights(request):
    """
    Generate AI-powered insights from an existing
    website audit using Ollama + Qwen 2.5 7B.
    """

    # --------------------------------------------------------
    # METHOD CHECK
    # --------------------------------------------------------

    if request.method != "POST":

        return JsonResponse({
            "status": "error",
            "message": (
                "Only POST requests are allowed."
            ),
        }, status=405)

    # --------------------------------------------------------
    # OLLAMA CONFIGURATION
    # --------------------------------------------------------

    ollama_url = os.environ.get(
        "OLLAMA_URL",
        "http://127.0.0.1:11434",
    ).rstrip("/")

    ollama_model = os.environ.get(
        "OLLAMA_MODEL",
        "qwen2.5:7b",
    )

    # --------------------------------------------------------
    # READ REQUEST
    # --------------------------------------------------------

    try:

        body = request.body.decode(
            "utf-8"
        ) or "{}"

        payload = json.loads(body)

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):

        return JsonResponse({
            "status": "error",
            "message": "Invalid JSON body.",
        }, status=400)

    # --------------------------------------------------------
    # VALIDATE AUDIT
    # --------------------------------------------------------

    audit = payload.get("audit")
    audit_id = payload.get("audit_id")  # <--- NEW: GET DATABASE ID

    if not isinstance(audit, dict):

        return JsonResponse({
            "status": "error",
            "message": (
                "Provide an audit object."
            ),
        }, status=400)

    # --------------------------------------------------------
    # PREPARE AUDIT DATA
    # --------------------------------------------------------

    recommendations = audit.get(
        "recommendations",
        [],
    )

    if not isinstance(
        recommendations,
        list,
    ):
        recommendations = []

    compact = {
        "website": audit.get(
            "website"
        ),

        "overall_score": audit.get(
            "overall_score"
        ),

        "score_grade": audit.get(
            "score_grade"
        ),

        "overall_status": audit.get(
            "overall_status"
        ),

        "seo_score": audit.get(
            "seo_score"
        ),

        "technical_seo_score": audit.get(
            "technical_seo_score"
        ),

        "accessibility_score": audit.get(
            "accessibility_score"
        ),

        "security_score": audit.get(
            "security_score"
        ),

        "performance_score": audit.get(
            "performance_score"
        ),

        "recommendations": recommendations[:20],
    }

    # --------------------------------------------------------
    # AI PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are a senior technical SEO, accessibility,
security, and web-performance consultant.

Analyze the website audit data below.

Return ONLY valid JSON.

Do not use Markdown.
Do not use ```json.
Do not add explanations outside the JSON object.

The JSON must contain exactly these top-level keys:

summary
priority_actions
seo_explanation
technical_explanation
performance_explanation
accessibility_explanation
security_explanation

The "summary" value must be a concise explanation
of the website's overall condition.

"priority_actions" must be an array of objects.

Every priority_actions object must contain:

priority
issue
why_it_matters
action

"priority" must be one of:

high
medium
low

Use only information supported by the audit data.

Do not invent measurements, problems, scores,
URLs, or technical details that are not present
in the audit data.

Audit data:

{json.dumps(
    compact,
    ensure_ascii=False,
    indent=2
)}
""".strip()

    # --------------------------------------------------------
    # OLLAMA REQUEST
    # --------------------------------------------------------

    ollama_endpoint = (
        f"{ollama_url}/api/generate"
    )

    ollama_payload = {
        "model": ollama_model,
        "prompt": prompt,
        "stream": False,
        "format": "json",

        "options": {
            "temperature": 0.2,
        },
    }

    try:

        result = requests.post(
            ollama_endpoint,
            json=ollama_payload,
            timeout=300, # <--- NEW: INCREASED TIMEOUT TO 300 SECONDS
        )

    # --------------------------------------------------------
    # OLLAMA CONNECTION ERROR
    # --------------------------------------------------------

    except requests.exceptions.ConnectionError as error:

        return JsonResponse({
            "status": "unavailable",
            "provider": "ollama",
            "model": ollama_model,

            "message": (
                "Django could not connect to Ollama. "
                f"Make sure Ollama is running at "
                f"{ollama_url}."
            ),

            "details": str(error),
        }, status=503)

    # --------------------------------------------------------
    # OLLAMA TIMEOUT
    # --------------------------------------------------------

    except requests.exceptions.Timeout as error:

        return JsonResponse({
            "status": "unavailable",
            "provider": "ollama",
            "model": ollama_model,

            "message": (
                "Ollama took too long to generate "
                "the AI insights."
            ),

            "details": str(error),
        }, status=504)

    # --------------------------------------------------------
    # OTHER REQUEST ERROR
    # --------------------------------------------------------

    except requests.exceptions.RequestException as error:

        return JsonResponse({
            "status": "unavailable",
            "provider": "ollama",
            "model": ollama_model,

            "message": (
                "The request to Ollama failed."
            ),

            "details": str(error),
        }, status=503)

    # --------------------------------------------------------
    # CHECK OLLAMA HTTP STATUS
    # --------------------------------------------------------

    if not result.ok:

        return JsonResponse({
            "status": "error",
            "provider": "ollama",
            "model": ollama_model,

            "message": (
                "Ollama returned an error."
            ),

            "ollama_status": result.status_code,

            "details": result.text[:2000],
        }, status=502)

    # --------------------------------------------------------
    # PARSE OLLAMA RESPONSE
    # --------------------------------------------------------

    try:

        response_body = result.json()

    except ValueError:

        return JsonResponse({
            "status": "error",
            "provider": "ollama",
            "model": ollama_model,

            "message": (
                "Ollama returned an invalid JSON response."
            ),

            "details": result.text[:2000],
        }, status=502)

    # --------------------------------------------------------
    # GET MODEL RESPONSE
    # --------------------------------------------------------

    raw_response = response_body.get(
        "response"
    )

    if not raw_response:

        return JsonResponse({
            "status": "error",
            "provider": "ollama",
            "model": ollama_model,

            "message": (
                "Ollama returned an empty AI response."
            ),

            "details": response_body,
        }, status=502)

    # --------------------------------------------------------
    # CLEAN RESPONSE
    # --------------------------------------------------------

    raw_response = raw_response.strip()

    # Handle ```json ... ```
    if raw_response.startswith(
        "```json"
    ):

        raw_response = raw_response[
            7:
        ]

    # Handle ``` ... ```
    elif raw_response.startswith(
        "```"
    ):

        raw_response = raw_response[
            3:
        ]

    if raw_response.endswith(
        "```"
    ):

        raw_response = raw_response[
            :-3
        ]

    raw_response = raw_response.strip()

    # --------------------------------------------------------
    # PARSE AI JSON
    # --------------------------------------------------------

    try:

        insights = json.loads(
            raw_response
        )

    except json.JSONDecodeError:

        return JsonResponse({
            "status": "error",
            "provider": "ollama",
            "model": ollama_model,

            "message": (
                "Ollama responded successfully, "
                "but the AI response was not valid JSON."
            ),

            "raw_response": raw_response[:5000],
        }, status=502)

    # --------------------------------------------------------
    # VALIDATE AI STRUCTURE
    # --------------------------------------------------------

    if not isinstance(
        insights,
        dict,
    ):

        return JsonResponse({
            "status": "error",
            "provider": "ollama",
            "model": ollama_model,

            "message": (
                "The AI response must be a JSON object."
            ),

            "raw_response": raw_response[:5000],
        }, status=502)

    # --------------------------------------------------------
    # SAVE INSIGHTS TO DATABASE
    # --------------------------------------------------------
    if audit_id:
        try:
            record = WebsiteAudit.objects.get(id=audit_id)
            record.ai_insights = insights
            record.save()
        except WebsiteAudit.DoesNotExist:
            pass  # Fails gracefully if the ID doesn't exist

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    return JsonResponse({
        "status": "success",
        "provider": "ollama",
        "model": ollama_model,
        "insights": insights,
    })