<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html"/>

    <xsl:template match="/">

        <html>
            <title><xsl:value-of select="idm/specId/@fullTitle"/></title>

            <style> 
                caption {
                font-family: sans-serif;
                font-size: 18pt;
                text-align: left;
                }

                #captionFigure {
                font-family: sans-serif;
                font-size: 12pt;
                text-align: left;
                }

                .cover {
                width: 794px;
                height: auto;
                margin-left: auto;
                margin-right: auto;
                background-color: white;
                }

                .page {
                width: 794px;
                height: auto;
                margin-top: 50px;
                margin-left: auto;
                margin-right: auto;
                background-color: white;
                }

                #sameAs {
                text-align: left;
                }

                .con_table {
                width: 750;
                border-collapse: collapse;
                margin-top: 5px;
                }

                .con_table th{
                font-family: sans-serif;
                font-size: 10pt;
                text-align: left;
                border: 0.5px solid lightgray;
                }

                .con_table td{
                
                font-family: sans-serif;
                font-size: 10pt;
                text-align: left;
                border: 0.5px solid lightgray;
                }

                .info_unit_table {
                width: 750px;
                border-collapse: collapse;
                margin-top: 20px;
                }
                
                .info_unit_table th{
                font-family: sans-serif;
                text-align: left;
                font-weight: border;
                font-size: 12pt;
                color: #002266;
                }
                
                .info_unit_table td{
                padding-upper:5px;
                padding-bottom:5px;
                padding-left:5px;
                padding-right:5px;
                font-family: sans-serif;
                font-size: 10pt;
                text-align: left;
                border: 0.5px solid lightgray;
                }

                .changeLog_table {
                border-collapse: collapse;
                border : 1px solid lightgray;
                width : 794px;
                }

                .changeLog_table th{
                padding-top: 2px;
                padding-bottom : 2px;
                padding-left : 5px;
                padding-right: 5px;
                text-align:left;
                border-collapse: collapse;
                border : 1px solid lightgray;
                background-color:#E0E0E0;
                width : 100%;
                }

                .changeLog_table td{
                padding-top: 2px;
                padding-bottom : 2px;
                padding-left : 5px;
                padding-right: 5px;
                border-collapse: collapse;
                border : 1px solid lightgray;
                width : auto;
                }


                .page #idmCode {
                font-family: sans-serif;
                margin-left: 28pt;
                font-size: 12pt
                }


                #idmFullTitle {
                margin-top: 60px;
                font-family: sans-serif;
                text-align: left;
                font-size: 20pt;
                }

                #idmSubTitle {
                font-family: sans-serif;
                text-align: left;
                font-size: 14pt;
                }

                #idmShortTitle {
                    font-family: sans-serif;
                    font-size: 10pt;
                }

                #idmCode {
                font-family: sans-serif;
                text-align: left;
                font-size: 14pt;
                }

                h1 {
                font-family: sans-serif;
                text-align: left;
                font-size: 20pt;
                font-weight: border;
                color: #002266;
                }

                h2 {
                font-family: sans-serif;
                text-align: left;
                font-weight: border;
                font-size: 12pt;
                color: #002266;
                }

                h3 {
                font-family: sans-serif;
                font-weight: bold;
                text-align: left;
                font-size: 12pt;
                display: inline;
                }

                contents {
                font-family: sans-serif;
                text-align: ;
                font-size: 10pt;
                display: block;
                }
            </style>

            <xsl:call-template name="cover"/>
            <!-- <xsl:call-template name="processMap"/> -->
            <xsl:call-template name="exchangeRequirement"/>
            <xsl:for-each select="idm/er/informationUnit">
                <xsl:call-template name="informationUnit"/>
            </xsl:for-each>
        </html>
    </xsl:template>

    <xsl:template name="cover">
        <div class="cover">
            <p id="idmShortTitle" style=""><xsl:value-of select="idm/specId/@shortTitle"/></p>
            <hr style="text-align:left;margin-left:0"/>

            <img src="image/cover.png" style="width:200px;"/>

            <h2 style="text-transform:capitalize;" id="idmFullTitle"><xsl:value-of select="idm/specId/@fullTitle"/> (IDM)</h2>
            <p id="idmSubTitle"><xsl:value-of select="idm/specId/@subTitle"/></p>
            <p id="idmCode"><xsl:value-of select="idm/specId/@idmCode"/></p>
        </div>
    </xsl:template>

    <xsl:template name="processMap">
        <div class="page">
            <h1><xsl:value-of select="idm/pm/specId/@fullTitle"/> (PM)</h1>
            <hr style="height:2px;border-width:0;color:gray;background-color:#002266;"/>
            <contents>Edited by <xsl:value-of select="idm/pm/authoring/author/@firstName"/>, on <xsl:value-of select="idm/pm/authoring/changeLog/@changeDate"/></contents>

            <br/>
            <br/>
            
            <h2>Summary</h2>
            <contents><xsl:value-of select="idm/uc/@summary"/></contents>

            <h2><xsl:value-of select="idm/pm/associatedPmDiagram/@pmDiagramName"/></h2>
            <img src="https://blog.kakaocdn.net/dn/bbbMcA/btqKWWFWnnk/FrKexUUxJsuehqcfZLadb1/img.png" style="style=vertical-align:middle; width:750px"/>

            <table class="con_table">
                <xsl:for-each select="idm/pm">    
                <tr>
                    <td rowspan="4"><xsl:value-of select="associatedPmDiagram/@pmDiagramId"/></td>
                    <td>author</td>
                    <td><xsl:value-of select="authoring/author/@firstName"/></td>
                    <td>created</td>
                    <td><xsl:value-of select="authoring/changeLog/@changeDate"/><xsl:value-of select="authoring/changeLog/@changeTime"/></td>
                    <td rowspan="4"><img src="https://blog.kakaocdn.net/dn/blm7VV/btqKSWzUsoo/cW7XyvFD0qoXmwvqHwF4Kk/img.png" width="200px"/></td>
                </tr>
                <tr>
                    <td>version</td>
                    <td><xsl:value-of select="specId/@version"/></td>
                    <td>modified</td>
                    <td><xsl:value-of select="authoring/changeLog/@changeDate"/><xsl:value-of select="authoring/changeLog/@changeTime"/></td>
                </tr>
                <tr>
                    <td>status</td>
                    <td><xsl:value-of select="specId/@isoStatus"/></td>
                    <td colspan="2"></td>
                </tr>
                <tr>
                    <td colspan="4"><xsl:value-of select="associatedPmDiagram/@pmDiagramFileName"/></td>
                </tr>
                </xsl:for-each>
            </table>

            <br/>

            <table class="con_table">
                <tr>
                    <th>Id</th>
                    <th>Type</th>
                    <th>Name</th>
                    <th>Description</th>
                </tr>
                <xsl:for-each select="idm/pm/associatedPmDiagram/pmElement">
                <tr>
                    <td><xsl:number value="position()" format="1"/></td>
                    <td><xsl:value-of select="@pmElementType"/></td>
                    <td><xsl:value-of select="@pmElementName"/></td>
                    <td><xsl:value-of select="@pmElementDescription"/></td>
                </tr>
                </xsl:for-each>
            </table>

            <br/>

            <h2>Role Overview</h2>
            <contents>The primary roles shown in the process model diagram (as "swimlanes") are defined as: </contents>

            <br/>
            <br/>

            <table>
                <xsl:for-each select="idm/uc/actorClassification/actor">
                <tr>
                    <td style="font-family: sans-serif; font-size: 10pt;"><xsl:value-of select="@actorRole"/></td>
                </tr>
                </xsl:for-each>
            </table>
        </div>
    </xsl:template>

    <xsl:key name="changedByKey" match="idm/er/authoring/author" use="@id"/>
    
    <xsl:template name="exchangeRequirement">
        <div class="page">
            <h1 style="text-transform:capitalize;"><xsl:value-of select="idm/er/specId/@fullTitle"/> (ER)</h1>
            <hr style="height:2px;border-width:0;color:gray;background-color:#002266;"/>
            <table class="changeLog_table">
                <tr>
                    <th colspan="3">Change Log</th>
                </tr>
                <tr>
                    <td style="font-weight: bold; text-transform:capitalize;">date</td>
                    <td style="font-weight: bold; text-transform:capitalize;">description</td>
                    <td style="font-weight: bold; text-transform:capitalize;">eddited by</td>
                </tr>
                
                <xsl:for-each select="idm/er/authoring/changeLog">
                    <tr>
                        <td><xsl:value-of select="@changeDate"/></td>
                        <td><xsl:value-of select ="@changeSummary"/></td>
                        <td><xsl:value-of select ="key('changedByKey', @changedBy)/@firstName"/>&#160;<xsl:value-of select ="key('changedByKey', @changedBy)/@lastName"/></td>
                    </tr>
                </xsl:for-each>


            </table>
            <!-- <contents>Edited by <xsl:value-of select="idm/er/authoring/author/@firstName"/>, on <xsl:value-of select="idm/er/authoring/changeLog/@changeDate"/></contents> -->
            <br/>
            <br/>
            <h2>Aim and Scope</h2>
            <p><xsl:value-of select="idm/uc/@aimAndScope"/></p>
            <img style="width:350px" src="Image/AS1.PNG"/>
            <img style="width:350px" src="Image/AS2.PNG"/>
            <br/>
            <br/>
            <h2>Summary</h2>
            <p><xsl:value-of select="idm/uc/@summary"/></p>
            <img style="width: 200px" src="Image/S1.PNG"/>
            <img style="width: 200px" src="Image/S2.PNG"/>
            <img style="width: 100px" src="Image/S3.PNG"/>
        </div>
    </xsl:template>

    <xsl:template name="informationUnit">
        <div class="page">
               
            <h2 style="text-transform : capitalize;"><xsl:value-of select="@name"/></h2>
            <contents><xsl:value-of select="@definition"/></contents>
            <table class="info_unit_table">
            <xsl:for-each select="graphicalExample">
                <img width="200px">
                    <xsl:attribute name="src">
                        <xsl:value-of select="@fullFilePath"/>
                    </xsl:attribute>
                </img>
            </xsl:for-each>
                    <tr>
                        <td>Information Needed</td>
                        <td>Data Type</td>
                        <td>Mandatory</td>
                        <td>Definition</td>
                        <td>Example</td>
                    </tr>
                <xsl:for-each select="subInformationUnit/informationUnit">
                    <tr>
                        <td style="text-transform: capitalize;"><xsl:value-of select="@name"/></td>
                        <td><xsl:value-of select="@dataType"/></td>
                        <td>
                            <xsl:choose>
                                <xsl:when test="@isMandatory='true'"><img style=" align = center; width:50%" src="image/check.png"/></xsl:when>
                                
                            </xsl:choose>
                        </td>
                        <td><xsl:value-of select="@definition"/></td>
                        <td>
                            <xsl:for-each select="graphicalExample">
                                <img style="width:200px">
                                                <xsl:attribute name="src">
                                                    <xsl:value-of select="@fullFilePath"/>
                                                </xsl:attribute>
                                            </img>
                            </xsl:for-each>
                            <xsl:for-each select="textualExample">
                                    <p style="font-size:8px;">example:<xsl:value-of select="@description"/>
                                    </p>
                            </xsl:for-each>
                        </td>
                    </tr>
                </xsl:for-each>
            </table>
        </div>
    </xsl:template>
</xsl:stylesheet>