import requests

from urllib.parse import urljoin, urlparse


# ============================================================
# CONSTANTS
# ============================================================

USER_AGENT = "AI-Website-Auditor/2.0"

REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
}


# ============================================================
# HELPERS
# ============================================================

def get_score_status(score):
    score = int(score)

    if score >= 90:
        return "excellent"

    if score >= 80:
        return "good"

    if score >= 70:
        return "needs_improvement"

    if score >= 60:
        return "poor"

    return "critical"


def get_score_grade(score):
    score = int(score)

    if score >= 90:
        return {
            "grade": "A",
            "label": "Excellent",
        }

    if score >= 80:
        return {
            "grade": "B",
            "label": "Good",
        }

    if score >= 70:
        return {
            "grade": "C",
            "label": "Needs Improvement",
        }

    if score >= 60:
        return {
            "grade": "D",
            "label": "Poor",
        }

    return {
        "grade": "F",
        "label": "Critical",
    }


# ============================================================
# BASIC SEO SCORE
# ============================================================

def calculate_seo_score(
    title,
    description,
    h1_count,
):
    score = 0
    recommendations = []

    # Title
    if title:
        score += 35
    else:
        recommendations.append(
            "Add a page title."
        )

    # Meta description
    if description:
        score += 35
    else:
        recommendations.append(
            "Add a meta description."
        )

    # H1
    if h1_count == 1:
        score += 30

    elif h1_count == 0:
        recommendations.append(
            "Add one H1 heading."
        )

    else:
        recommendations.append(
            "Use only one H1 heading."
        )

    return score, recommendations


# ============================================================
# ACCESSIBILITY SCORE
# ============================================================

def calculate_accessibility_score(
    image_count,
    images_without_alt,
):
    if image_count == 0:
        return 100, []

    accessible_images = max(
        image_count - images_without_alt,
        0,
    )

    score = int(
        (accessible_images / image_count) * 100
    )

    recommendations = []

    if images_without_alt > 0:
        recommendations.append(
            f"Add alt text to {images_without_alt} image(s)."
        )

    return score, recommendations


# ============================================================
# BASIC SECURITY SCORE
# ============================================================

def calculate_security_score(url):
    score = 100
    recommendations = []

    if not url.lower().startswith("https://"):
        score -= 50

        recommendations.append(
            "Use HTTPS to secure communication with visitors."
        )

    return max(score, 0), recommendations


# ============================================================
# PERFORMANCE SCORE
# ============================================================

def calculate_performance_score(response):
    score = 100
    recommendations = []

    response_time = response.elapsed.total_seconds()

    if response_time > 5:
        score -= 50

        recommendations.append(
            "Website response time is very slow. "
            "Consider improving server and hosting performance."
        )

    elif response_time > 3:
        score -= 30

        recommendations.append(
            "Website response time is slow. "
            "Consider improving server performance."
        )

    elif response_time > 1.5:
        score -= 20

        recommendations.append(
            "Website response time could be improved."
        )

    return max(score, 0), recommendations


# ============================================================
# ADVANCED SEO
# ============================================================

def analyze_advanced_seo(
    soup,
    url,
):
    score = 0
    recommendations = []

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    title_tag = soup.find("title")

    if title_tag:
        title = title_tag.get_text(
            strip=True
        )

        title_length = len(title)

        if 30 <= title_length <= 60:
            score += 15

        elif title_length > 0:
            recommendations.append(
                "Keep the page title between 30 and 60 characters."
            )

    else:
        title_length = 0

        recommendations.append(
            "Add a page title."
        )

    # --------------------------------------------------------
    # META DESCRIPTION
    # --------------------------------------------------------

    description_tag = soup.find(
        "meta",
        attrs={
            "name": "description",
        },
    )

    if description_tag:

        description = description_tag.get(
            "content",
            "",
        ).strip()

        description_length = len(
            description
        )

        if 120 <= description_length <= 160:
            score += 15

        elif description_length > 0:
            recommendations.append(
                "Keep the meta description between 120 and 160 characters."
            )

        else:
            recommendations.append(
                "Add a meta description."
            )

    else:

        description_length = 0

        recommendations.append(
            "Add a meta description."
        )

    # --------------------------------------------------------
    # CANONICAL
    # --------------------------------------------------------

    canonical = soup.find(
        "link",
        attrs={
            "rel": lambda value: (
                value
                and (
                    "canonical" in value
                    if isinstance(value, list)
                    else "canonical" in str(value).lower()
                )
            )
        },
    )

    canonical_url = None
    canonical_valid = False

    if canonical:

        href = canonical.get(
            "href",
            "",
        ).strip()

        if href:

            canonical_url = urljoin(
                url,
                href,
            )

            parsed = urlparse(
                canonical_url
            )

            canonical_valid = bool(
                parsed.scheme
                and parsed.netloc
            )

    if canonical_valid:
        score += 15
    else:
        recommendations.append(
            "Add a canonical URL."
        )

    # --------------------------------------------------------
    # VIEWPORT
    # --------------------------------------------------------

    viewport = soup.find(
        "meta",
        attrs={
            "name": "viewport",
        },
    )

    viewport_content = None

    if viewport:

        viewport_content = viewport.get(
            "content",
            "",
        ).strip()

        if viewport_content:
            score += 15
        else:
            recommendations.append(
                "Add a valid viewport configuration."
            )

    else:
        recommendations.append(
            "Add a responsive viewport meta tag."
        )

    # --------------------------------------------------------
    # OPEN GRAPH
    # --------------------------------------------------------

    og_title = soup.find(
        "meta",
        attrs={
            "property": "og:title",
        },
    )

    og_description = soup.find(
        "meta",
        attrs={
            "property": "og:description",
        },
    )

    og_image = soup.find(
        "meta",
        attrs={
            "property": "og:image",
        },
    )

    if og_title and og_title.get("content"):
        score += 10
    else:
        recommendations.append(
            "Add an Open Graph title."
        )

    if og_description and og_description.get("content"):
        score += 10
    else:
        recommendations.append(
            "Add an Open Graph description."
        )

    if og_image and og_image.get("content"):
        score += 10
    else:
        recommendations.append(
            "Add an Open Graph image."
        )

    # --------------------------------------------------------
    # TWITTER
    # --------------------------------------------------------

    twitter_card = soup.find(
        "meta",
        attrs={
            "name": "twitter:card",
        },
    )

    twitter_title = soup.find(
        "meta",
        attrs={
            "name": "twitter:title",
        },
    )

    twitter_description = soup.find(
        "meta",
        attrs={
            "name": "twitter:description",
        },
    )

    twitter_image = soup.find(
        "meta",
        attrs={
            "name": "twitter:image",
        },
    )

    twitter_recommendations = []

    if not twitter_card:
        twitter_recommendations.append(
            "Consider adding Twitter Card metadata."
        )

    return {
        "score": min(score, 100),

        "title_length": title_length,

        "description_length": description_length,

        "canonical_url": canonical_url,

        "canonical_valid": canonical_valid,

        "viewport": viewport_content,

        "open_graph": {
            "title": bool(
                og_title
                and og_title.get("content")
            ),
            "description": bool(
                og_description
                and og_description.get("content")
            ),
            "image": bool(
                og_image
                and og_image.get("content")
            ),
        },

        "twitter_card": {
            "exists": bool(twitter_card),

            "title": bool(
                twitter_title
                and twitter_title.get("content")
            ),

            "description": bool(
                twitter_description
                and twitter_description.get("content")
            ),

            "image": bool(
                twitter_image
                and twitter_image.get("content")
            ),
        },

        "recommendations": (
            recommendations
            + twitter_recommendations
        ),
    }


# ============================================================
# ROBOTS META
# ============================================================

def analyze_robots_meta(soup):

    robots_meta = soup.find(
        "meta",
        attrs={
            "name": lambda value: (
                value
                and str(value).lower() == "robots"
            )
        },
    )

    if not robots_meta:

        return {
            "exists": False,
            "content": None,
            "indexable": True,
            "followable": True,
            "recommendations": [],
        }

    content = robots_meta.get(
        "content",
        "",
    ).strip()

    directives = [
        item.strip().lower()
        for item in content.split(",")
        if item.strip()
    ]

    indexable = "noindex" not in directives
    followable = "nofollow" not in directives

    recommendations = []

    if "noindex" in directives:
        recommendations.append(
            "The robots meta tag contains noindex. Make sure this is intentional."
        )

    if "nofollow" in directives:
        recommendations.append(
            "The robots meta tag contains nofollow. Make sure this is intentional."
        )

    return {
        "exists": True,
        "content": content,
        "indexable": indexable,
        "followable": followable,
        "recommendations": recommendations,
    }


# ============================================================
# ROBOTS.TXT
# ============================================================

def check_robots_txt(url):

    robots_url = urljoin(
        url,
        "/robots.txt",
    )

    try:

        response = requests.get(
            robots_url,
            timeout=10,
            headers=REQUEST_HEADERS,
        )

        if response.status_code != 200:

            return {
                "exists": False,
                "url": robots_url,
                "status_code": response.status_code,
                "sitemaps": [],
                "disallow_rules": [],
                "allow_rules": [],
                "content_preview": "",
                "recommendations": [
                    "Add a robots.txt file."
                ],
            }

        content = response.text

        sitemaps = []
        disallow_rules = []
        allow_rules = []

        for line in content.splitlines():

            line = line.strip()

            if not line or line.startswith("#"):
                continue

            lower_line = line.lower()

            if lower_line.startswith("sitemap:"):

                sitemap_url = line.split(
                    ":",
                    1,
                )[1].strip()

                if sitemap_url:
                    sitemaps.append(
                        sitemap_url
                    )

            elif lower_line.startswith("disallow:"):

                rule = line.split(
                    ":",
                    1,
                )[1].strip()

                disallow_rules.append(rule)

            elif lower_line.startswith("allow:"):

                rule = line.split(
                    ":",
                    1,
                )[1].strip()

                allow_rules.append(rule)

        return {
            "exists": True,
            "url": robots_url,
            "status_code": response.status_code,
            "sitemaps": sitemaps,
            "disallow_rules": disallow_rules[:100],
            "allow_rules": allow_rules[:100],
            "content_preview": content[:1000],
            "recommendations": [],
        }

    except requests.exceptions.RequestException:

        return {
            "exists": False,
            "url": robots_url,
            "status_code": None,
            "sitemaps": [],
            "disallow_rules": [],
            "allow_rules": [],
            "content_preview": "",
            "recommendations": [
                "Add a robots.txt file."
            ],
        }


# ============================================================
# SITEMAP
# ============================================================

def check_sitemap(
    url,
    robots_txt=None,
):

    sitemap_urls = []

    if robots_txt:

        sitemap_urls.extend(
            robots_txt.get(
                "sitemaps",
                [],
            )
        )

    default_sitemap = urljoin(
        url,
        "/sitemap.xml",
    )

    if default_sitemap not in sitemap_urls:
        sitemap_urls.append(
            default_sitemap
        )

    for sitemap_url in sitemap_urls:

        try:

            response = requests.get(
                sitemap_url,
                timeout=10,
                headers=REQUEST_HEADERS,
            )

            if response.status_code != 200:
                continue

            content = response.text

            url_count = content.count(
                "<url>"
            )

            sitemap_count = content.count(
                "<sitemap>"
            )

            if sitemap_count > 0:
                sitemap_type = "sitemap_index"

            elif url_count > 0:
                sitemap_type = "urlset"

            else:
                sitemap_type = "unknown"

            return {
                "exists": True,
                "url": sitemap_url,
                "status_code": response.status_code,
                "url_count": url_count,
                "sitemap_type": sitemap_type,
                "recommendations": [],
            }

        except requests.exceptions.RequestException:
            continue

    return {
        "exists": False,
        "url": default_sitemap,
        "status_code": 404,
        "url_count": 0,
        "sitemap_type": None,
        "recommendations": [
            "Add a sitemap.xml file."
        ],
    }


# ============================================================
# LINKS
# ============================================================

def analyze_links(
    soup,
    base_url,
):

    links = soup.find_all(
        "a",
        href=True,
    )

    internal_links = []
    external_links = []
    empty_links = []

    base_domain = urlparse(
        base_url
    ).netloc.lower()

    for link in links:

        href = link.get(
            "href",
            "",
        ).strip()

        if not href:

            empty_links.append("")

            continue

        if href.startswith("#"):
            continue

        if href.lower().startswith(
            "javascript:"
        ):
            continue

        full_url = urljoin(
            base_url,
            href,
        )

        parsed = urlparse(
            full_url
        )

        domain = parsed.netloc.lower()

        if domain == base_domain:
            internal_links.append(full_url)
        else:
            external_links.append(full_url)

    return {
        "total": len(links),

        "internal": len(internal_links),

        "external": len(external_links),

        "empty": len(empty_links),

        "internal_urls": list(
            dict.fromkeys(
                internal_links
            )
        )[:50],

        "external_urls": list(
            dict.fromkeys(
                external_links
            )
        )[:50],
    }


# ============================================================
# URL STATUS
# ============================================================

def check_url_status(url):

    try:

        response = requests.head(
            url,
            timeout=8,
            allow_redirects=True,
            headers=REQUEST_HEADERS,
        )

        if response.status_code >= 400:

            response = requests.get(
                url,
                timeout=8,
                allow_redirects=True,
                headers=REQUEST_HEADERS,
            )

        return {
            "url": url,
            "status_code": response.status_code,
            "working": response.status_code < 400,
            "final_url": response.url,
        }

    except requests.exceptions.RequestException as error:

        return {
            "url": url,
            "status_code": None,
            "working": False,
            "final_url": None,
            "error": str(error),
        }


# ============================================================
# BROKEN LINKS
# ============================================================

def analyze_broken_links(
    link_analysis,
):

    urls = (
        link_analysis.get(
            "internal_urls",
            [],
        )
        +
        link_analysis.get(
            "external_urls",
            [],
        )
    )

    urls = list(
        dict.fromkeys(urls)
    )[:50]

    results = []
    broken_links = []

    for url in urls:

        result = check_url_status(
            url
        )

        results.append(result)

        if not result["working"]:
            broken_links.append(result)

    return {
        "checked": len(results),

        "broken": len(broken_links),

        "working": (
            len(results)
            - len(broken_links)
        ),

        "broken_urls": broken_links,
    }


# ============================================================
# FAVICON
# ============================================================

def check_favicon(
    soup,
    base_url,
):

    favicon = None

    for link in soup.find_all("link"):

        rel = link.get(
            "rel",
            [],
        )

        if isinstance(rel, str):

            rel_values = (
                rel.lower().split()
            )

        else:

            rel_values = [
                str(value).lower()
                for value in rel
            ]

        if "icon" in rel_values:

            favicon = link

            break

    if favicon:

        href = favicon.get(
            "href"
        )

        if href:

            favicon_url = urljoin(
                base_url,
                href,
            )

            if favicon_url.startswith(
                "data:"
            ):

                return {
                    "exists": True,
                    "valid": False,
                    "url": favicon_url,
                    "type": favicon.get("type"),
                    "recommendations": [
                        "Add a valid favicon file."
                    ],
                }

            try:

                response = requests.get(
                    favicon_url,
                    timeout=5,
                    headers=REQUEST_HEADERS,
                )

                content_type = response.headers.get(
                    "Content-Type",
                    "",
                ).lower()

                valid = (
                    response.status_code == 200
                    and (
                        "image/" in content_type
                        or favicon_url.lower().endswith(
                            (
                                ".ico",
                                ".png",
                                ".jpg",
                                ".jpeg",
                                ".svg",
                                ".webp",
                            )
                        )
                    )
                )

                return {
                    "exists": True,
                    "valid": valid,
                    "url": favicon_url,
                    "type": (
                        content_type
                        or favicon.get("type")
                    ),
                    "recommendations": (
                        []
                        if valid
                        else [
                            "Add a valid favicon file."
                        ]
                    ),
                }

            except requests.exceptions.RequestException:

                return {
                    "exists": True,
                    "valid": False,
                    "url": favicon_url,
                    "type": favicon.get("type"),
                    "recommendations": [
                        "Add a valid favicon file."
                    ],
                }

    favicon_url = urljoin(
        base_url,
        "/favicon.ico",
    )

    try:

        response = requests.get(
            favicon_url,
            timeout=5,
            headers=REQUEST_HEADERS,
        )

        content_type = response.headers.get(
            "Content-Type",
            "",
        ).lower()

        valid = (
            response.status_code == 200
            and (
                "image/" in content_type
                or favicon_url.lower().endswith(".ico")
            )
        )

        if valid:

            return {
                "exists": True,
                "valid": True,
                "url": favicon_url,
                "type": content_type,
                "recommendations": [],
            }

    except requests.exceptions.RequestException:
        pass

    return {
        "exists": False,
        "valid": False,
        "url": favicon_url,
        "type": None,
        "recommendations": [
            "Add a valid favicon file."
        ],
    }


# ============================================================
# LANGUAGE
# ============================================================

def analyze_language(soup):

    html_tag = soup.find("html")

    if not html_tag:

        return {
            "exists": False,
            "language": None,
            "recommendations": [
                "Add a language attribute to the HTML element."
            ],
        }

    language = html_tag.get(
        "lang"
    )

    if language:

        return {
            "exists": True,
            "language": language.strip(),
            "recommendations": [],
        }

    return {
        "exists": False,
        "language": None,
        "recommendations": [
            "Add a language attribute to the HTML element."
        ],
    }


# ============================================================
# STRUCTURED DATA
# ============================================================

def analyze_structured_data(soup):

    json_ld_scripts = soup.find_all(
        "script",
        attrs={
            "type": "application/ld+json"
        },
    )

    microdata_items = soup.find_all(
        attrs={
            "itemscope": True
        },
    )

    count = (
        len(json_ld_scripts)
        +
        len(microdata_items)
    )

    if count > 0:

        return {
            "exists": True,

            "count": count,

            "json_ld_count": len(
                json_ld_scripts
            ),

            "microdata_count": len(
                microdata_items
            ),

            "recommendations": [],
        }

    return {
        "exists": False,
        "count": 0,
        "json_ld_count": 0,
        "microdata_count": 0,
        "recommendations": [
            "Consider adding structured data using Schema.org."
        ],
    }


# ============================================================
# MOBILE
# ============================================================

def analyze_mobile_readiness(soup):

    viewport = soup.find(
        "meta",
        attrs={
            "name": "viewport"
        },
    )

    if not viewport:

        return {
            "mobile_ready": False,
            "viewport": None,
            "recommendations": [
                "Add a responsive viewport meta tag."
            ],
        }

    viewport_content = viewport.get(
        "content",
        "",
    ).strip()

    if not viewport_content:

        return {
            "mobile_ready": False,
            "viewport": "",
            "recommendations": [
                "Add a valid viewport configuration."
            ],
        }

    return {
        "mobile_ready": True,
        "viewport": viewport_content,
        "recommendations": [],
    }


# ============================================================
# PAGE SIZE
# ============================================================

def analyze_page_size(response):

    html_bytes = len(
        response.content
    )

    html_kilobytes = round(
        html_bytes / 1024,
        2,
    )

    recommendations = []

    if html_kilobytes > 500:

        recommendations.append(
            "HTML page size is large. "
            "Consider reducing unnecessary markup."
        )

    elif html_kilobytes > 300:

        recommendations.append(
            "Consider reducing HTML page size "
            "to improve loading performance."
        )

    return {
        "bytes": html_bytes,
        "kilobytes": html_kilobytes,
        "recommendations": recommendations,
    }


# ============================================================
# TEXT RATIO
# ============================================================

def analyze_text_ratio(
    soup,
    response,
):
    """
    Calculates the percentage of the HTML response
    represented by visible text.

    This function is intentionally kept as a standalone
    function because views.py imports it directly.
    """

    html_bytes = len(
        response.content
    )

    text = soup.get_text(
        separator=" ",
        strip=True,
    )

    text_bytes = len(
        text.encode(
            "utf-8",
            errors="ignore",
        )
    )

    if html_bytes > 0:

        ratio = round(
            (text_bytes / html_bytes) * 100,
            2,
        )

    else:

        ratio = 0

    recommendations = []

    if ratio < 10:

        recommendations.append(
            "The page has a low text-to-HTML ratio. "
            "Consider adding useful textual content."
        )

    return {
        "text_bytes": text_bytes,

        "html_bytes": html_bytes,

        "ratio_percent": ratio,

        "recommendations": recommendations,
    }


# ============================================================
# HEADING STRUCTURE
# ============================================================

def analyze_heading_structure(soup):

    counts = {}

    for level in range(1, 7):

        tag = f"h{level}"

        counts[tag] = len(
            soup.find_all(tag)
        )

    recommendations = []

    if counts["h1"] == 0:

        recommendations.append(
            "No H1 heading was found."
        )

    elif counts["h1"] > 1:

        recommendations.append(
            "Multiple H1 headings were found."
        )

    heading_levels = []

    for heading in soup.find_all(
        [
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
        ]
    ):

        try:

            level = int(
                heading.name[1:]
            )

            heading_levels.append(
                level
            )

        except (
            ValueError,
            TypeError,
        ):
            continue

    skipped_levels = []

    for previous, current in zip(
        heading_levels,
        heading_levels[1:],
    ):

        if current > previous + 1:

            skipped_levels.append(
                {
                    "from": f"h{previous}",
                    "to": f"h{current}",
                }
            )

    if skipped_levels:

        recommendations.append(
            "Heading hierarchy contains skipped levels."
        )

    return {
        "counts": counts,

        "heading_levels": heading_levels,

        "skipped_levels": skipped_levels,

        "recommendations": recommendations,
    }


# ============================================================
# IMAGE ANALYSIS
# ============================================================

def analyze_images(soup):

    images = soup.find_all("img")

    without_alt = []
    with_alt = []
    empty_alt = []
    with_title = []
    lazy_loaded = []
    missing_dimensions = []

    for image in images:

        alt = image.get("alt")

        if alt is None:

            without_alt.append(image)

        elif not alt.strip():

            empty_alt.append(image)

        else:

            with_alt.append(image)

        if image.get("title"):
            with_title.append(image)

        loading = image.get(
            "loading",
            "",
        ).lower()

        if loading == "lazy":
            lazy_loaded.append(image)

        if (
            not image.get("width")
            or not image.get("height")
        ):

            missing_dimensions.append(
                image
            )

    missing_alt_count = (
        len(without_alt)
        +
        len(empty_alt)
    )

    recommendations = []

    if missing_alt_count > 0:

        recommendations.append(
            f"Add meaningful alt text to "
            f"{missing_alt_count} image(s)."
        )

    if images and not lazy_loaded:

        recommendations.append(
            "Consider lazy-loading below-the-fold images."
        )

    if missing_dimensions:

        recommendations.append(
            f"Add width and height attributes to "
            f"{len(missing_dimensions)} image(s) "
            "to reduce layout shifts."
        )

    return {
        "total": len(images),

        "with_alt": len(with_alt),

        "without_alt": len(without_alt),

        "empty_alt": len(empty_alt),

        "with_title": len(with_title),

        "lazy_loaded": len(lazy_loaded),

        "missing_dimensions": len(
            missing_dimensions
        ),

        "recommendations": recommendations,
    }


# ============================================================
# NOFOLLOW
# ============================================================

def analyze_nofollow_links(soup):

    links = soup.find_all(
        "a",
        href=True,
    )

    nofollow_links = []

    for link in links:

        rel = link.get(
            "rel",
            [],
        )

        if isinstance(rel, str):
            rel = rel.split()

        rel = [
            str(value).lower()
            for value in rel
        ]

        if "nofollow" in rel:

            nofollow_links.append(
                link.get("href")
            )

    return {
        "count": len(nofollow_links),
        "urls": nofollow_links[:50],
    }


# ============================================================
# SECURITY HEADERS
# ============================================================

def analyze_security_headers(response):

    headers = response.headers

    security_headers = {
        "strict_transport_security": headers.get(
            "Strict-Transport-Security"
        ),

        "content_security_policy": headers.get(
            "Content-Security-Policy"
        ),

        "x_content_type_options": headers.get(
            "X-Content-Type-Options"
        ),

        "x_frame_options": headers.get(
            "X-Frame-Options"
        ),

        "referrer_policy": headers.get(
            "Referrer-Policy"
        ),

        "permissions_policy": headers.get(
            "Permissions-Policy"
        ),
    }

    recommendations = []

    if not security_headers[
        "strict_transport_security"
    ]:

        recommendations.append(
            "Consider enabling HSTS with the "
            "Strict-Transport-Security header."
        )

    if not security_headers[
        "content_security_policy"
    ]:

        recommendations.append(
            "Consider adding a Content-Security-Policy header."
        )

    if not security_headers[
        "x_content_type_options"
    ]:

        recommendations.append(
            "Add the X-Content-Type-Options: nosniff header."
        )

    if not security_headers[
        "x_frame_options"
    ]:

        recommendations.append(
            "Consider adding the X-Frame-Options header."
        )

    if not security_headers[
        "referrer_policy"
    ]:

        recommendations.append(
            "Consider adding a Referrer-Policy header."
        )

    if not security_headers[
        "permissions_policy"
    ]:

        recommendations.append(
            "Consider adding a Permissions-Policy header."
        )

    return {
        "headers": security_headers,
        "recommendations": recommendations,
    }


# ============================================================
# ENHANCED SECURITY SCORE
# ============================================================

def calculate_enhanced_security_score(
    url,
    security_headers,
):

    score = 100
    recommendations = []

    if not url.lower().startswith(
        "https://"
    ):

        score -= 50

        recommendations.append(
            "Use HTTPS to secure communication with visitors."
        )

    headers = security_headers.get(
        "headers",
        {},
    )

    checks = [
        (
            "strict_transport_security",
            10,
            "Enable HSTS.",
        ),
        (
            "content_security_policy",
            10,
            "Add a Content-Security-Policy header.",
        ),
        (
            "x_content_type_options",
            5,
            "Add X-Content-Type-Options: nosniff.",
        ),
        (
            "x_frame_options",
            5,
            "Add X-Frame-Options.",
        ),
    ]

    for (
        key,
        deduction,
        recommendation,
    ) in checks:

        if not headers.get(key):

            score -= deduction

            recommendations.append(
                recommendation
            )

    return (
        max(
            min(score, 100),
            0,
        ),
        recommendations,
    )


# ============================================================
# PERFORMANCE DETAILS
# ============================================================

def analyze_performance_details(
    response,
):

    response_time = round(
        response.elapsed.total_seconds(),
        3,
    )

    html_bytes = len(
        response.content
    )

    content_encoding = response.headers.get(
        "Content-Encoding"
    )

    cache_control = response.headers.get(
        "Cache-Control"
    )

    content_type = response.headers.get(
        "Content-Type"
    )

    recommendations = []

    if response_time > 3:

        recommendations.append(
            "Server response time is slow."
        )

    elif response_time > 1.5:

        recommendations.append(
            "Server response time could be improved."
        )

    if html_bytes > 500 * 1024:

        recommendations.append(
            "HTML document is larger than 500 KB."
        )

    if not content_encoding:

        recommendations.append(
            "Consider enabling HTTP compression such as Brotli or gzip."
        )

    return {
        "response_time_seconds": response_time,

        "html_bytes": html_bytes,

        "html_kilobytes": round(
            html_bytes / 1024,
            2,
        ),

        "content_encoding": content_encoding,

        "cache_control": cache_control,

        "content_type": content_type,

        "recommendations": recommendations,
    }


# ============================================================
# TECHNICAL SEO SCORE
# ============================================================

def calculate_technical_seo_score(
    advanced_seo,
    favicon,
    language,
    structured_data,
    mobile_readiness,
    robots_txt,
    sitemap,
    robots_meta,
):

    score = 0

    # Advanced SEO: 40
    score += (
        min(
            advanced_seo.get(
                "score",
                0,
            ),
            100,
        )
        * 0.40
    )

    # Favicon: 10
    if favicon.get("valid"):
        score += 10

    # Language: 10
    if language.get("exists"):
        score += 10

    # Structured data: 10
    if structured_data.get("exists"):
        score += 10

    # Mobile: 10
    if mobile_readiness.get(
        "mobile_ready"
    ):
        score += 10

    # Robots: 10
    if robots_txt.get("exists"):
        score += 10

    # Sitemap: 10
    if sitemap.get("exists"):
        score += 10

    return round(
        min(score, 100)
    )


# ============================================================
# SCORE CATEGORIES
# ============================================================

def analyze_score_categories(
    seo_score,
    technical_seo_score,
    accessibility_score,
    performance_score,
    security_score,
):

    categories = {

        "seo": {
            "score": seo_score,
            "weight": 30,
        },

        "technical_seo": {
            "score": technical_seo_score,
            "weight": 20,
        },

        "accessibility": {
            "score": accessibility_score,
            "weight": 15,
        },

        "performance": {
            "score": performance_score,
            "weight": 20,
        },

        "security": {
            "score": security_score,
            "weight": 15,
        },
    }

    for category in categories:

        score = categories[
            category
        ]["score"]

        weight = categories[
            category
        ]["weight"]

        categories[
            category
        ]["weighted_score"] = round(
            score * weight / 100,
            2,
        )

        categories[
            category
        ]["status"] = get_score_status(
            score
        )

    return categories


# ============================================================
# WEIGHTED OVERALL SCORE
# ============================================================

def calculate_weighted_overall_score(
    seo_score,
    technical_seo_score,
    accessibility_score,
    performance_score,
    security_score,
):

    score = (
        (seo_score * 0.30)
        +
        (technical_seo_score * 0.20)
        +
        (accessibility_score * 0.15)
        +
        (performance_score * 0.20)
        +
        (security_score * 0.15)
    )

    return round(score)


# ============================================================
# RECOMMENDATION STATISTICS
# ============================================================

def analyze_recommendation_stats(
    recommendations,
):

    unique_recommendations = list(
        dict.fromkeys(
            recommendations
        )
    )

    total = len(
        unique_recommendations
    )

    if total == 0:

        status = "excellent"

    elif total <= 3:

        status = "good"

    elif total <= 7:

        status = "needs_improvement"

    else:

        status = "poor"

    return {
        "total": total,
        "status": status,
    }


# ============================================================
# AUDIT SUMMARY
# ============================================================
def create_audit_summary(
    overall_score,
    score_grade,
    category_scores,
    recommendations,
):

    strongest_category = max(
        category_scores,
        key=lambda category:
        category_scores[
            category
        ]["score"],
    )

    weakest_category = min(
        category_scores,
        key=lambda category:
        category_scores[
            category
        ]["score"],
    )

    recommendation_stats = (
        analyze_recommendation_stats(
            recommendations
        )
    )

    if overall_score >= 80:

        priority = "low"

    elif overall_score >= 60:

        priority = "medium"

    else:

        priority = "high"

    return {

        "overall_score": overall_score,

        "grade": score_grade["grade"],

        "label": score_grade["label"],

        "status": get_score_status(
            overall_score
        ),

        "strongest_category": {
            "name": strongest_category,
            "score": category_scores[
                strongest_category
            ]["score"],
        },

        "weakest_category": {
            "name": weakest_category,
            "score": category_scores[
                weakest_category
            ]["score"],
        },

        "recommendation_count": (
            recommendation_stats["total"]
        ),

        "recommendation_status": (
            recommendation_stats["status"]
        ),

        "priority": priority,
    }