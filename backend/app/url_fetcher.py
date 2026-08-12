"""Server-side URL fetching and text extraction."""

import logging

import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException

logger = logging.getLogger("app.url_fetcher")


async def fetch_url_content(url: str) -> str:
    """Fetch a URL and return its extracted, readable text.

    Raises HTTPException(400) for bad input, (502) for fetch failures
    the caller isn't responsible for.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(
                url, headers={"User-Agent": "AI-Knowledge-Inbox/0.1"}
            )
            response.raise_for_status()
    except httpx.TimeoutException:
        logger.warning("url_fetch_timeout", extra={"url": url})
        raise HTTPException(status_code=502, detail=f"Timed out fetching URL: {url}")
    except httpx.HTTPStatusError as exc:
        logger.warning(
            "url_fetch_http_error",
            extra={"url": url, "status": exc.response.status_code},
        )
        raise HTTPException(
            status_code=502,
            detail=f"URL returned an error status ({exc.response.status_code}): {url}",
        )
    except httpx.RequestError as exc:
        logger.warning("url_fetch_failed", extra={"url": url, "error": str(exc)})
        raise HTTPException(status_code=400, detail=f"Could not reach URL: {url}")

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type:
        raise HTTPException(
            status_code=400,
            detail=f"URL did not return HTML content (got '{content_type}'): {url}",
        )

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    if not text:
        raise HTTPException(
            status_code=400, detail=f"No readable text content found at: {url}"
        )

    return text
