#!/usr/bin/env python3
"""Download missing logos from public sources."""

from __future__ import annotations

import re
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlparse

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "site.yaml"
LOGOS_DIR = ROOT / "assets" / "logos"
USER_AGENT = "Mozilla/5.0 (compatible; preserve.games-logo-fetch/1.0)"
SECTIONS = ("organizations", "guides", "resources")
OPENSOURCE_GROUPS = ("emulators", "dumping_tools")


def iter_logo_items(data: dict):
    for section in SECTIONS:
        for item in data[section]:
            yield section, item
    opensource = data.get("opensource", {})
    for group in OPENSOURCE_GROUPS:
        for item in opensource.get(group, []):
            yield f"opensource.{group}", item


def domain(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def default_slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    return slug[:48].strip("-")


def sniff_ext(data: bytes) -> str:
    if data[:4] == b"\x89PNG":
        return ".png"
    if data[:3] == b"GIF":
        return ".gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    if data.lstrip()[:5] == b"<?xml" or b"<svg" in data[:256]:
        return ".svg"
    if data[:2] == b"\xff\xd8":
        return ".jpg"
    if data[:4] == b"\x00\x00\x01\x00" or data[:4] == b"\x00\x00\x02\x00":
        return ".ico"
    return ".png"


def fetch(url: str) -> bytes | None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            data = response.read()
    except (urllib.error.URLError, TimeoutError):
        return None
    if len(data) < 200:
        return None
    return data


def scrape_icon_urls(site_url: str) -> list[str]:
    urls: list[str] = []
    try:
        request = urllib.request.Request(site_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=25) as response:
            html = response.read().decode("utf-8", errors="ignore")
    except (urllib.error.URLError, TimeoutError):
        return urls

    for tag in re.findall(r"<link[^>]+>", html, re.I):
        if "icon" not in tag.lower():
            continue
        match = re.search(r'href=["\']([^"\']+)', tag)
        if match:
            urls.append(urljoin(site_url, match.group(1)))

    og = re.search(
        r'property=["\']og:image["\'][^>]*content=["\']([^"\']+)|content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']',
        html,
        re.I,
    )
    if og:
        urls.append(urljoin(site_url, og.group(1) or og.group(2)))

    for match in re.findall(
        r'(?:src|href)=["\']([^"\']+(?:logo|favicon)[^"\']*\.(?:png|svg|jpg|webp|ico))["\']',
        html,
        re.I,
    ):
        urls.append(urljoin(site_url, match))

    return urls


def candidate_urls(site_url: str, site_domain: str) -> list[str]:
    parsed = urlparse(site_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    urls = [
        urljoin(origin, "/apple-touch-icon.png"),
        urljoin(origin, "/apple-touch-icon-precomposed.png"),
        urljoin(origin, "/favicon.ico"),
        urljoin(origin, "/favicon.png"),
        f"https://www.google.com/s2/favicons?domain={site_domain}&sz=128",
        f"https://icons.duckduckgo.com/ip3/{site_domain}.ico",
    ]
    urls.extend(scrape_icon_urls(site_url))
    if site_domain != domain(site_url):
        urls.extend(scrape_icon_urls(origin + "/"))

    seen: set[str] = set()
    unique: list[str] = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique


def logo_path_for_item(item: dict) -> tuple[str, str]:
    if item.get("logo"):
        rel = item["logo"]
        slug = Path(rel).stem
    else:
        slug = default_slug(item["name"])
        rel = f"assets/logos/{slug}.png"
    return slug, rel


def ensure_logo_field(content: str, item: dict, rel_path: str) -> str:
    if item.get("logo"):
        return content
    name = item["name"]
    pattern = re.compile(
        rf"(- name: {re.escape(name)}\n(?:  .+\n)*?)(    url: )",
        re.MULTILINE,
    )
    replacement = rf"\1    logo: {rel_path}\n    logo_alt: {re.escape(name)} logo\n\2"
    return pattern.sub(replacement, content, count=1)


def main() -> None:
    LOGOS_DIR.mkdir(parents=True, exist_ok=True)
    data = yaml.safe_load(DATA_FILE.read_text(encoding="utf-8"))
    content = DATA_FILE.read_text(encoding="utf-8")
    updated_paths: list[tuple[str, str]] = []
    added_fields = False

    for section, item in iter_logo_items(data):
        slug, rel_path = logo_path_for_item(item)
        if not item.get("logo"):
            item["logo"] = rel_path
            content = ensure_logo_field(content, item, rel_path)
            added_fields = True

        logo_path = ROOT / rel_path
        if logo_path.exists() and logo_path.stat().st_size > 300:
            print(f"skip  {section:14} {logo_path.name}")
            continue

        original_logo = item["logo"]
        site_domain = domain(item["url"])
        saved = False

        for candidate in candidate_urls(item["url"], site_domain):
            data_bytes = fetch(candidate)
            if not data_bytes:
                continue

            ext = sniff_ext(data_bytes)
            dest = LOGOS_DIR / f"{slug}{ext}"
            dest.write_bytes(data_bytes)

            new_rel = f"assets/logos/{dest.name}"
            item["logo"] = new_rel
            if new_rel != original_logo:
                if original_logo in content:
                    updated_paths.append((original_logo, new_rel))
                else:
                    content = ensure_logo_field(content, item, new_rel)
                    added_fields = True

            print(f"saved {section:14} {dest.name} <- {candidate}")
            saved = True
            break

        if not saved:
            print(f"fail  {section:14} {slug} ({site_domain})")

    if updated_paths:
        for old_path, new_path in updated_paths:
            content = content.replace(f"logo: {old_path}", f"logo: {new_path}", 1)

    if updated_paths or added_fields:
        DATA_FILE.write_text(content, encoding="utf-8")
        print("\nUpdated data/site.yaml")


if __name__ == "__main__":
    main()
