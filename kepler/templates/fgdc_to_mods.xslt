<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:mods="http://www.loc.gov/mods/v3">
  <xsl:output omit-xml-declaration="yes" />

  <xsl:template match="/">
    <mods:mods>
      <xsl:apply-templates select="metadata" />
    </mods:mods>
  </xsl:template>

  <xsl:template match="idinfo">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="citation">
    <xsl:apply-templates select="citeinfo" />
  </xsl:template>

  <xsl:template match="title">
    <mods:titleInfo>
      <mods:title><xsl:value-of select="." /></mods:title>
    </mods:titleInfo>
  </xsl:template>

  <xsl:template match="origin">
    <mods:name>
      <mods:namePart><xsl:value-of select="." /></mods:namePart>
    </mods:name>
  </xsl:template>

  <xsl:template match="text()"></xsl:template>

</xsl:stylesheet>
