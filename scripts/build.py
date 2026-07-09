#!/usr/bin/env python3
"""Build dev.html from data/site.yaml and dev.template.html."""

import html
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "site.yaml"
TEMPLATE_FILE = ROOT / "dev.template.html"
OUTPUT_FILE = ROOT / "dev.html"


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


def render_card(item: dict, *, category_attr: str | None = None) -> str:
    attrs_parts = []
    if category_attr and item.get("category"):
        attrs_parts.append(f'data-{category_attr}="{esc(item["category"])}"')
    attrs = f' {" ".join(attrs_parts)}' if attrs_parts else ""
    return f"""                    <a href="{esc(item["url"])}" target="_blank" rel="noopener noreferrer" class="card"{attrs}>{render_logo(item)}
                        <h3>{esc(item["name"])}</h3>
                        <p>{esc(item["description"])}</p>
                    </a>"""


def render_continents(continents: list, orgs: list, *, include_visitable: bool = True) -> str:
    org_continents = {org.get("continent") for org in orgs if org.get("continent")}
    has_visitable = include_visitable and any(org.get("visitable") for org in orgs)

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


def render_filter_chips(categories: list, attr: str) -> str:
    lines = []
    for index, category in enumerate(categories):
        cid = category["id"]
        active = " is-active" if index == 0 else ""
        selected = ' aria-selected="true"' if index == 0 else ""
        lines.append(
            f'                        <button class="chip{active}" data-{attr}="{esc(cid)}" role="tab"{selected}>{esc(category["label"])}</button>'
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
    items = []
    for item in section.get("emulators", []):
        items.append({**item, "category": "emulator"})
    for item in section.get("dumping_tools", []):
        items.append({**item, "category": "dumping_tool"})
    return items


def visitable_orgs(orgs: list) -> list:
    return [org for org in orgs if org.get("visitable")]


def render_hero_tagline(lines: list) -> str:
    return "".join(f'<span class="hero-tagline-line">{esc(line)}</span>' for line in lines)


def render_hero_tagline_default(hero: dict) -> str:
    taglines = hero.get("taglines", [])
    if not taglines:
        return ""
    return render_hero_tagline(taglines[0]["lines"])


def render_hero_taglines_json(hero: dict) -> str:
    taglines = hero.get("taglines", [])
    return json.dumps(taglines)


def render_hero_blurb(hero: dict) -> str:
    paragraphs = hero.get("blurb", [])
    lines = []
    for paragraph in paragraphs:
        lines.append(f'                        <p>{esc(paragraph)}</p>')
    return "\n".join(lines)


def render_hero_stats(data: dict) -> str:
    orgs = data["organizations"]
    sections = [
        (len(orgs), "Organizations"),
        (len(visitable_orgs(orgs)), "Visit in Person"),
        (len(data["guides"]), "Guides"),
        (len(data.get("communities", [])), "Communities"),
        (len(opensource_items(data)), "Open Source"),
        (len(data["resources"]), "Resources"),
    ]
    lines = []
    for count, label in sections:
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
    suffix = esc(credit.get("suffix", ""))
    return (
        f'<p class="footer-credit">{esc(credit["text"])} '
        f'<a href="{esc(credit["url"])}" target="_blank" rel="noopener noreferrer">'
        f'{esc(credit["name"])}</a>{suffix}</p>'
    )


def render_suggest_block(site: dict) -> str:
    suggest = site.get("suggest")
    if not suggest:
        return ""
    link_text = esc(suggest.get("link_text", "Suggest a resource"))
    return (
        f'<p class="suggest-block">{esc(suggest["text"])} '
        f'<a href="{esc(suggest["url"])}" target="_blank" rel="noopener noreferrer">'
        f'{link_text}</a>.</p>'
    )


def build() -> None:
    data = yaml.safe_load(DATA_FILE.read_text(encoding="utf-8"))
    template = TEMPLATE_FILE.read_text(encoding="utf-8")

    site = data["site"]
    hero = site["hero"]

    orgs = data["organizations"]
    visitable = visitable_orgs(orgs)
    community = (
        data["guides"]
        + data.get("communities", [])
        + opensource_items(data)
        + data["resources"]
    )

    replacements = {
        "{{title}}": esc(site["title"]),
        "{{hero_tagline_default}}": render_hero_tagline_default(hero),
        "{{hero_taglines_json}}": render_hero_taglines_json(hero),
        "{{hero_blurb}}": render_hero_blurb(hero),
        "{{footer}}": esc(site["footer"]),
        "{{footer_credit}}": render_footer_credit(site),
        "{{suggest_block}}": render_suggest_block(site),
        "{{hero_stats}}": render_hero_stats(data),
        "{{marquee_orgs}}": render_marquee_row(orgs, reverse=False),
        "{{marquee_community}}": render_marquee_row(community, reverse=True),
        "{{continents}}": render_continents(data["continents"], orgs, include_visitable=True),
        "{{visit_continents}}": render_continents(data["continents"], visitable, include_visitable=False),
        "{{organizations}}": "\n\n".join(render_org_card(org) for org in orgs),
        "{{visit_in_person}}": "\n\n".join(render_org_card(org) for org in visitable),
        "{{guides}}": "\n\n".join(render_card(guide) for guide in data["guides"]),
        "{{communities}}": "\n\n".join(render_card(item) for item in data.get("communities", [])),
        "{{resource_categories}}": render_filter_chips(data["resource_categories"], "category"),
        "{{resources}}": "\n\n".join(
            render_card(resource, category_attr="category") for resource in data["resources"]
        ),
        "{{opensource_categories}}": render_filter_chips(data["opensource_categories"], "category"),
        "{{opensource}}": "\n\n".join(
            render_card(item, category_attr="category") for item in opensource_items(data)
        ),
    }

    output = template
    for key, value in replacements.items():
        output = output.replace(key, value)

    OUTPUT_FILE.write_text(output, encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    build()
