#!/usr/bin/env python3
"""Build index.html from data/site.yaml and dev.template.html."""

import html
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "site.yaml"
TEMPLATE_FILE = ROOT / "dev.template.html"
OUTPUT_FILE = ROOT / "index.html"


def esc(text: str) -> str:
    return html.escape(str(text))


def render_logo(item: dict) -> str:
    logo = item.get("logo")
    if not logo:
        return ""
    logo_alt = item.get("logo_alt", "")
    return f'\n                        <img src="{esc(logo)}" alt="{esc(logo_alt)}" class="card-logo" onerror="this.style.display=\'none\'">'


def render_org_card(org: dict) -> str:
    attrs_parts = []
    continent = org.get("continent")
    if continent:
        attrs_parts.append(f'data-continent="{esc(continent)}"')
    if org.get("visitable"):
        attrs_parts.append('data-visitable="true"')
    attrs = f' {" ".join(attrs_parts)}' if attrs_parts else ""
    return f"""                    <a href="{esc(org["url"])}" target="_blank" rel="noopener noreferrer" class="card"{attrs}>{render_logo(org)}
                        <h3>{esc(org["name"])}</h3>
                        <p>{esc(org["description"])}</p>
                    </a>"""


def render_card(item: dict) -> str:
    return f"""                    <a href="{esc(item["url"])}" target="_blank" rel="noopener noreferrer" class="card">{render_logo(item)}
                        <h3>{esc(item["name"])}</h3>
                        <p>{esc(item["description"])}</p>
                    </a>"""


def render_continents(continents: list, orgs: list) -> str:
    org_continents = {org.get("continent") for org in orgs if org.get("continent")}
    has_visitable = any(org.get("visitable") for org in orgs)

    lines = []
    for continent in continents:
        cid = continent["id"]
        if cid == "all":
            pass
        elif cid == "visitable":
            if not has_visitable:
                continue
        elif cid not in org_continents:
            continue

        active = " is-active" if cid == "all" else ""
        selected = ' aria-selected="true"' if cid == "all" else ""
        lines.append(
            f'                        <button class="chip{active}" data-continent="{esc(cid)}" role="tab"{selected}>{esc(continent["label"])}</button>'
        )
    return "\n".join(lines)


def render_marquee_item(item: dict) -> str:
    name = esc(item["name"])
    url = esc(item["url"])
    logo = item.get("logo")
    logo_alt = esc(item.get("logo_alt", name))
    logo_html = ""
    if logo:
        logo_html = (
            f'<img class="marquee-logo" src="{esc(logo)}" alt="{logo_alt}" width="80" height="36" '
            f'decoding="async" onerror="this.style.visibility=\'hidden\'">'
        )
    return (
        f'                        <a href="{url}" target="_blank" rel="noopener noreferrer" '
        f'class="marquee-item">{logo_html}<span class="marquee-name">{name}</span></a>'
    )


def render_marquee_row(items: list, reverse: bool = False) -> str:
    if not items:
        return ""
    block = "\n".join(render_marquee_item(item) for item in items)
    direction = " logo-marquee-reverse" if reverse else ""
    return f"""                <div class="logo-marquee{direction}">
                    <div class="logo-marquee-track">
{block}
{block}
                    </div>
                </div>"""


def opensource_items(data: dict) -> list:
    section = data.get("opensource", {})
    return section.get("emulators", []) + section.get("dumping_tools", [])


def render_hero_stats(data: dict) -> str:
    sections = [
        ("organizations", "Organizations"),
        ("guides", "Guides"),
        ("databases", "Databases"),
        ("opensource", "Open Source"),
        ("resources", "Resources"),
        ("unreleased", "Unreleased"),
    ]
    lines = []
    for key, label in sections:
        if key == "opensource":
            count = len(opensource_items(data))
        else:
            count = len(data[key])
        lines.append(
            f"""                    <div class="hero-stat">
                        <span class="hero-stat-num">{count}</span>
                        <span class="hero-stat-label">{esc(label)}</span>
                    </div>"""
        )
    return "\n".join(lines)


def render_footer_credit(site: dict) -> str:
    credit = site.get("footer_credit")
    if not credit:
        return ""
    return (
        f'<p class="footer-credit">{esc(credit["text"])} '
        f'<a href="{esc(credit["url"])}" target="_blank" rel="noopener noreferrer">'
        f'{esc(credit["name"])}</a></p>'
    )


def build() -> None:
    data = yaml.safe_load(DATA_FILE.read_text(encoding="utf-8"))
    template = TEMPLATE_FILE.read_text(encoding="utf-8")

    site = data["site"]
    hero = site["hero"]

    orgs = data["organizations"]
    community = (
        data["guides"]
        + data["databases"]
        + opensource_items(data)
        + data["resources"]
        + data["unreleased"]
    )
    opensource = data.get("opensource", {})

    replacements = {
        "{{title}}": esc(site["title"]),
        "{{hero_title}}": esc(hero["title"]),
        "{{hero_subtitle}}": esc(hero["subtitle"]),
        "{{hero_text}}": esc(hero["text"]),
        "{{footer}}": esc(site["footer"]),
        "{{footer_credit}}": render_footer_credit(site),
        "{{hero_stats}}": render_hero_stats(data),
        "{{marquee_orgs}}": render_marquee_row(orgs, reverse=False),
        "{{marquee_community}}": render_marquee_row(community, reverse=True),
        "{{continents}}": render_continents(data["continents"], orgs),
        "{{organizations}}": "\n\n".join(render_org_card(org) for org in data["organizations"]),
        "{{guides}}": "\n\n".join(render_card(guide) for guide in data["guides"]),
        "{{databases}}": "\n\n".join(render_card(db) for db in data["databases"]),
        "{{opensource_emulators}}": "\n\n".join(
            render_card(item) for item in opensource.get("emulators", [])
        ),
        "{{opensource_tools}}": "\n\n".join(
            render_card(item) for item in opensource.get("dumping_tools", [])
        ),
        "{{resources}}": "\n\n".join(render_card(resource) for resource in data["resources"]),
        "{{unreleased}}": "\n\n".join(render_card(item) for item in data["unreleased"]),
    }

    output = template
    for key, value in replacements.items():
        output = output.replace(key, value)

    OUTPUT_FILE.write_text(output, encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    build()
