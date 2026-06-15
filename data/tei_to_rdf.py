import xml.etree.ElementTree as ET
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, OWL, XSD, RDFS

TEI   = "http://www.tei-c.org/ns/1.0"
XMLID = "{http://www.w3.org/XML/1998/namespace}id"
NS    = {"t": TEI}

CRM    = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
FRBROO = Namespace("http://erlangen-crm.org/efrbroo/")

PERSON  = Namespace("https://w3id.org/wretchedoftheearth/person/")
PLACE   = Namespace("https://w3id.org/wretchedoftheearth/place/")
ORG     = Namespace("https://w3id.org/wretchedoftheearth/org/")
EVENT   = Namespace("https://w3id.org/wretchedoftheearth/event/")
CONCEPT = Namespace("https://w3id.org/wretchedoftheearth/concept/")
BIBL    = Namespace("https://w3id.org/wretchedoftheearth/bibl/")
TIME    = Namespace("https://w3id.org/wretchedoftheearth/time/")
EVNT    = Namespace("https://w3id.org/wretchedoftheearth/creation/")


def en(text):
    """English-tagged string literal."""
    return Literal(text, lang="en")


def reconcile(g, uri, el):
    """Link an entity to its authority files via owl:sameAs (from <idno>)."""
    for idno in el.findall("t:idno", NS):
        url = (idno.text or "").strip()
        if url:
            g.add((uri, OWL.sameAs, URIRef(url)))


def date_literal(value):
    """Typed Literal for a TEI @when value (full date or year only)."""
    parts = value.split("-")
    if len(parts) == 3:
        return Literal(value, datatype=XSD.date)
    if len(parts) == 1 and value.isdigit():
        return Literal(value, datatype=XSD.gYear)
    return Literal(value)


def build_graph(root):
    g = Graph()
    g.bind("crm", CRM); g.bind("frbroo", FRBROO); g.bind("owl", OWL)
    g.bind("rdfs", RDFS); g.bind("xsd", XSD)
    g.bind("person", PERSON); g.bind("place", PLACE)
    g.bind("org", ORG, override=True, replace=True)
    g.bind("event", EVENT); g.bind("concept", CONCEPT); g.bind("bibl", BIBL)
    g.bind("time", TIME, override=True, replace=True)

    book = BIBL["wretchedoftheearth"]
    g.add((book, RDF.type, FRBROO["F2_Expression"]))

    creation = EVNT["creationOfTheWretchedOfTheEarth"]
    g.add((creation, RDF.type, FRBROO["F28_Expression_Creation"]))
    g.add((creation, FRBROO["R17_created"], book))

    for person in root.findall(".//t:listPerson/t:person", NS):
        pid = person.get(XMLID)
        if not pid:
            continue
        uri = PERSON[pid]
        g.add((uri, RDF.type, CRM["E21_Person"]))
        name = person.findtext("t:persName", default="", namespaces=NS).strip()
        if name:
            g.add((uri, RDFS.label, en(name)))
        occupation = person.findtext("t:occupation", default="", namespaces=NS).strip()
        if occupation:
            g.add((uri, CRM["P2_has_type"], en(occupation)))

        birth = person.find("t:birth", NS)
        if birth is not None:
            b_uri = EVENT[f"birth-{pid}"]
            g.add((b_uri, RDF.type, CRM["E67_Birth"]))
            g.add((b_uri, CRM["P98_brought_into_life"], uri))
            when = birth.get("when")
            if when:
                t_uri = TIME[when]
                g.add((t_uri, RDF.type, CRM["E52_Time-Span"]))
                g.add((t_uri, CRM["P82_at_some_time_within"], date_literal(when)))
                g.add((b_uri, CRM["P4_has_time-span"], t_uri))

        reconcile(g, uri, person)

    for place in root.findall(".//t:listPlace/t:place", NS):
        pid = place.get(XMLID)
        if not pid:
            continue
        uri = PLACE[pid]
        g.add((uri, RDF.type, CRM["E53_Place"]))
        name = place.findtext("t:placeName", default="", namespaces=NS).strip()
        if name:
            g.add((uri, RDFS.label, en(name)))
        geo = place.findtext(".//t:geo", default="", namespaces=NS).strip()
        if geo:
            g.add((uri, CRM["P168_place_is_defined_by"], Literal(geo)))
        reconcile(g, uri, place)

    for org in root.findall(".//t:listOrg/t:org", NS):
        oid = org.get(XMLID)
        if not oid:
            continue
        uri = ORG[oid]
        g.add((uri, RDF.type, CRM["E74_Group"]))
        name = org.findtext("t:orgName", default="", namespaces=NS).strip()
        if name:
            g.add((uri, RDFS.label, en(name)))
        reconcile(g, uri, org)

    for event in root.findall(".//t:listEvent/t:event", NS):
        eid = event.get(XMLID)
        if not eid:
            continue
        uri = EVENT[eid]
        g.add((uri, RDF.type, CRM["E5_Event"]))
        label = event.findtext("t:label", default="", namespaces=NS).strip()
        if label:
            g.add((uri, RDFS.label, en(label)))
        date = event.find("t:date", NS)
        if date is not None:
            when = date.get("when")
            span = when or "-".join(p for p in (date.get("from"), date.get("to")) if p)
            if span:
                t_uri = TIME[span]
                g.add((t_uri, RDF.type, CRM["E52_Time-Span"]))
                g.add((t_uri, RDFS.label, Literal(span)))
                g.add((uri, CRM["P4_has_time-span"], t_uri))
        reconcile(g, uri, event)

    for clist in root.findall(".//t:div[@type='listConcept']/t:list", NS):
        last_label = ""
        for child in clist:
            tag = child.tag.split("}")[-1]
            if tag == "label":
                last_label = (child.text or "").strip()
            elif tag == "item":
                cid = child.get(XMLID)
                if not cid:
                    continue
                uri = CONCEPT[cid]
                g.add((uri, RDF.type, CRM["E28_Conceptual_Object"]))
                if last_label:
                    g.add((uri, RDFS.label, en(last_label)))
                reconcile(g, uri, child)

    for bibl in root.findall(".//t:listBibl/t:bibl", NS):
        bid = bibl.get(XMLID)
        if not bid:
            continue
        uri = BIBL[bid]
        g.add((uri, RDF.type, FRBROO["F2_Expression"]))
        title = bibl.findtext("t:title", default="", namespaces=NS).strip()
        if title:
            g.add((uri, RDFS.label, en(title)))
        reconcile(g, uri, bibl)

    negritude = CONCEPT["negritude"]
    critique = EVENT["fanon-critique-negritude"]
    g.add((critique, RDF.type, CRM["E7_Activity"]))
    g.add((critique, CRM["P14_carried_out_by"], PERSON["fanon"]))
    g.add((critique, CRM["P129_is_about"], negritude))

    founding = EVENT["cesaire-founding-negritude"]
    g.add((founding, RDF.type, CRM["E7_Activity"]))
    g.add((founding, CRM["P14_carried_out_by"], PERSON["cesaire"]))
    g.add((founding, CRM["P94_has_created"], negritude))

    return g

def main():
    root = ET.parse("tei.xml").getroot()
    g = build_graph(root)
    g.serialize("output.ttl", format="turtle")
    print(f"Done! Graph saved to output.ttl with {len(g)} triples.")

if __name__ == "__main__":
    main()
