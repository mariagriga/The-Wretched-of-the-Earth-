<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:t="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="t">

  <xsl:output method="html" encoding="UTF-8" indent="yes"
              doctype-system="about:legacy-compat"/>

  <xsl:template match="/">
    <html lang="en">
      <head>
        <meta charset="UTF-8"/>
        <title>TEI Output (XSLT) — The Wretched of the Earth</title>
        <style>
          body { background:#0c0b10; color:#e8e4dc; font-family:Georgia,serif;
                 line-height:1.8; padding:3rem clamp(1.5rem,8vw,8rem); }
          h1 { font-weight:normal; color:#f0ece4; }
          .tei-head { text-transform:uppercase; letter-spacing:.06em;
                      color:rgba(232,228,220,.4); margin:2rem 0 .5rem; }
          .entity { border-bottom:1px solid rgba(255,255,255,.35); }
          .person { color:#e0b3b3; } .place { color:#b3d1e0; }
          .org { color:#c9b3e0; } .work { color:#e0d6b3; }
          .concept { color:#b3e0c2; } .event { color:#e0c4a0; }
          .quote { font-style:italic; color:#e0c4a0; }
          .entity a { color:inherit; font-size:.7rem; }
          table { width:100%; border-collapse:collapse; margin:1rem 0 2rem; }
          th,td { border:1px solid #333; padding:8px; text-align:left; font-size:.8rem; }
        </style>
      </head>
      <body>
        <header>
          <h1><xsl:value-of select="//t:titleStmt/t:title"/></h1>
        </header>


        <xsl:apply-templates select="//t:body//t:div"/>


        <xsl:apply-templates select="//t:back/t:div"/>
      </body>
    </html>
  </xsl:template>


  <xsl:template match="t:div">
    <xsl:if test="t:head">
      <h3 class="tei-head"><xsl:value-of select="t:head"/></h3>
    </xsl:if>
    <xsl:apply-templates select="t:div"/>
    <xsl:apply-templates select="t:p"/>
  </xsl:template>

  <xsl:template match="t:p">
    <p class="tei-p"><xsl:apply-templates/></p>
  </xsl:template>


  <xsl:template match="t:persName">
    <xsl:call-template name="entity"><xsl:with-param name="css" select="'person'"/></xsl:call-template>
  </xsl:template>
  <xsl:template match="t:placeName">
    <xsl:call-template name="entity"><xsl:with-param name="css" select="'place'"/></xsl:call-template>
  </xsl:template>
  <xsl:template match="t:orgName">
    <xsl:call-template name="entity"><xsl:with-param name="css" select="'org'"/></xsl:call-template>
  </xsl:template>
  <xsl:template match="t:title">
    <xsl:call-template name="entity"><xsl:with-param name="css" select="'work'"/></xsl:call-template>
  </xsl:template>
  <xsl:template match="t:rs[@type='concept']">
    <xsl:call-template name="entity"><xsl:with-param name="css" select="'concept'"/></xsl:call-template>
  </xsl:template>
  <xsl:template match="t:rs[@type='event']">
    <xsl:call-template name="entity"><xsl:with-param name="css" select="'event'"/></xsl:call-template>
  </xsl:template>
  <xsl:template match="t:quote">
    <xsl:call-template name="entity"><xsl:with-param name="css" select="'quote'"/></xsl:call-template>
  </xsl:template>

  <xsl:template name="entity">
    <xsl:param name="css"/>
    <span class="entity {$css}">
      <xsl:value-of select="."/>
      <xsl:if test="@ref">
        <xsl:text> </xsl:text>
        <a href="{@ref}" target="_blank">↗</a>
      </xsl:if>
    </span>
  </xsl:template>


  <xsl:template match="t:div[@type='listPerson']">
    <h3 class="tei-head">Persons</h3>
    <table><tr><th>Name</th><th>Born</th><th>Occupation</th><th>Authority</th></tr>
      <xsl:for-each select="t:listPerson/t:person">
        <tr>
          <td><xsl:value-of select="t:persName[1]"/></td>
          <td><xsl:value-of select="t:birth/@when"/></td>
          <td><xsl:value-of select="t:occupation"/></td>
          <td><xsl:apply-templates select="t:idno" mode="link"/></td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>

  <xsl:template match="t:div[@type='listPlace']">
    <h3 class="tei-head">Places</h3>
    <table><tr><th>Name</th><th>Coordinates</th><th>Authority</th></tr>
      <xsl:for-each select="t:listPlace/t:place">
        <tr>
          <td><xsl:value-of select="t:placeName"/></td>
          <td><xsl:value-of select="t:location/t:geo"/></td>
          <td><xsl:apply-templates select="t:idno" mode="link"/></td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>

  <xsl:template match="t:div[@type='listOrg']">
    <h3 class="tei-head">Organisations</h3>
    <table><tr><th>Name</th><th>Authority</th></tr>
      <xsl:for-each select="t:listOrg/t:org">
        <tr>
          <td><xsl:value-of select="t:orgName"/></td>
          <td><xsl:apply-templates select="t:idno" mode="link"/></td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>

  <xsl:template match="t:div[@type='listEvent']">
    <h3 class="tei-head">Events</h3>
    <table><tr><th>Label</th><th>Date</th><th>Authority</th></tr>
      <xsl:for-each select="t:listEvent/t:event">
        <tr>
          <td><xsl:value-of select="t:label"/></td>
          <td>
            <xsl:choose>
              <xsl:when test="t:date/@from"><xsl:value-of select="concat(t:date/@from,'–',t:date/@to)"/></xsl:when>
              <xsl:otherwise><xsl:value-of select="t:date/@when"/></xsl:otherwise>
            </xsl:choose>
          </td>
          <td><xsl:apply-templates select="t:idno" mode="link"/></td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>

  <xsl:template match="t:div[@type='listConcept']">
    <h3 class="tei-head">Concepts</h3>
    <table><tr><th>Term</th><th>Gloss</th><th>Authority</th></tr>
      <xsl:for-each select="t:list/t:item">
        <tr>
          <td><xsl:value-of select="preceding-sibling::t:label[1]"/></td>
          <td><xsl:value-of select="t:gloss"/></td>
          <td><xsl:apply-templates select="t:idno" mode="link"/></td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>

  <xsl:template match="t:div[@type='listBibl']">
    <h3 class="tei-head">Bibliography</h3>
    <table><tr><th>Title</th><th>Author</th><th>Date</th><th>Authority</th></tr>
      <xsl:for-each select="t:listBibl/t:bibl[t:title]">
        <tr>
          <td><xsl:value-of select="t:title[1]"/></td>
          <td><xsl:value-of select="t:author"/></td>
          <td><xsl:value-of select="t:date"/></td>
          <td><xsl:apply-templates select="t:idno" mode="link"/></td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>


  <xsl:template match="t:idno" mode="link">
    <a href="{.}" target="_blank"><xsl:value-of select="@type"/></a>
    <xsl:text> </xsl:text>
  </xsl:template>

</xsl:stylesheet>
