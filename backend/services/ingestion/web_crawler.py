import logging
import re
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

from pydantic import BaseModel, Field

from backend.services.ingestion.document_parser import DocumentParser

logger = logging.getLogger("EKOS-WebCrawler")

class CrawlType(str, Enum):
    SINGLE_PAGE = "SINGLE_PAGE"
    SITEMAP = "SITEMAP"
    RECURSIVE = "RECURSIVE"

class CrawlRequest(BaseModel):
    url: str
    crawl_type: CrawlType
    max_pages: int = 50
    max_depth: int = 3
    tenant_id: str

class CrawledPage(BaseModel):
    url: str
    title: str
    content: str
    metadata: Dict = Field(default_factory=dict)
    crawled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CrawlResult(BaseModel):
    request_url: str
    pages_crawled: int
    pages: List[CrawledPage]
    status: str
    errors: List[str] = Field(default_factory=list)

class WebCrawler:
    """Service for web crawling and sitemap ingestion."""
    
    async def crawl(self, request: CrawlRequest) -> CrawlResult:
        logger.info(f"Starting crawl for {request.url} with type {request.crawl_type}")
        pages = []
        errors = []
        status = "SUCCESS"
        
        try:
            if request.crawl_type == CrawlType.SINGLE_PAGE:
                page = await self._crawl_single_page(request.url)
                pages.append(page)
            elif request.crawl_type == CrawlType.SITEMAP:
                pages = await self._crawl_sitemap(request.url, request.max_pages)
            elif request.crawl_type == CrawlType.RECURSIVE:
                pages = await self._crawl_recursive(request.url, request.max_pages, request.max_depth)
        except Exception as e:
            logger.error(f"Error during crawl: {e}")
            errors.append(str(e))
            status = "FAILED"
            
        return CrawlResult(
            request_url=request.url,
            pages_crawled=len(pages),
            pages=pages,
            status=status,
            errors=errors
        )
        
    async def _crawl_single_page(self, url: str) -> CrawledPage:
        # Production: use aiohttp session
        logger.debug(f"Crawling single page: {url}")
        html = f"<html><head><title>Simulated {url}</title></head><body>Content for {url}</body></html>"
        
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        title = title_match.group(1) if title_match else "Unknown Title"
        
        content = self._extract_text(html)
        
        return CrawledPage(
            url=url,
            title=title,
            content=content,
            metadata={"source": "web_crawler"}
        )
        
    async def _crawl_sitemap(self, sitemap_url: str, max_pages: int) -> List[CrawledPage]:
        # Production: use aiohttp session
        logger.debug(f"Crawling sitemap: {sitemap_url}")
        xml_content = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f'<url><loc>{sitemap_url}/page1</loc></url>'
            f'<url><loc>{sitemap_url}/page2</loc></url>'
            '</urlset>'
        )
        
        urls = self._parse_sitemap_xml(xml_content)
        pages = []
        for i, url in enumerate(urls):
            if i >= max_pages:
                break
            try:
                page = await self._crawl_single_page(url)
                pages.append(page)
            except Exception as e:
                logger.warning(f"Failed to crawl {url} from sitemap: {e}")
                
        return pages
        
    async def _crawl_recursive(self, start_url: str, max_pages: int, max_depth: int) -> List[CrawledPage]:
        # Production: use aiohttp session
        logger.debug(f"Crawling recursively: {start_url}")
        visited = set()
        queue = [(start_url, 0)]
        pages = []
        
        base_domain = urlparse(start_url).netloc
        
        while queue and len(pages) < max_pages:
            url, depth = queue.pop(0)
            
            if url in visited or depth > max_depth:
                continue
                
            visited.add(url)
            
            try:
                # Simulate fetching HTML
                html = f"<html><head><title>Page {url}</title></head><body>Content <a href='/next'>Next</a></body></html>"
                page = await self._crawl_single_page(url)
                pages.append(page)
                
                if depth < max_depth:
                    links = self._extract_links(html, url)
                    for link in links:
                        link_domain = urlparse(link).netloc
                        if not link_domain or link_domain == base_domain:
                            if link not in visited:
                                queue.append((link, depth + 1))
            except Exception as e:
                logger.warning(f"Failed to crawl {url}: {e}")
                
        return pages
        
    def _extract_text(self, html: str) -> str:
        text = re.sub('<[^>]+>', ' ', html)
        return re.sub(r'\s+', ' ', text).strip()
        
    def _extract_links(self, html: str, base_url: str) -> List[str]:
        links = []
        matches = re.finditer(r'<a\s+(?:[^>]*?\s+)?href=["\'](.*?)["\']', html, re.IGNORECASE)
        for match in matches:
            href = match.group(1)
            full_url = urljoin(base_url, href)
            # Basic hash fragment removal
            full_url = full_url.split('#')[0]
            if full_url:
                links.append(full_url)
        return list(set(links))
        
    def _parse_sitemap_xml(self, xml_content: str) -> List[str]:
        urls = []
        matches = re.finditer(r'<loc>(.*?)</loc>', xml_content, re.IGNORECASE)
        for match in matches:
            urls.append(match.group(1).strip())
        return urls
