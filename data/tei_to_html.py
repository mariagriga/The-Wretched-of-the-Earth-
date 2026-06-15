from lxml import etree

TEI = "http://www.tei-c.org/ns/1.0"
NS  = {"t": TEI}

TAG_MAP = {
    f"{{{TEI}}}persName": ("person",  "Person"),
    f"{{{TEI}}}placeName":("place",   "Place"),
    f"{{{TEI}}}orgName":  ("org",     "Organisation"),
    f"{{{TEI}}}title":    ("work",    "Text"),
    f"{{{TEI}}}quote":    ("quote",   "Quotation"),
}

def get_entity_class(el):
    """Return (css_class, label) for a TEI element."""
    tag = el.tag
    if tag in TAG_MAP:
        return TAG_MAP[tag]
    if tag == f"{{{TEI}}}rs":
        t = el.get("type", "")
        if t == "concept":  return ("concept", "Concept")
        if t == "event":    return ("event",   "Event")
    return None

def el_to_html(el):
    info = get_entity_class(el)
    ref  = el.get("ref", "")
    inner = (el.text or "")
    for child in el:
        inner += el_to_html(child)
        if child.tail:
            inner += child.tail

    if info:
        css, label = info
        tooltip = label
        if ref:
            tooltip += f' · <a href="{ref}" target="_blank">↗ authority</a>'
        return (
            f'<span class="entity {css}" tabindex="0">'
            f'<span class="entity-tooltip">{tooltip}</span>'
            f'{inner}</span>'
        )
    return inner

def paragraphs_to_html(root):
    html_parts = []
    body = root.find(".//t:body", NS)
    if body is None: return "<p>No body found.</p>"

    for div in body.iter(f"{{{TEI}}}div"):
        head = div.find(f"{{{TEI}}}head")
        if head is not None:
            html_parts.append(f'<h3 class="tei-head">{head.text or ""}</h3>')
        for p in div.findall(f"{{{TEI}}}p"):
            parts = [p.text or ""]
            for child in p:
                parts.append(el_to_html(child))
                if child.tail: parts.append(child.tail)
            html_parts.append(f'<p class="tei-p">{"".join(parts)}</p>')
    return "\n".join(html_parts)

def back_persons(root):
    rows = []
    for person in root.findall(".//t:listPerson/t:person", NS):
        name = person.findtext(f"{{{TEI}}}persName", default="—")
        bdate = person.find(f"{{{TEI}}}birth").get("when") if person.find(f"{{{TEI}}}birth") is not None else ""
        birth = person.findtext(f".//{{{TEI}}}birth/{{{TEI}}}placeName", default="")
        occ   = person.findtext(f"{{{TEI}}}occupation", default="")
        viaf  = person.find(f"{{{TEI}}}idno[@type='VIAF']")
        wd    = person.find(f"{{{TEI}}}idno[@type='Wikidata']")
        links = f'<a href="{viaf.text}" target="_blank">VIAF</a> ' if viaf is not None else ""
        links += f'<a href="{wd.text}" target="_blank">WD</a>' if wd is not None else ""
        rows.append(f"<tr><td>{name}</td><td>{bdate}</td><td>{birth}</td><td>{occ}</td><td>{links}</td></tr>")
    return "\n".join(rows)

def back_places(root):
    rows = []
    for place in root.findall(".//t:listPlace/t:place", NS):
        name = place.findtext(f"{{{TEI}}}placeName", default="—")
        geo  = place.findtext(f".//{{{TEI}}}geo", default="")
        note = place.findtext(f"{{{TEI}}}note", default="")
        gn   = place.find(f"{{{TEI}}}idno[@type='GeoNames']")
        wd   = place.find(f"{{{TEI}}}idno[@type='Wikidata']")
        links = f'<a href="{gn.text}" target="_blank">GN</a> ' if gn is not None else ""
        links += f'<a href="{wd.text}" target="_blank">WD</a>' if wd is not None else ""
        rows.append(f"<tr><td>{name}</td><td>{geo}</td><td>{note}</td><td>{links}</td></tr>")
    return "\n".join(rows)

def back_events(root):
    rows = []
    for ev in root.findall(".//t:listEvent/t:event", NS):
        label = ev.findtext(f"{{{TEI}}}label", default="—")
        date_el = ev.find(f"{{{TEI}}}date")
        date_str = f"{date_el.get('from', '')}–{date_el.get('to', '')}" if date_el is not None and date_el.get('from') else (date_el.get('when') if date_el is not None else "")
        desc = ev.findtext(f"{{{TEI}}}desc", default="")
        wd = ev.find(f"{{{TEI}}}idno[@type='Wikidata']")
        link = f'<a href="{wd.text}" target="_blank">WD</a>' if wd is not None else ""
        rows.append(f"<tr><td>{label}</td><td>{date_str}</td><td>{desc}</td><td>{link}</td></tr>")
    return "\n".join(rows)

def back_concepts(root):
    rows = []
    for label in root.findall(".//t:listConcept/t:label", NS):
        item = label.getnext()
        if item is not None and item.tag == f"{{{TEI}}}item":
            term = label.text or "—"
            gloss = item.findtext(f"{{{TEI}}}gloss", default="")
            wd = item.find(f"{{{TEI}}}idno[@type='Wikidata']")
            aat = item.find(f"{{{TEI}}}idno[@type='GettyAAT']")
            links = f'<a href="{wd.text}" target="_blank">WD</a> ' if wd is not None else ""
            links += f'<a href="{aat.text}" target="_blank">AAT</a>' if aat is not None else ""
            rows.append(f"<tr><td>{term}</td><td>{gloss}</td><td>{links}</td></tr>")
    return "\n".join(rows)

def back_bibl(root):
    rows = []
    for bibl in root.findall(".//t:listBibl/t:bibl", NS):
        title = bibl.findtext(f"{{{TEI}}}title", default="—")
        author = bibl.findtext(f"{{{TEI}}}author", default="—")
        date = bibl.get("when") or bibl.findtext(f"{{{TEI}}}date", default="")
        wd = bibl.find(f"{{{TEI}}}idno[@type='Wikidata']")
        link = f'<a href="{wd.text}" target="_blank">WD</a>' if wd is not None else ""
        rows.append(f"<tr><td>{title}</td><td>{author}</td><td>{date}</td><td>{link}</td></tr>")
    return "\n".join(rows)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/><title>TEI Output — The Wretched of the Earth</title>
<style>
body { background: #0c0b10; color: #e8e4dc; font-family: Georgia, serif; line-height: 1.8; padding: 3rem 10%; }
h1 { font-weight: normal; color: #f0ece4; }
.tei-head { text-transform: uppercase; letter-spacing: .06em; color: rgba(232,228,220,.4); margin: 2rem 0 .5rem; }
.entity { border-bottom: 1px solid rgba(255,255,255,.25); position: relative; cursor: help; }
.person { color:#e0b3b3; } .place { color:#b3d1e0; }
.org { color:#c9b3e0; } .work { color:#e0d6b3; }
.concept { color:#b3e0c2; } .event { color:#e0c4a0; }
.entity.quote { font-style: italic; color:#e0c4a0; border-bottom: none; }
.entity-tooltip { display: none; position: absolute; bottom: 100%; left: 0; white-space: nowrap; background: #222; color: #e8e4dc; padding: 4px 8px; border-radius: 3px; font-family: sans-serif; font-size: 0.7rem; z-index: 10; }
.entity-tooltip a { color: #b3d1e0; }
.entity:hover .entity-tooltip, .entity:focus .entity-tooltip { display: block; }
table { width: 100%; border-collapse: collapse; margin-top: 2rem; }
th, td { border: 1px solid #333; padding: 8px; text-align: left; font-size: 0.8rem; }
</style>
</head>
<body>
<h1>The Wretched of the Earth</h1>
{body_html}
<h2>Persons</h2><table>{persons_html}</table>
<h2>Places</h2><table>{places_html}</table>
<h2>Events</h2><table>{events_html}</table>
<h2>Concepts</h2><table>{concepts_html}</table>
<h2>Bibliography</h2><table>{bibl_html}</table>
</body>
</html>
"""

def main():
    tree = etree.parse("tei.xml")
    root = tree.getroot()
    replacements = {
        "{body_html}":     paragraphs_to_html(root),
        "{persons_html}":  back_persons(root),
        "{places_html}":   back_places(root),
        "{events_html}":   back_events(root),
        "{concepts_html}": back_concepts(root),
        "{bibl_html}":     back_bibl(root),
    }
    html = HTML_TEMPLATE
    for key, value in replacements.items():
        html = html.replace(key, value)
    with open("tei_output.html", "w", encoding="utf-8") as f: f.write(html)
    print("Done! Output saved to tei_output.html")

if __name__ == "__main__":
    main()
    