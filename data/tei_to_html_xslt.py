from lxml import etree


def transform_tei_to_html(xml_path="tei.xml",
                          xsl_path="tei_to_html.xsl",
                          output_path="tei_xslt_output.html"):
    # Load XML
    xml_doc = etree.parse(xml_path)
    # Load XSLT
    xsl_doc = etree.parse(xsl_path)
    transform = etree.XSLT(xsl_doc)
    # Transform
    result = transform(xml_doc)
    # Write output
    with open(output_path, "wb") as f:
        f.write(etree.tostring(result, pretty_print=True,
                               method="html", encoding="UTF-8"))
    print(f"HTML output written to {output_path}")


if __name__ == "__main__":
    transform_tei_to_html()
