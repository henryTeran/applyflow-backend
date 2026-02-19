"""
Job offer scraping service - extracts job details from URLs.
Supports: LinkedIn, Indeed, Welcome to the Jungle
"""

import time
import logging
import re
import html as html_lib
import json
from pydantic import BaseModel

logger = logging.getLogger(__name__)


def _strip_html(html_text: str) -> str:
    if not html_text:
        return ""
    # Unescape entities then remove tags
    text = html_lib.unescape(html_text)
    text = re.sub(r"<\s*br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</\s*p\s*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    # Restore some spacing/newlines heuristically
    text = text.replace(" \n ", "\n").strip()
    return text


def _extract_description_from_jsonld(page_source: str) -> str:
    """Try to extract a full job description from JSON-LD scripts."""
    if not page_source:
        return ""

    scripts = re.findall(
        r"<script[^>]*type=['\"]application/ld\+json['\"][^>]*>(.*?)</script>",
        page_source,
        flags=re.IGNORECASE | re.DOTALL,
    )

    best = ""
    for raw in scripts:
        raw = raw.strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue

        candidates = data if isinstance(data, list) else [data]
        for item in candidates:
            if not isinstance(item, dict):
                continue
            desc = item.get("description")
            if isinstance(desc, str) and len(desc) > len(best):
                best = desc

    return _strip_html(best)


def _extract_jobposting_from_jsonld(page_source: str) -> dict:
    """Extract key JobPosting fields from JSON-LD (title/company/location)."""
    if not page_source:
        return {}

    scripts = re.findall(
        r"<script[^>]*type=['\"]application/ld\+json['\"][^>]*>(.*?)</script>",
        page_source,
        flags=re.IGNORECASE | re.DOTALL,
    )

    def _iter_items(obj):
        if isinstance(obj, list):
            for it in obj:
                yield from _iter_items(it)
        elif isinstance(obj, dict):
            yield obj
            # Sometimes wrapped in @graph
            graph = obj.get("@graph")
            if graph is not None:
                yield from _iter_items(graph)

    best: dict = {}
    for raw in scripts:
        raw = raw.strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue

        for item in _iter_items(data):
            if not isinstance(item, dict):
                continue
            if item.get("@type") != "JobPosting":
                continue

            title = item.get("title") or ""
            company = ""
            org = item.get("hiringOrganization")
            if isinstance(org, dict):
                company = org.get("name") or ""

            location = ""
            job_loc = item.get("jobLocation")
            # jobLocation can be dict or list
            job_locs = job_loc if isinstance(job_loc, list) else [job_loc]
            for jl in job_locs:
                if not isinstance(jl, dict):
                    continue
                addr = jl.get("address")
                if isinstance(addr, dict):
                    parts = [
                        addr.get("addressLocality"),
                        addr.get("addressRegion"),
                        addr.get("addressCountry"),
                    ]
                    location = ", ".join([p for p in parts if isinstance(p, str) and p.strip()])
                if location:
                    break

            candidate = {
                "title": title.strip(),
                "company": company.strip(),
                "location": location.strip(),
            }

            # Keep the one with most filled fields
            if sum(1 for v in candidate.values() if v) > sum(1 for v in best.values() if v):
                best = candidate

    return best


def _extract_meta_content(page_source: str, key: str) -> str:
    """Extract <meta property/name=key content=...>."""
    if not page_source or not key:
        return ""

    patterns = [
        rf"<meta[^>]+property=['\"]{re.escape(key)}['\"][^>]+content=['\"](.*?)['\"][^>]*>",
        rf"<meta[^>]+name=['\"]{re.escape(key)}['\"][^>]+content=['\"](.*?)['\"][^>]*>",
    ]
    for pat in patterns:
        m = re.search(pat, page_source, flags=re.IGNORECASE | re.DOTALL)
        if m:
            return html_lib.unescape(m.group(1)).strip()
    return ""


def _looks_truncated(description: str) -> bool:
    if not description:
        return True
    # LinkedIn pages often contain these headings; absence + short text => likely truncated
    d = description.lower()
    if len(description) < 600:
        return True
    if ("requirements" not in d and "responsibil" not in d) and len(description) < 1200:
        return True
    return False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium not available - scraping will use mock data")


class ScrapeResult(BaseModel):
    """Result of job offer scraping"""
    title: str
    company: str
    location: str | None = None
    description: str
    application_type: str = "portal"
    application_url: str


def get_chrome_driver():
    """Initialize headless Chrome driver"""
    if not SELENIUM_AVAILABLE:
        raise RuntimeError("Selenium is not installed")
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    return webdriver.Chrome(options=options)


def scrape_linkedin(url: str) -> ScrapeResult:
    """
    Scrape LinkedIn job posting.
    
    Args:
        url: LinkedIn job URL (e.g., https://www.linkedin.com/jobs/view/12345/)
    
    Returns:
        ScrapeResult with job details
    
    Raises:
        Exception if scraping fails
    """
    driver = get_chrome_driver()
    
    try:
        logger.info(f"Scraping LinkedIn job: {url}")

        # LinkedIn est souvent plus accessible via la vue publique "jobs-guest"
        job_id_match = re.search(r"/jobs/view/(\d+)", url)
        if job_id_match and "jobs-guest" not in url:
            job_id = job_id_match.group(1)
            guest_url = f"https://www.linkedin.com/jobs-guest/jobs/view/{job_id}/"
            logger.info(f"Using LinkedIn guest URL: {guest_url}")
            driver.get(guest_url)
        else:
            driver.get(url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 10)

        # Scroll un peu pour forcer le chargement lazy
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
        except Exception:
            pass

        # Détection basique de "login wall" / page bloquée
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
            if ("sign in" in body_text and "join linkedin" in body_text) or "you've reached the limit" in body_text:
                raise ValueError(
                    "LinkedIn bloque l'accès (page de connexion). Essayez avec un lien public jobs-guest, "
                    "ou copiez/collez la description dans l'app si le scraping échoue."
                )
        except ValueError:
            raise
        except Exception:
            pass
        
        # Extract title
        try:
            title_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.top-card-layout__title, h1.topcard__title"))
            )
            title = title_element.text.strip()
        except TimeoutException:
            # Fallback
            try:
                title = driver.find_element(By.TAG_NAME, "h1").text.strip()
            except Exception:
                title = ""
        
        # Extract company
        try:
            company = driver.find_element(By.CSS_SELECTOR, "a.topcard__org-name-link, .topcard__flavor--black-link").text.strip()
        except NoSuchElementException:
            try:
                company = driver.find_element(By.CSS_SELECTOR, ".topcard__flavor").text.strip()
            except Exception:
                company = ""
        
        # Extract location (optional)
        location = None
        try:
            location_element = driver.find_element(By.CSS_SELECTOR, "span.topcard__flavor--bullet, .topcard__flavor--metadata")
            location = location_element.text.strip()
        except NoSuchElementException:
            pass

        # Fallback title/company/location from JSON-LD + meta
        try:
            page_source = driver.page_source or ""
            jobposting = _extract_jobposting_from_jsonld(page_source)
            if not title:
                title = (jobposting.get("title") or "")
            if not company:
                company = (jobposting.get("company") or "")
            if not location:
                location = (jobposting.get("location") or None)

            if not title:
                og_title = _extract_meta_content(page_source, "og:title")
                # og:title often looks like "Title | LinkedIn"
                title = og_title.split("|")[0].strip() if og_title else title
        except Exception:
            pass
        
        # Extract description with improved selectors
        description = ""
        try:
            # Try to click "Show more" button if exists (multiple possible selectors)
            show_more_buttons = [
                "button.show-more-less-html__button",
                "button[aria-label*='Show more']",
                "button.show-more-less-html__button--more",
                ".show-more-less-html__button",
                "button[aria-label*='See more']",
                "button[aria-label*='Show']",
            ]
            
            for selector in show_more_buttons:
                try:
                    show_more = driver.find_element(By.CSS_SELECTOR, selector)
                    driver.execute_script("arguments[0].click();", show_more)
                    logger.info(f"Clicked 'Show more' button using selector: {selector}")
                    time.sleep(2)  # Wait for content to expand
                    break
                except NoSuchElementException:
                    continue
            
            # Try multiple possible selectors for description
            description_selectors = [
                ".show-more-less-html__markup",
                ".description__text",
                ".jobs-description__content",
                ".jobs-box__html-content",
                "div.description",
                "article.jobs-description"
            ]
            
            description_found = False
            for selector in description_selectors:
                try:
                    desc_element = driver.find_element(By.CSS_SELECTOR, selector)
                    description = desc_element.text.strip()
                    if description:
                        logger.info(f"Found description using selector: {selector} ({len(description)} chars)")
                        description_found = True
                        break
                except NoSuchElementException:
                    continue
            
            if not description_found or len(description) < 200:
                # Last resort: get all text from the main content area
                try:
                    main_content = driver.find_element(By.CSS_SELECTOR, "main")
                    description_fallback = main_content.text.strip()
                    if description_fallback and len(description_fallback) > len(description):
                        description = description_fallback
                    logger.info(f"Used fallback main content extraction ({len(description)} chars)")
                except NoSuchElementException:
                    try:
                        body = driver.find_element(By.TAG_NAME, "body").text.strip()
                        if body and len(body) > len(description):
                            description = body
                        logger.info(f"Used body fallback extraction ({len(description)} chars)")
                    except Exception:
                        description = "No description available"
                        logger.warning("Could not extract job description")

            # If it still looks truncated, try JSON-LD from page source (often has full HTML description)
            if _looks_truncated(description):
                try:
                    jsonld_desc = _extract_description_from_jsonld(driver.page_source)
                    if jsonld_desc and len(jsonld_desc) > len(description):
                        description = jsonld_desc
                        logger.info(f"Used JSON-LD description extraction ({len(description)} chars)")
                except Exception as e:
                    logger.info(f"JSON-LD extraction not available: {e}")
        except Exception as e:
            logger.error(f"Error extracting description: {e}")
            description = "No description available"
        
        if not title or not company:
            logger.warning(f"LinkedIn scrape missing key fields title/company (title='{title}', company='{company}')")

        logger.info(f"Successfully scraped LinkedIn job: {title} at {company}")
        
        return ScrapeResult(
            title=title,
            company=company,
            location=location,
            description=description,
            application_type="portal",
            application_url=url
        )
        
    except Exception as e:
        logger.error(f"Failed to scrape LinkedIn job: {str(e)}")
        raise Exception(f"Failed to scrape LinkedIn job: {str(e)}")
    
    finally:
        driver.quit()


def scrape_indeed(url: str) -> ScrapeResult:
    """
    Scrape Indeed job posting.
    
    Args:
        url: Indeed job URL
    
    Returns:
        ScrapeResult with job details
    """
    driver = get_chrome_driver()
    
    try:
        logger.info(f"Scraping Indeed job: {url}")
        driver.get(url)
        time.sleep(2)
        
        # Extract title
        title = driver.find_element(By.CSS_SELECTOR, "h1.jobsearch-JobInfoHeader-title, h1").text.strip()
        
        # Extract company
        try:
            company = driver.find_element(By.CSS_SELECTOR, "[data-testid='inlineHeader-companyName'], .jobsearch-InlineCompanyRating").text.strip()
        except NoSuchElementException:
            company = driver.find_element(By.CSS_SELECTOR, ".icl-u-lg-mr--sm").text.strip()
        
        # Extract location
        location = None
        try:
            location_selectors = [
                "[data-testid='inlineHeader-companyLocation']",
                ".jobsearch-JobInfoHeader-subtitle",
                "[data-testid='job-location']",
                ".jobsearch-JobMetadataHeader-iconLabel"
            ]
            for selector in location_selectors:
                try:
                    location = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                    if location:
                        break
                except NoSuchElementException:
                    continue
        except Exception:
            pass
        
        # Extract description with improved selectors
        description = ""
        try:
            description_selectors = [
                "#jobDescriptionText",
                "[id='jobDescriptionText']",
                ".jobsearch-jobDescriptionText",
                ".jobsearch-JobComponent-description",
                "div[class*='description']"
            ]
            
            for selector in description_selectors:
                try:
                    if selector.startswith("#"):
                        desc_element = driver.find_element(By.ID, selector[1:])
                    else:
                        desc_element = driver.find_element(By.CSS_SELECTOR, selector)
                    description = desc_element.text.strip()
                    if description:
                        logger.info(f"Found Indeed description using selector: {selector} ({len(description)} chars)")
                        break
                except NoSuchElementException:
                    continue
            
            if not description:
                description = "No description available"
                logger.warning("Could not extract Indeed job description")
        except Exception as e:
            logger.error(f"Error extracting Indeed description: {e}")
            description = "No description available"
        
        logger.info(f"Successfully scraped Indeed job: {title} at {company}")
        
        return ScrapeResult(
            title=title,
            company=company,
            location=location,
            description=description,
            application_type="portal",
            application_url=url
        )
        
    except Exception as e:
        logger.error(f"Failed to scrape Indeed job: {str(e)}")
        raise Exception(f"Failed to scrape Indeed job: {str(e)}")
    
    finally:
        driver.quit()


def scrape_wttj(url: str) -> ScrapeResult:
    """
    Scrape Welcome to the Jungle job posting.
    
    Args:
        url: WTTJ job URL
    
    Returns:
        ScrapeResult with job details
    """
    driver = get_chrome_driver()
    
    try:
        logger.info(f"Scraping WTTJ job: {url}")
        driver.get(url)
        time.sleep(3)  # WTTJ is heavy on JS
        
        # Extract title
        title = driver.find_element(By.TAG_NAME, "h1").text.strip()
        
        # Extract company - try multiple selectors
        company = "Unknown Company"
        company_selectors = [
            "[data-testid='job-header-company-name']",
            "a.ais-company-name",
            ".company-name",
            "[class*='company']",
            "h2"
        ]
        for selector in company_selectors:
            try:
                company = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                if company:
                    logger.info(f"WTTJ company found with selector: {selector}")
                    break
            except NoSuchElementException:
                continue
        
        # Extract location - try multiple selectors
        location = None
        location_selectors = [
            "[data-testid='job-location']",
            ".location",
            "[class*='location']",
            "span[class*='location']"
        ]
        for selector in location_selectors:
            try:
                location = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                if location:
                    logger.info(f"WTTJ location found with selector: {selector}")
                    break
            except NoSuchElementException:
                continue
        
        # Try to click "Show more" / "Read more" buttons if present
        show_more_buttons = [
            "button[data-testid='show-more']",
            "button[class*='show-more']",
            "button[class*='read-more']",
            "a[class*='show-more']"
        ]
        for selector in show_more_buttons:
            try:
                button = driver.find_element(By.CSS_SELECTOR, selector)
                driver.execute_script("arguments[0].click();", button)
                logger.info(f"WTTJ clicked show more button: {selector}")
                time.sleep(1)
            except:
                pass
        
        # Extract description - try multiple selectors with fallback
        description = ""
        description_selectors = [
            ".ais-job-description section",
            "[data-testid='job-description']",
            ".job-description",
            "[class*='description']",
            "article",
            "main"
        ]
        
        for selector in description_selectors:
            try:
                if selector == ".ais-job-description section":
                    desc_sections = driver.find_elements(By.CSS_SELECTOR, selector)
                    description = "\n\n".join([sec.text.strip() for sec in desc_sections if sec.text.strip()])
                else:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    description = element.text.strip()
                
                if description and len(description) > 50:
                    logger.info(f"WTTJ description found with selector: {selector} ({len(description)} chars)")
                    break
            except NoSuchElementException:
                continue
        
        if not description:
            description = "No description available"
        
        logger.info(f"Successfully scraped WTTJ job: {title} at {company}")
        
        return ScrapeResult(
            title=title,
            company=company,
            location=location,
            description=description,
            application_type="portal",
            application_url=url
        )
        
    except Exception as e:
        logger.error(f"Failed to scrape WTTJ job: {str(e)}")
        raise Exception(f"Failed to scrape WTTJ job: {str(e)}")
    
    finally:
        driver.quit()


def scrape_generic(url: str) -> ScrapeResult:
    """Fallback générique Selenium pour les sites non supportés.

    Objectif: récupérer un maximum de texte (body/main) plutôt que d'échouer.
    """
    driver = get_chrome_driver()

    try:
        logger.info(f"Scraping generic page: {url}")
        driver.get(url)
        time.sleep(3)

        # Title
        title = ""
        try:
            title = driver.find_element(By.TAG_NAME, "h1").text.strip()
        except Exception:
            title = (driver.title or "").strip() or "Job Offer"

        # Company is often not reliably extractable generically
        company = "Unknown Company"

        # Description: prefer <main>, else body
        description = ""
        for selector in ["main", "article", "body"]:
            try:
                el = driver.find_element(By.CSS_SELECTOR, selector)
                description = el.text.strip()
                if description and len(description) > 200:
                    break
            except Exception:
                continue

        if not description:
            description = "No description available"

        logger.info(f"Generic scraping extracted {len(description)} chars")
        return ScrapeResult(
            title=title,
            company=company,
            location=None,
            description=description,
            application_type="portal",
            application_url=url,
        )
    except Exception as e:
        logger.error(f"Failed to scrape generic page: {str(e)}")
        raise Exception(f"Failed to scrape generic page: {str(e)}")
    finally:
        driver.quit()


def scrape_job_offer(url: str) -> ScrapeResult:
    """
    Auto-detect platform and scrape job offer.
    
    Args:
        url: Job posting URL
    
    Returns:
        ScrapeResult with job details
    
    Raises:
        ValueError: If platform is not supported
        Exception: If scraping fails
    """
    url_lower = url.lower()
    
    # Check if Selenium is available
    if not SELENIUM_AVAILABLE:
        logger.error(f"Selenium not available - cannot scrape {url}")
        raise ValueError(
            "Selenium is not installed. Please install it with: pip install selenium\n"
            "And install ChromeDriver: https://chromedriver.chromium.org/"
        )
    
    try:
        if "linkedin.com" in url_lower:
            return scrape_linkedin(url)
        elif "indeed.com" in url_lower or "indeed.fr" in url_lower:
            return scrape_indeed(url)
        elif "welcometothejungle.com" in url_lower or "wttj.co" in url_lower:
            return scrape_wttj(url)
        else:
            # Fallback générique au lieu d'échouer: utile pour sites corporate / ATS.
            return scrape_generic(url)
    except Exception as e:
        # If scraping fails due to ChromeDriver, provide helpful error
        error_msg = str(e).lower()
        if "chromedriver" in error_msg or "chrome" in error_msg:
            logger.error(f"ChromeDriver issue: {e}")
            raise ValueError(
                f"ChromeDriver not found or incompatible. Please ensure:\n"
                f"1. Chrome browser is installed\n"
                f"2. ChromeDriver is installed and in PATH\n"
                f"3. ChromeDriver version matches your Chrome version\n"
                f"Error: {str(e)}"
            )
        raise


# Note: Mock data function removed - real scraping only
# If you need mock data for testing, you can re-implement _get_mock_job_data()

