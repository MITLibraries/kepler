<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:mods="http://www.loc.gov/mods/v3">
  <xsl:output omit-xml-declaration="yes" />

  <xsl:variable name="lowercase" select="'abcdefghijklmnopqrstuvwxyz'" />
  <xsl:variable name="uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'" />

  <xsl:template match="/">
    <mods:mods>
      <xsl:apply-templates select="metadata" />
    </mods:mods>
  </xsl:template>

  <xsl:template match="title">
    <mods:titleInfo>
      <mods:title><xsl:value-of select="." /></mods:title>
    </mods:titleInfo>
  </xsl:template>

  <xsl:template match="origin">
    <mods:name>
      <mods:role>
        <mods:roleTerm type="text">creator</mods:roleTerm>
      </mods:role>
      <mods:displayForm>
        <xsl:value-of select="." />
      </mods:displayForm>
    </mods:name>
  </xsl:template>

  <xsl:template match="citeinfo[pubdate or pubinfo/publish]">
    <mods:originInfo>
      <xsl:if test="pubdate">
        <mods:dateCreated point="start">
          <xsl:value-of select="pubdate" />
        </mods:dateCreated>
      </xsl:if>
      <xsl:if test="pubinfo/publish">
        <mods:publisher>
          <xsl:value-of select="pubinfo/publish" />
        </mods:publisher>
      </xsl:if>
    </mods:originInfo>
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="abstract">
    <mods:abstract><xsl:value-of select="." /></mods:abstract>
  </xsl:template>

  <xsl:template match="accconst">
      <mods:accessCondition type="use and reproduction">
      <xsl:value-of
        select="concat(
          translate(normalize-space(.), '.', ''), '. ',
          normalize-space(//distinfo/distliab))" />
    </mods:accessCondition>
  </xsl:template>

  <xsl:template match="themekey">
    <mods:subject>
      <mods:topic><xsl:value-of select="." /></mods:topic>
    </mods:subject>
  </xsl:template>

  <xsl:template match="placekey">
    <mods:subject>
      <mods:geographic><xsl:value-of select="." /></mods:geographic>
    </mods:subject>
  </xsl:template>

  <xsl:template match="bounding">
    <mods:subject>
      <mods:cartographics>
        <mods:coordinates>
          <xsl:value-of select="concat(
              'POLYGON ((',
                westbc, ' ', southbc, ', ',
                eastbc, ' ', southbc, ', ',
                eastbc, ' ', northbc, ', ',
                westbc, ' ', northbc, ', ',
                westbc, ' ', southbc,
              '))'
              )" />
        </mods:coordinates>
      </mods:cartographics>
    </mods:subject>
  </xsl:template>

  <xsl:template match="direct">
    <xsl:if test="translate(., $uppercase, $lowercase) = 'raster'">
      <mods:typeOfResource>Image</mods:typeOfResource>
    </xsl:if>
  </xsl:template>

  <xsl:template match="text()"></xsl:template>

</xsl:stylesheet>
