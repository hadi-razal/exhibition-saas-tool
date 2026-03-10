"""
Scraper Engine — Main orchestrator for exhibitor web scraping.

Two-phase approach:
1. Analyze: Quick page analysis to detect structure
2. Scrape: Full data extraction with user-confirmed options
"""
import re
import logging
import asyncio
from typing import AsyncGenerator, Optional
from urllib.parse import urljoin, urlparse

logger = logging.getLogger("exhibitiq.scraper")


class ScraperEngine:
    """Orchestrates exhibitor web scraping with analysis and full scrape phases."""

    async def analyze(self, url: str) -> dict:
        """
        Phase A: Analyze a page to detect structure, pagination, and detail pages.
        Returns analysis summary for user confirmation.
        """
        logger.info(f"Analyzing URL: {url}")

        html, is_dynamic = await self._fetch_page(url)
        if not html:
            raise RuntimeError("Could not load the page. Check the URL and try again.")

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")

        # Detect page title
        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        # Detect pagination
        pagination_detected, estimated_pages = self._detect_pagination(soup, url)

        # Detect exhibitor listing blocks
        exhibitor_count, detected_fields = self._detect_exhibitor_blocks(soup)

        # Detect detail page links
        detail_pages_detected = self._detect_detail_pages(soup, url)

        return {
            "page_title": title[:100],
            "pagination_detected": pagination_detected,
            "estimated_pages": estimated_pages,
            "detail_pages_detected": detail_pages_detected,
            "exhibitor_count_page1": exhibitor_count,
            "detected_fields": detected_fields,
            "is_dynamic": is_dynamic,
        }

    async def scrape(
        self,
        url: str,
        max_pages: int = 10,
        follow_detail_pages: bool = True,
        extract_contacts: bool = True,
    ) -> AsyncGenerator[dict, None]:
        """
        Phase B: Full scrape with user-confirmed options.
        Yields SSE-compatible progress events and final results.
        """
        all_exhibitors = []
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

        yield {"type": "progress", "message": "Loading page...", "current_page": 0, "total_pages": max_pages, "exhibitors_found": 0}

        # Fetch first page
        html, is_dynamic = await self._fetch_page(url)
        if not html:
            yield {"type": "error", "message": "Could not load the page"}
            return

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")

        # Detect pagination URLs
        page_urls = [url]
        pagination_detected, _ = self._detect_pagination(soup, url)
        if pagination_detected:
            additional_urls = self._get_pagination_urls(soup, url, max_pages)
            page_urls.extend(additional_urls)

        total_pages = min(len(page_urls), max_pages)

        # Scrape each page
        for page_num, page_url in enumerate(page_urls[:max_pages], 1):
            yield {
                "type": "progress",
                "message": f"Scraping page {page_num} of {total_pages}...",
                "current_page": page_num,
                "total_pages": total_pages,
                "exhibitors_found": len(all_exhibitors),
            }

            if page_num > 1:
                html, _ = await self._fetch_page(page_url)
                if not html:
                    continue
                soup = BeautifulSoup(html, "lxml")

            # Extract exhibitors from this page
            page_exhibitors = self._extract_exhibitors_from_page(soup, base_url)

            # Follow detail pages if enabled
            if follow_detail_pages and page_exhibitors:
                for i, exhibitor in enumerate(page_exhibitors):
                    profile_url = exhibitor.get("profile_url")
                    if profile_url:
                        yield {
                            "type": "progress",
                            "message": f"Page {page_num}: visiting detail page {i + 1}/{len(page_exhibitors)}...",
                            "current_page": page_num,
                            "total_pages": total_pages,
                            "exhibitors_found": len(all_exhibitors) + i,
                        }
                        detail_data = await self._scrape_detail_page(
                            profile_url, extract_contacts
                        )
                        exhibitor.update(detail_data)

            all_exhibitors.extend(page_exhibitors)

            # Small delay between pages to be polite
            if page_num < total_pages:
                await asyncio.sleep(1)

        # Normalize and deduplicate
        yield {
            "type": "progress",
            "message": "Normalizing and deduplicating data...",
            "current_page": total_pages,
            "total_pages": total_pages,
            "exhibitors_found": len(all_exhibitors),
        }

        all_exhibitors = self._normalize_and_dedup(all_exhibitors)

        # Final result
        yield {
            "type": "result",
            "rows": all_exhibitors,
            "total": len(all_exhibitors),
        }

    # ===================== Page Fetching =====================

    async def _fetch_page(self, url: str) -> tuple[Optional[str], bool]:
        """Fetch a page, trying static first, then dynamic with Playwright."""
        # Try static first
        html = self._fetch_static(url)
        if html and len(html) > 500:
            return html, False

        # Fall back to Playwright for JS-rendered pages
        html = await self._fetch_dynamic(url)
        if html:
            return html, True

        return None, False

    def _fetch_static(self, url: str) -> Optional[str]:
        """Fetch page using requests (fast, for static pages)."""
        try:
            import requests

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }
            resp = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            logger.warning(f"Static fetch failed for {url}: {e}")
            return None

    async def _fetch_dynamic(self, url: str) -> Optional[str]:
        """Fetch page using Playwright (for JS-rendered pages)."""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                await page.goto(url, timeout=30000, wait_until="networkidle")

                # Try clicking "load more" buttons
                for _ in range(3):
                    try:
                        load_more = page.locator(
                            "button:has-text('load more'), button:has-text('Load More'), "
                            "button:has-text('Show More'), a:has-text('Load More')"
                        )
                        if await load_more.count() > 0:
                            await load_more.first.click()
                            await page.wait_for_timeout(2000)
                    except Exception:
                        break

                html = await page.content()
                await browser.close()
                return html

        except ImportError:
            logger.warning("Playwright not installed. Install with: pip install playwright && playwright install chromium")
            return None
        except Exception as e:
            logger.warning(f"Dynamic fetch failed for {url}: {e}")
            return None

    # ===================== Detection Methods =====================

    def _detect_pagination(self, soup, url: str) -> tuple[bool, int]:
        """Detect pagination elements on the page."""
        pagination_selectors = [
            "nav[aria-label*='pagination']",
            ".pagination",
            "[class*='pagination']",
            "[class*='pager']",
            ".page-numbers",
            "ul.pages",
        ]

        for selector in pagination_selectors:
            elements = soup.select(selector)
            if elements:
                # Try to find the max page number
                page_numbers = []
                for el in elements:
                    for link in el.find_all("a"):
                        text = link.get_text(strip=True)
                        if text.isdigit():
                            page_numbers.append(int(text))

                max_page = max(page_numbers) if page_numbers else 5
                return True, min(max_page, 50)

        # Check for next/prev buttons
        next_patterns = [
            "a:has-text('Next')",
            "a:has-text('next')",
            "a[rel='next']",
            "[class*='next']",
            "a:has-text('→')",
            "a:has-text('»')",
        ]

        for selector in next_patterns:
            try:
                if soup.select_one(selector.replace(":has-text", ":contains") if ":has-text" in selector else selector):
                    return True, 5
            except Exception:
                pass

        # Check for next text in links
        for link in soup.find_all("a"):
            text = link.get_text(strip=True).lower()
            if text in ["next", "next page", "next →", "»", ">"]:
                return True, 5

        return False, 1

    def _detect_exhibitor_blocks(self, soup) -> tuple[int, list[str]]:
        """Detect repeated exhibitor listing blocks and what fields are present."""
        # Common selectors for exhibitor cards/rows
        card_selectors = [
            "[class*='exhibitor']",
            "[class*='company']",
            "[class*='participant']",
            "[class*='card']",
            "[class*='listing']",
            "[class*='directory']",
            "article",
            ".list-item",
            "[class*='item']",
        ]

        best_count = 0
        detected_fields = set()

        for selector in card_selectors:
            elements = soup.select(selector)
            if len(elements) >= 3:  # At least 3 repeated blocks
                if len(elements) > best_count:
                    best_count = len(elements)

        # If no specific selectors found, look at repeated structures
        if best_count < 3:
            # Look at divs with many similar children
            for parent in soup.find_all(["div", "ul", "section"]):
                children = parent.find_all(recursive=False)
                if len(children) >= 3:
                    # Check if children have similar structure
                    tags = [child.name for child in children[:10]]
                    if len(set(tags)) <= 2:  # Most children have same tag
                        best_count = max(best_count, len(children))

        # Detect fields from page text
        page_text = soup.get_text(separator=" ").lower()
        field_keywords = {
            "company_name": ["company", "exhibitor", "name"],
            "booth": ["booth", "stand", "booth no", "stand no"],
            "hall": ["hall", "pavilion"],
            "country": ["country", "nation"],
            "category": ["category", "sector", "industry"],
            "website": ["website", "web", "url", "www"],
            "email": ["email", "@"],
            "phone": ["phone", "tel", "mobile"],
            "description": ["description", "about", "profile"],
        }

        for field, keywords in field_keywords.items():
            for keyword in keywords:
                if keyword in page_text:
                    detected_fields.add(field)
                    break

        return best_count, sorted(detected_fields)

    def _detect_detail_pages(self, soup, base_url: str) -> bool:
        """Detect if exhibitor cards link to detail/profile pages."""
        # Look for links within card-like elements
        card_selectors = [
            "[class*='exhibitor'] a",
            "[class*='company'] a",
            "[class*='card'] a",
            "[class*='listing'] a",
            "article a",
        ]

        for selector in card_selectors:
            links = soup.select(selector)
            if len(links) >= 3:
                # Check if links point to detail pages (not pagination, not external)
                detail_count = 0
                for link in links[:10]:
                    href = link.get("href", "")
                    if href and not href.startswith("#") and "page" not in href.lower():
                        detail_count += 1

                if detail_count >= 2:
                    return True

        return False

    def _get_pagination_urls(self, soup, base_url: str, max_pages: int) -> list[str]:
        """Extract pagination URLs from the page."""
        urls = []
        parsed = urlparse(base_url)

        # Find all pagination links
        pagination = soup.select(
            "nav[aria-label*='pagination'] a, .pagination a, [class*='pagination'] a, "
            "[class*='pager'] a, .page-numbers a"
        )

        for link in pagination:
            href = link.get("href", "")
            if href and href != "#":
                full_url = urljoin(base_url, href)
                if full_url not in urls and full_url != base_url:
                    urls.append(full_url)

        # If we found next-page links, also try generating sequential URLs
        if not urls:
            # Try common pagination URL patterns
            for link in soup.find_all("a"):
                href = link.get("href", "")
                text = link.get_text(strip=True).lower()
                if text in ["next", "next page", "2", "→", "»"]:
                    if href and href != "#":
                        next_url = urljoin(base_url, href)
                        urls.append(next_url)

                        # Try to generate more pages from the pattern
                        page_match = re.search(r"[?&]page=(\d+)", next_url)
                        if page_match:
                            for p in range(3, max_pages + 1):
                                gen_url = re.sub(
                                    r"([?&]page=)\d+", f"\\g<1>{p}", next_url
                                )
                                urls.append(gen_url)
                        break

        return urls[:max_pages - 1]

    # ===================== Extraction Methods =====================

    def _extract_exhibitors_from_page(self, soup, base_url: str) -> list[dict]:
        """Extract exhibitor data from a listing page."""
        exhibitors = []

        # Try multiple strategies to find exhibitor blocks
        blocks = self._find_exhibitor_blocks(soup)

        for block in blocks:
            exhibitor = self._extract_exhibitor_from_block(block, base_url)
            if exhibitor and exhibitor.get("company_name"):
                exhibitors.append(exhibitor)

        # If no structured blocks found, try table extraction
        if not exhibitors:
            exhibitors = self._extract_from_tables(soup, base_url)

        return exhibitors

    def _find_exhibitor_blocks(self, soup) -> list:
        """Find repeated DOM blocks that likely represent exhibitors."""
        selectors = [
            "[class*='exhibitor']",
            "[class*='company']",
            "[class*='participant']",
            "[class*='directory'] [class*='item']",
            "[class*='listing'] [class*='item']",
            "[class*='card']",
            "article",
        ]

        for selector in selectors:
            blocks = soup.select(selector)
            if len(blocks) >= 2:
                return blocks

        # Fallback: find the parent with the most similar children
        best_parent = None
        best_count = 0

        for parent in soup.find_all(["div", "ul", "section", "main"]):
            children = parent.find_all(recursive=False)
            if len(children) >= 3:
                tags = [c.name for c in children]
                if tags.count(tags[0]) >= 3:
                    if len(children) > best_count:
                        best_count = len(children)
                        best_parent = parent

        if best_parent:
            return best_parent.find_all(recursive=False)

        return []

    def _extract_exhibitor_from_block(self, block, base_url: str) -> dict:
        """Extract exhibitor data from a single DOM block."""
        data = {}

        text = block.get_text(separator="\n", strip=True)

        # Company name: typically the first heading or strong text
        name_el = block.find(["h1", "h2", "h3", "h4", "h5", "strong", "b"])
        if name_el:
            data["company_name"] = name_el.get_text(strip=True)[:150]
        elif text:
            # Use first meaningful line
            lines = [l.strip() for l in text.split("\n") if l.strip() and len(l.strip()) > 2]
            if lines:
                data["company_name"] = lines[0][:150]

        # Profile URL
        link = block.find("a", href=True)
        if link:
            href = link.get("href", "")
            if href and not href.startswith("#") and "page" not in href.lower():
                data["profile_url"] = urljoin(base_url, href)

        # Booth/Stand number
        booth_patterns = [
            r"(?:booth|stand)\s*(?:no\.?|number|#|:)?\s*([A-Z]?\d{1,5}[A-Z]?(?:[-/]\d{0,4})?)",
            r"\b([A-Z]{1,3}[-\s]?\d{1,5})\b",
        ]
        for pattern in booth_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and "booth_number" not in data:
                data["booth_number"] = match.group(1).strip().upper()

        # Hall
        hall_match = re.search(r"(?:hall|pavilion)\s*[-:]?\s*(\w+)", text, re.IGNORECASE)
        if hall_match:
            data["hall"] = hall_match.group(1).strip()

        # Country
        country_el = block.select_one("[class*='country'], [class*='location']")
        if country_el:
            data["country"] = country_el.get_text(strip=True)[:50]

        # Category
        cat_el = block.select_one("[class*='category'], [class*='sector'], [class*='industry']")
        if cat_el:
            data["category"] = cat_el.get_text(strip=True)[:100]

        # Description
        desc_el = block.select_one("[class*='description'], [class*='summary'], p")
        if desc_el and desc_el != name_el:
            desc = desc_el.get_text(strip=True)
            if len(desc) > 10:
                data["description"] = desc[:300]

        # Website
        for a in block.find_all("a", href=True):
            href = a.get("href", "")
            if href.startswith("http") and urlparse(href).netloc not in urlparse(base_url).netloc:
                text_hint = a.get_text(strip=True).lower()
                if any(kw in text_hint for kw in ["website", "visit", "www"]) or any(
                    kw in href.lower() for kw in ["www.", ".com", ".org", ".net"]
                ):
                    data["website"] = href

        # Email
        email_match = re.search(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text
        )
        if email_match:
            data["email"] = email_match.group(0)

        # Phone
        phone_match = re.search(
            r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}", text
        )
        if phone_match:
            data["phone"] = phone_match.group(0).strip()

        # Social links
        for a in block.find_all("a", href=True):
            href = a.get("href", "").lower()
            if "linkedin.com" in href:
                data["linkedin"] = a.get("href", "")
            elif "twitter.com" in href or "x.com" in href:
                data["twitter"] = a.get("href", "")
            elif "facebook.com" in href:
                data["facebook"] = a.get("href", "")

        return data

    def _extract_from_tables(self, soup, base_url: str) -> list[dict]:
        """Extract exhibitor data from HTML tables."""
        exhibitors = []

        for table in soup.find_all("table"):
            headers = []
            for th in table.find_all("th"):
                headers.append(th.get_text(strip=True).lower())

            for row in table.find_all("tr"):
                cells = row.find_all(["td", "th"])
                if len(cells) < 2:
                    continue

                exhibitor = {}
                for i, cell in enumerate(cells):
                    text = cell.get_text(strip=True)
                    header = headers[i] if i < len(headers) else ""

                    if any(kw in header for kw in ["name", "company", "exhibitor"]):
                        exhibitor["company_name"] = text
                    elif any(kw in header for kw in ["booth", "stand"]):
                        exhibitor["booth_number"] = text
                    elif "hall" in header:
                        exhibitor["hall"] = text
                    elif "country" in header:
                        exhibitor["country"] = text
                    elif "category" in header or "sector" in header:
                        exhibitor["category"] = text
                    elif not exhibitor.get("company_name") and len(text) > 3:
                        exhibitor["company_name"] = text

                    # Check for links
                    link = cell.find("a", href=True)
                    if link:
                        exhibitor["profile_url"] = urljoin(base_url, link["href"])

                if exhibitor.get("company_name"):
                    exhibitors.append(exhibitor)

        return exhibitors

    async def _scrape_detail_page(
        self, url: str, extract_contacts: bool
    ) -> dict:
        """Scrape additional data from an exhibitor detail page."""
        data = {}
        try:
            html = self._fetch_static(url)
            if not html:
                return data

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "lxml")
            text = soup.get_text(separator="\n", strip=True)

            # Extract additional fields from detail page
            if extract_contacts:
                # Email
                email_match = re.search(
                    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text
                )
                if email_match:
                    data["email"] = email_match.group(0)

                # Phone
                phone_match = re.search(
                    r"(?:phone|tel|mobile)[:\s]*([+\d\s().-]{7,20})", text, re.IGNORECASE
                )
                if phone_match:
                    data["phone"] = phone_match.group(1).strip()

                # Social links
                for a in soup.find_all("a", href=True):
                    href = a.get("href", "").lower()
                    if "linkedin.com" in href:
                        data["linkedin"] = a.get("href", "")
                    elif "twitter.com" in href or "x.com" in href:
                        data["twitter"] = a.get("href", "")
                    elif "facebook.com" in href:
                        data["facebook"] = a.get("href", "")

            # Website
            for a in soup.find_all("a", href=True):
                href = a.get("href", "")
                text_hint = a.get_text(strip=True).lower()
                if (
                    href.startswith("http")
                    and any(kw in text_hint for kw in ["website", "visit", "www", "site"])
                ):
                    data["website"] = href
                    break

            # Description / profile text
            desc_selectors = [
                "[class*='description']",
                "[class*='about']",
                "[class*='profile']",
                "[class*='content'] p",
                "article p",
                "main p",
            ]
            for selector in desc_selectors:
                el = soup.select_one(selector)
                if el:
                    desc = el.get_text(strip=True)
                    if len(desc) > 20:
                        data["description"] = desc[:500]
                        break

            # Country / city from text
            address_el = soup.select_one("[class*='address'], [class*='location']")
            if address_el:
                addr = address_el.get_text(strip=True)
                data.setdefault("country", addr.split(",")[-1].strip()[:50] if "," in addr else "")
                if "," in addr:
                    data.setdefault("city", addr.split(",")[0].strip()[:50])

            # Category
            cat_el = soup.select_one("[class*='category'], [class*='sector']")
            if cat_el:
                data.setdefault("category", cat_el.get_text(strip=True)[:100])

            # Booth from detail page
            booth_match = re.search(
                r"(?:booth|stand)\s*(?:no\.?|number|#|:)?\s*([A-Z]?\d{1,5}[A-Z]?)",
                text,
                re.IGNORECASE,
            )
            if booth_match:
                data.setdefault("booth_number", booth_match.group(1).strip().upper())

            # Add small delay
            await asyncio.sleep(0.5)

        except Exception as e:
            logger.warning(f"Detail page scrape failed for {url}: {e}")

        return data

    # ===================== Normalization =====================

    def _normalize_and_dedup(self, exhibitors: list[dict]) -> list[dict]:
        """Normalize field values and remove duplicates."""
        seen = set()
        unique = []

        for ex in exhibitors:
            # Normalize company name
            name = ex.get("company_name", "").strip()
            if not name:
                continue

            # Dedup by company name
            name_key = name.lower().replace(" ", "")
            if name_key in seen:
                continue
            seen.add(name_key)

            # Clean up fields
            for key, val in list(ex.items()):
                if isinstance(val, str):
                    ex[key] = val.strip()
                if not val:
                    ex[key] = ""

            unique.append(ex)

        return unique
