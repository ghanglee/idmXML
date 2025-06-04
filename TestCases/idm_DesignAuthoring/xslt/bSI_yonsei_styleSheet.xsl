<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
exclude-result-prefixes="bpmn">

    <xsl:output method="html"/> 

    <xsl:key name="findBPMN" match="document('Diagram\Diagram(1).bpmn')/bpmn:definitions/bpmn:process/bpmn:dataObjectReference" use="@id"/>
    <xsl:key name="findErByGuid" match="idm/er/subEr/er/specId" use="@guid"/>
    <xsl:key name="findErByGuid2" match="idm/er/subEr/er" use="specId/@guid"/>
    <xsl:key name="dup" match="idm/authoring/changeLog/change/@changedFrom" use="." />
    <xsl:key name="dup_uc" match="idm/uc/authoring/changeLog/change/@changedFrom" use="." />
    <xsl:key name="dup_bcm" match="idm/businessContextMap/authoring/changeLog/change/@changedFrom" use="." />
    <xsl:key name="dup_er" match="idm/er/authoring/changeLog/change/@changedFrom" use="." />
     
    <xsl:template match="/">

        <link rel="stylesheet" type="text/css" href="xml_styleSheet2.css"/>
       
        <html>
            <style>    
                
                @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300&amp;display=swap');
                
                .cover {
                    width: 794px;
                    height: auto;
                    padding-top: 96px;
                    margin-left: auto;
                    margin-right: auto;
                    background-color: white;
                }

                .page {
                    width: 794px;
                    height: auto;             
                    margin-left: auto;
                    margin-right: auto;
                    background-color: white;
                }
                

                <!--Full Title-->
                h1 {                
                    margin-top: 192px;
                    font-family:Tahoma;
                    text-align: left;
                    font-size: 25.5pt;   
                    font-weight: normal;        
                    }
                
                <!--IDM code-->   

                h2 {          
                    font-family:Tahoma;  
                    text-align: left;
                    font-size: 12.5pt;     
                    font-weight: normal;         
                    }

                <!--Component Title-->   

                h3 {          
                    font-family: Arial;     
                    text-align: left;
                    font-size: 14pt;   
                    }

                <!--ER_IU Title-->   

                h4 {          
                   
                    font-weight: normal;
                    font-style: italic; bold;
                    text-align: left;
                    font-size: 12pt;                 
                    }

                <!--Sub_Component Title-->   

                h5 {          
                    font-family: Arial;    
                    text-align: left;
                    font-size: 12pt;   
                }

                <!--Sub_Component Title-->   

                h6 {          
                    font-family: "Times New Roman";    
                    text-align: left;
                    font-size: 10pt;                   
                }

                <!--Sub_Component Title-->   

                h7 {          
                    font-family: "Times New Roman";    
                    text-align: left;
                    font-style:italic;
                    font-size: 10pt;                   
                }
    
                <!--Table-->
                 
                .basicInfo .additionalInfo 
                    {
                        width: 100%;                    
                        text-align: left;                      
                        border:1px solid;
                        border-color:black;    
                        border-collapse: collapse;   
                        background-color: #ECECEC;              
                    }

                .basicInfo th {
                    font-family:Arial;  
                    text-align: left;
                    font-size: 10pt;
                    width: 110px;
                    padding: 5px;
                    font-weight: normal;  
                    border:1px solid;
                    border-color:black; 
                    border-collapse: collapse;  
                    background-color: #f3f3f3;    
                }

                .additionalInfo th {
                    font-family:"Times New Roman";  
                    text-align: left;
                    font-size: 10pt;
                    width: 110px;
                    padding: 5px;
                    font-weight: normal;  
                    border:1px solid;
                    border-color:black; 
                    border-collapse: collapse;  
                    background-color: #f3f3f3;   
                }

                .basicInfo td {
                    font-family:"Times New Roman";
                    text-align: left;
                    font-size: 10pt;
                    padding-left: 10px;
                    border:1px solid;
                    border-color:black; 
                    border-collapse: collapse;   
                    background-color: #ECECEC;      
                }

                .additionalInfo td {
                    font-family:"Times New Roman";
                    text-align: left;
                    font-size: 10pt;
                    padding-left: 10px;
                    border:1px solid;
                    border-color:black; 
                    border-collapse: collapse;   
                    background-color: #eeece1;     
                }   
                
                <!--Table 4 Name-->
                
                .name
                    {
                        width: 100%;                    
                        text-align: left;                      
                        border:1px solid;
                        border-color:black;    
                        border-collapse: collapse;   
                        background-color: #FFFFFF;              
                    }

                .name th {
                    font-family:Arial; 
                    text-align: left;
                    font-size: 12pt;
                    width: 110px;
                    padding: 5px;
                    font-weight: normal;  
                    border:1px solid;
                    border-color:black; 
                    border-collapse: collapse;  
                    background-color: #FFFFFF;
                    font-weight:bold;   
                    padding-right: 50px;
                }

                .name td {
                    font-family:Tahoma;
                    text-align: left;
                    font-size: 12pt;                    
                    border:1px solid;
                    border-color:black; 
                    border-collapse: collapse;   
                    background-color: #FFFFFF; 
                    font-weight:bold;        
                }

                 <!--Table 4 Name-->
                
                 .id
                 {
                     width: 100%;                    
                     text-align: left;                      
                     border:1px solid;
                     border-color:black;    
                     border-collapse: collapse;   
                     background-color: #FFFFFF;              
                 }

                 .id th {
                    font-family: Arial; 
                    text-align: left;
                    font-size: 10pt;
                    width: 110px;
                    padding: 5px;
                    font-weight: normal;  
                    border:1px solid;
                    border-color:black; 
                    border-collapse: collapse;  
                    background-color: #FFFFFF
                    font-weight:bold;   
           
                }

                .id td {
                    font-family:Tahoma;
                    text-align: left;
                    font-size: 10pt;                    
                    border:1px solid;
                    border-color:black; 
                    border-collapse: collapse;   
                    background-color: #FFFFFF; 
                    font-weight:normal;        
                }
                             
                <!--Table 4 C.log-->
                
                .c_table {
                    text-align: left;
                    border: 2px solid #444444;
                    border-collapse: collapse;  
                    margin-top: 20px;          
                }

                .c_table td{                    
                    text-align: left;
                    border: 1px solid #444444;
                    border-collapse: collapse;                 
                }

                .c_table th{
                    text-align: left;
                    border: 1px solid #444444;
                    border-collapse: collapse;
                    background-color: #ECECEC;                    
                }          
                
                hr {
                    margin-top: 96px;
                    margin-bottom: 96px;
                }
                
            </style>       

            <body>
                <div class="cover">

                    <!--IDM Metadata-->

                    <h1 id="idmFullTitle"><xsl:value-of select="idm/specId/@fullTitle"/></h1>
                   
                    <h2 id="idmCode"><xsl:value-of select="idm/specId/@idmCode"/></h2>          
                   
                    <table  class="basicInfo" style="margin-top: 75px;">                        
                        <xsl:for-each select="idm">     
                        
                            <tr>
                                <xsl:if test="specId/@shortTitle != ''">
                                    <th>shortTitle</th>
                                    <td><xsl:value-of select="specId/@shortTitle"/></td>
                                </xsl:if>
                            </tr>  

                            <tr>       
                                <th>Status</th>
                                <td>
                                    <xsl:if test="specId/@documentStatus='NP'">
                                            <bool>New Proposal</bool> 
                                    </xsl:if>
                                    <xsl:if test="specId/@documentStatus='WD'">
                                            <bool>Working Draft</bool> 
                                    </xsl:if>
                                    <xsl:if test="specId/@documentStatus='PUB'">
                                            <bool>Publication</bool> 
                                    </xsl:if>
                                    <xsl:if test="specId/@documentStatus='WDRL'">
                                            <bool>Withdrawal</bool> 
                                    </xsl:if>                                  
                                </td>                                                                                         
                            </tr>      
                                                                       
                            <tr>                                
                                <th>Authors</th>                            
                                <td style="text-align:left; margin-left:0px;">
                                    <xsl:for-each select="authoring/author">  
                                    <xsl:value-of select= "@firstName"/>&#160;<xsl:value-of select="@lastName"/>
                                    <xsl:choose style="text-align:left; margin-left:0px;">
                                        <xsl:when test="position() != last()">,&#160;</xsl:when>
                                    </xsl:choose>
                                </xsl:for-each>
                                </td>                                
                            </tr>

                            <tr>
                                <xsl:if test="authoring/committee/@name != ''">
                                    <th>Committee</th>
                                    <td><xsl:value-of select="authoring/committee/@name"/></td>
                                </xsl:if>
                            </tr>
                            
                        </xsl:for-each>                      
                    </table>                

                    <!--Table for Changelog-->                 
                                    
                    <table class="c_table" style="margin-top: 20px;">

                        <tr>
                            <th colspan ="4" style="font-weight: bold; background-color:#c0fec8;">Change log</th>                           
                        </tr>

                        <tr>                            
                            <th>Changed Date</th>    
                            <th>Changed Element</th> 
                            <th>Changed From</th> 
                            <th>Changed by</th>                       
                        </tr>

                    
                        <xsl:for-each select="(idm/authoring/changeLog/change/@changedFrom)[generate-id(.) = generate-id(key('dup', .))]">
                            <xsl:sort select="."/>

                                <tr>
                                    <td><xsl:value-of select="../../@changeDateTime"/></td>
                                    <td><xsl:value-of select="../@changedElement"/></td>                                  
                                    <td>                                                       
                                        <xsl:value-of select="." />                                   
                                    </td>
                                    <xsl:if test="../../@changedBy =../../../author/@id">
                                        <td>
                                            <xsl:value-of select="../../../author/@firstName"/>&#160;<xsl:value-of select="../../../author/@lastName"/>
                                        </td>                                                     
                                    </xsl:if>                    
                                </tr>       

                        </xsl:for-each>                                                  
            
                    </table>  

                </div>             
                                          
                <!--UC-->

                <div class="page" style="page-break-before: always;">
                    
                    <h3>Use Case</h3>                   
                                       
                    <xsl:if test="idm/uc/specId/@shortTitle != ''">

                        <table  class="name">                       
                            
                            <tr>
                                
                                    <th>Name</th>
                                    <td>&#160;<xsl:value-of select="idm/uc/specId/@shortTitle"/></td>
                                
                            </tr>
                    
                        </table>

                    </xsl:if>

                    <xsl:if test="idm/uc/specId/@idmCode != ''">
                    
                        <table class="id" style="margin-top:10px;">                      
                            <tr>
                                
                                    <th>Identifier</th>
                                    <td>&#160;<xsl:value-of select="idm/uc/specId/@idmCode"/></td>

                            </tr>
                        </table>

                    </xsl:if>

                    <xsl:if test="idm/uc/specId/@documentStatus != ''">

                        <table class="id"> 
                            <xsl:for-each select="idm/uc">
                                <tr>       
                                    <th>Status</th>
                                    <td>
                                        <xsl:if test="specId/@documentStatus='NP'">
                                                <bool>&#160;New Proposal</bool> 
                                        </xsl:if>
                                        <xsl:if test="specId/@documentStatus='WD'">
                                                <bool>&#160;Working Draft</bool> 
                                        </xsl:if>
                                        <xsl:if test="specId/@documentStatus='PUB'">
                                                <bool>&#160;Publication</bool> 
                                        </xsl:if>
                                        <xsl:if test="specId/@documentStatus='WDRL'">
                                                <bool>&#160;Withdrawal</bool> 
                                        </xsl:if>                                  
                                    </td>                                                                                         
                                </tr>   
                            </xsl:for-each>                    
                        </table>

                    </xsl:if>

                    <!--Table for Changelog-->                 
                                    
                    <table class="c_table" style="margin-top: 20px;">

                        <tr>
                            <th colspan ="4" style="font-weight: bold; background-color:#c0fec8;">Change log</th>                           
                        </tr>

                        <tr>                            
                            <th>Changed Date</th>    
                            <th>Changed Element</th> 
                            <th>Changed From</th> 
                            <th>Changed by</th>                       
                        </tr>

                    
                        <xsl:for-each select="(idm/uc/authoring/changeLog/change/@changedFrom)[generate-id(.) = generate-id(key('dup_uc', .))]">
                            <xsl:sort select="."/>

                                <tr>
                                    <td><xsl:value-of select="../../@changeDateTime"/></td>
                                    <td><xsl:value-of select="../@changedElement"/></td>                                  
                                    <td>                                                       
                                        <xsl:value-of select="." />                                   
                                    </td>
                                    <xsl:if test="../../@changedBy =../../../author/@id">
                                        <td>
                                            <xsl:value-of select="../../../author/@firstName"/>&#160;<xsl:value-of select="../../../author/@lastName"/>
                                        </td>                                                     
                                    </xsl:if>                    
                                </tr>       

                        </xsl:for-each>                                                  
            
                    </table>  
                    
                    <!--Mandatory Attributes_Paragraph-->  

                    <h5 style="margin-top: 25px; margin-bottom:10px; font-weight:bold;">Overview</h5>
                    
                    <table class="basicInfo" style="margin-top: 5px">
                        <xsl:for-each select="idm/uc">                           
                            <tr> 
                                <td>
                                    <xsl:value-of select="summary/description/content"/><br/>
                                </td>
                            </tr> 
                        </xsl:for-each>    
                    </table>

                    <h6 style="margin-top: 15px; margin-bottom:10px; font-weight:bold;">Scope</h6>

                    <table class="basicInfo" style="margin-top: 5px;">
                        <xsl:for-each select="idm/uc"> 
                            <tr>                              
                                <td>
                                    <xsl:value-of select="aimAndScope/description/content"/><br/>
                                </td>
                            </tr> 
                        </xsl:for-each>    
                    </table>

                     <!--Optional Attributes_Paragraph-->

                    <xsl:if test="benefits/description != ''">

                    <h5 style="margin-top: 15px; margin-bottom:10px; font-weight:bold;">Results</h5>                   
                    
                        <table class="basicInfo" style="margin-top: 15px;">
                            <xsl:for-each select="idm/uc">                                
                                    <tr>                                                            
                                        <td>
                                            <contents><xsl:value-of select="benefits/description/content"/></contents>
                                        </td>                                                                 
                                    </tr>
                                
                            </xsl:for-each>    
                        </table>  
                    </xsl:if>

                    <h6 style="margin-top: 15px;">General Description</h6>                    
                    
                    <table Class="additionalInfo" style="margin-top: 5px; margin-bottom:30px;">
                        
                        <h7>Target Project Phase</h7>
                                                        
                        <tr style="margin-top:0px; margin-bottom:0px;">                            
                            <th>Target Project Name&#160;</th>
                            <th>Outcome Description&#160;</th>   
                            <th>Information Requirement Description&#160;</th>   
                            <th>Exchange Requirement&#160;</th>                                         
                        </tr>    
                        <xsl:for-each select="idm/uc/standardProjectPhase">    

                            <tr style="background-color: #D3D3D3;"> 
                                
                                    <td ><xsl:value-of select="name"/></td>  
                                    <td><xsl:value-of select="outcomes/description/content"/></td>       
                                    <td><xsl:value-of select="informationRequirements/description/content"/></td>
                                <td>    
                                    <xsl:value-of select ="key('findErByGuid', informationRequirements/associatedEr)/@shortTitle"/> 
                                
                                </td>               
                                                                            
                            </tr>
                        </xsl:for-each>
                        
                    </table>

                    <xsl:if test="idm/uc/actor != ''">  

                        <h7>Actor</h7>
                        
                        <table Class="additionalInfo" style="margin-top: 5px; margin-bottom:30px;">

                            <tr>                                     
                                <th style="font-family:'Calibri';  font-weight:bold;">Classification&#160;</th>
                                <th style="font-family:'Calibri';  font-weight:bold;">Actor&#160;</th>                                     
                            </tr>     

                            <xsl:for-each select="idm/uc/actor">             
                                <tr>  
                                    <td><xsl:value-of select="classification/@name"/></td>  
                                    <td><xsl:value-of select="@name"/></td>                 
                                </tr>
                            </xsl:for-each>

                        </table>

                    </xsl:if>

                    <xsl:if test="idm/uc/userDefinedProperty != ''"> 

                        <h7>User Defined Property</h7>                  

                        <table Class="additionalInfo" style="margin-top: 5px; margin-bottom:30px;">
                            <tr>                                    
                                <th style="font-family:'Calibri'; font-weight:bold;">Name&#160;</th>                            
                                <th style="font-family:'Calibri'; font-weight:bold;">Description&#160;</th>                    
                            </tr>     
                            <xsl:for-each select="idm/uc/userDefinedProperty ">             
                                <tr>   
                                    <td><xsl:value-of select="@name"/></td>  
                                    <td><xsl:value-of select="description/content"/></td>                                        
                                </tr>
                            </xsl:for-each>
                        </table>    
                        
                    </xsl:if>
                   
                    <h6 style="margin-top: 15px; margin-bottom:30px;">Information Description</h6>  

                    <xsl:if test="limitations/description != ''">  
                        <table class="additionalInfo" style="margin-top: 5px;">
                            <xsl:for-each select="idm/uc">                 
                                    <tr>                                 
                                        <th>limitations</th>
                                        <td>
                                            <contents><xsl:value-of select="limitations/description/content"/></contents>
                                        </td>                                                                 
                                    </tr>                                   
                            </xsl:for-each>    
                        </table>
                    </xsl:if> 

                    <xsl:if test="requiredResources/description != ''"> 
                        <table class="additionalInfo" style="margin-top: 5px;">
                            <xsl:for-each select="idm/uc">                     
                                <tr>                                 
                                    <th>Required Resources</th>
                                    <td>
                                        <contents><xsl:value-of select="requiredResources/description/content"/></contents>
                                    </td>                
                                </tr>  
                                
                            </xsl:for-each>    
                        </table> 
                    </xsl:if>   
                    
                    <xsl:if test="requiredCompetencies/description != ''"> 
                        <table class="additionalInfo" style="margin-top: 5px;">
                            <xsl:for-each select="idm/uc"> 
                                                        
                                    <tr>                                
                                        <th>Required Competencies</th>
                                        <td>
                                            <contents><xsl:value-of select="requiredCompetencies/description/content"/></contents>
                                        </td>                                                                 
                                    </tr>  
                                    
                            </xsl:for-each>    
                        </table>    
                    </xsl:if> 

                    <!--Mandatory Attributes-->  
                    
                    <table class="additionalInfo" style="margin-top: 10px;">
                        <xsl:for-each select="idm/uc">                                                                                                
                              
                            <tr>                           
                                <th>Language</th>
                                <td>                                      
                                    <xsl:value-of select="language"/>                                                                           
                                </td>                                                         
                            </tr>  
                                    
                            <tr>           
                                <th>Use</th>
                                <td> 
                                    <xsl:value-of select="useClassification/@name"/>                                   
                                        <xsl:choose>
                                            <xsl:when test="useClassification/classification/@name != 'No classification'">
                                                <bool>&#160;(<xsl:value-of select="useClassification/classification/@name"/>)</bool>        
                                            </xsl:when>
                                        <xsl:otherwise>&#160;</xsl:otherwise>                                 
                                    </xsl:choose>                                                                          
                                </td>                                             
                            </tr>                
                            <!--Optional Attributes-->    
                            <tr>
                                <xsl:if test="region/@value != ''">                              
                                    <th>Region</th>
                                    <td> 
                                        <xsl:value-of select="region/@value"/>
                                                                            
                                            <xsl:choose>
                                            <xsl:when test="region/@type='USR'">
                                                <bool>&#160;(User-Defined)</bool> 
                                            </xsl:when>
                                            <xsl:otherwise>&#160;</xsl:otherwise>                                 
                                        </xsl:choose>                                                                          
                                    </td> 
                                </xsl:if>                                
                            </tr>

                            <tr> 
                                <xsl:if test="scopeKeyword != ''">       
                                    <th>Scope Keywords</th>
                                    <td>
                                        <xsl:for-each select="scopeKeyword">
                                            <xsl:value-of select="."/>
                                            <xsl:choose>
                                                <xsl:when test="position() != last()">,&#160;</xsl:when>
                                            </xsl:choose>
                                        </xsl:for-each>
                                    </td>
                                </xsl:if> 
                            </tr> 

                            <tr> 
                                <xsl:if test="benefitKeyword != ''">  
                                    <th>Benefit Keywords</th>
                                    <td>
                                        <xsl:for-each select="benefitKeyword">
                                            <xsl:value-of select="."/>
                                            <xsl:choose>
                                                <xsl:when test="position() != last()">,&#160;</xsl:when>
                                            </xsl:choose>
                                        </xsl:for-each>                                       
                                    </td> 
                                </xsl:if>                                
                            </tr>  

                            <tr> 
                                <xsl:if test="reference/@fullCitation != ''"> 
                                    <th>Reference</th>                          
                                    <td>
                                        <xsl:for-each select="reference">
                                            <xsl:value-of select="@fullCitation"/>                                     
                                            <xsl:choose>
                                                <xsl:when test="position() != last()">,&#160;</xsl:when>
                                            </xsl:choose>
                                        </xsl:for-each>                                       
                                    </td> 
                                </xsl:if>                                
                            </tr>  

                        </xsl:for-each> 
                    </table>                           
               </div>

               <!--Business Context Map-->

               <div class="page" style="page-break-before: always;">
                    
                    <h3>Business Context Map</h3>               
                                   
                    <xsl:if test="idm/businessContextMap/specId/@shortTitle != ''">

                        <table  class="name">                       
                            
                            <tr>
                                
                                    <th>Name</th>
                                    <td>&#160;<xsl:value-of select="idm/businessContextMap/specId/@shortTitle"/></td>
                                
                            </tr>
                    
                        </table>

                    </xsl:if>

                    <xsl:if test="idm/businessContextMap/specId/@idmCode != ''">
                    
                        <table class="id" style="margin-top:10px;">                      
                            <tr>
                                
                                    <th>Identifier</th>
                                    <td>&#160;<xsl:value-of select="idm/businessContextMap/specId/@idmCode"/></td>

                            </tr>
                        </table>

                    </xsl:if>

                    <xsl:if test="idm/businessContextMap/specId/@documentStatus != ''">

                        <table class="id"> 
                            <xsl:for-each select="idm/businessContextMap">
                                <tr>       
                                    <th>Status</th>
                                    <td>
                                        <xsl:if test="specId/@documentStatus='NP'">
                                                <bool>&#160;New Proposal</bool> 
                                        </xsl:if>
                                        <xsl:if test="specId/@documentStatus='WD'">
                                                <bool>&#160;Working Draft</bool> 
                                        </xsl:if>
                                        <xsl:if test="specId/@documentStatus='PUB'">
                                                <bool>&#160;Publication</bool> 
                                        </xsl:if>
                                        <xsl:if test="specId/@documentStatus='WDRL'">
                                                <bool>&#160;Withdrawal</bool> 
                                        </xsl:if>                                  
                                    </td>                                                                                         
                                </tr>   
                            </xsl:for-each>                    
                        </table>

                    </xsl:if>

                    <!--Table for Changelog-->                 
                                    
                    <table class="c_table" style="margin-top: 20px;">

                        <tr>
                            <th colspan ="4" style="font-weight: bold; background-color:#c0fec8;">Change log</th>                           
                        </tr>

                        <tr>                            
                            <th>Changed Date</th>    
                            <th>Changed Element</th> 
                            <th>Changed From</th> 
                            <th>Changed by</th>                       
                        </tr>

                    
                        <xsl:for-each select="(idm/businessContextMap/authoring/changeLog/change/@changedFrom)[generate-id(.) = generate-id(key('dup_bcm', .))]">
                            <xsl:sort select="."/>

                                <tr>
                                    <td><xsl:value-of select="../../@changeDateTime"/></td>
                                    <td><xsl:value-of select="../@changedElement"/></td>                                  
                                    <td>                                                       
                                        <xsl:value-of select="." />                                   
                                    </td>
                                    <xsl:if test="../../@changedBy =../../../author/@id">
                                        <td>
                                            <xsl:value-of select="../../../author/@firstName"/>&#160;<xsl:value-of select="../../../author/@lastName"/>
                                        </td>                                                     
                                    </xsl:if>                    
                                </tr>       

                        </xsl:for-each>                                                  
            
                    </table>
                    
                    <xsl:if test="idm/businessContextMap/pm/diagram/@id !=''">

                            <h5 style="margin-top: 35px;">PM Diagram</h5> 
                        
                            <img style="float: left; width: 100%; height: 250px; margin-bottom:96px"  src="Diagram\Diagram(1).png"/>
                        
                        </xsl:if>

                        <h5 style="margin-top: 0px;">Data Object</h5>                        

                        <table  class="additionalInfo" style="margin-top: 5px;"> 
                            <tr>          
                                <th>Data Object</th>                      
                                <th>Exchange Requirement</th>
                                <th>Description</th>
                            </tr>  

                            <xsl:for-each select="idm/businessContextMap/pm/dataObjectAndEr">                        
                                <xsl:variable name="a" select="associatedDataObject" />                                                        
                                    <tr>                                             
                                        <td>            
                                            <xsl:value-of select ="document('Diagram\Diagram(1).bpmn')/bpmn:definitions/bpmn:process/bpmn:dataObjectReference[@id=$a]/@name"/>                                     
                                        </td>                                 
                                        <td>
                                            <xsl:value-of select ="key('findErByGuid',associatedEr)/@shortTitle"/> 
                                        </td>
                                        <td>
                                            <xsl:value-of select ="key('findErByGuid2',associatedEr)/description/content"/> 
                                        </td>                          
                                    </tr>                                                                                  
                            </xsl:for-each>
                        </table>      
                </div>

               <!--ER-->                      

               <div class="page" style="page-break-before: always;">
                    
                <h3>Exchange Requirement</h3>               
                               
                <xsl:if test="idm/er/specId/@shortTitle != ''">

                    <table  class="name">                       
                        
                        <tr>
                            
                                <th>Name</th>
                                <td>&#160;<xsl:value-of select="idm/er/specId/@shortTitle"/></td>
                            
                        </tr>
                
                    </table>

                </xsl:if>

                <xsl:if test="idm/er/specId/@idmCode != ''">
                
                    <table class="id" style="margin-top:10px;">                      
                        <tr>
                            
                                <th>Identifier</th>
                                <td>&#160;<xsl:value-of select="idm/er/specId/@idmCode"/></td>

                        </tr>
                    </table>

                </xsl:if>

                <xsl:if test="idm/er/specId/@documentStatus != ''">

                    <table class="id"> 
                        <xsl:for-each select="idm/er">
                            <tr>       
                                <th>Status</th>
                                <td>
                                    <xsl:if test="specId/@documentStatus='NP'">
                                            <bool>&#160;New Proposal</bool> 
                                    </xsl:if>
                                    <xsl:if test="specId/@documentStatus='WD'">
                                            <bool>&#160;Working Draft</bool> 
                                    </xsl:if>
                                    <xsl:if test="specId/@documentStatus='PUB'">
                                            <bool>&#160;Publication</bool> 
                                    </xsl:if>
                                    <xsl:if test="specId/@documentStatus='WDRL'">
                                            <bool>&#160;Withdrawal</bool> 
                                    </xsl:if>                                  
                                </td>                                                                                         
                            </tr>   
                        </xsl:for-each>                    
                    </table>

                </xsl:if>

                <!--Table for Changelog-->                 
                                
                <table class="c_table" style="margin-top: 20px;">

                    <tr>
                        <th colspan ="4" style="font-weight: bold; background-color:#c0fec8;">Change log</th>                           
                    </tr>

                    <tr>                            
                        <th>Changed Date</th>    
                        <th>Changed Element</th> 
                        <th>Changed From</th> 
                        <th>Changed by</th>                       
                    </tr>

                
                    <xsl:for-each select="(idm/er/authoring/changeLog/change/@changedFrom)[generate-id(.) = generate-id(key('dup_er', .))]">
                        <xsl:sort select="."/>

                            <tr>
                                <td><xsl:value-of select="../../@changeDateTime"/></td>
                                <td><xsl:value-of select="../@changedElement"/></td>                                  
                                <td>                                                       
                                    <xsl:value-of select="." />                                   
                                </td>
                                <xsl:if test="../../@changedBy =../../../author/@id">
                                    <td>
                                        <xsl:value-of select="../../../author/@firstName"/>&#160;<xsl:value-of select="../../../author/@lastName"/>
                                    </td>                                                     
                                </xsl:if>                    
                            </tr>       

                    </xsl:for-each>                                                  
        
                </table>

                <xsl:if test="idm/er/description/content != ''">
                    <h5>Description</h5>
                    <table Class="basicInfo" style="margin-top: 5px; margin-bottom: 40px;"> 
                                
                            <tr>                               
                                <td><xsl:value-of select="idm/er/description/content"/></td>                               
                            </tr>       
                                        
                    </table> 
                </xsl:if> 

                <!-- SubER_Information Unit --> 
                <xsl:for-each select="idm/er/subEr/er">      
                <table Class="additionalInfo" style="margin-top: 15px;">                                                                            

                    <tr >
                        <th style ="font-family:'Calibri'; text-align:center;" colspan="9">sub_<bool style ="text-transform:capitalize;"><xsl:value-of select="specId/@shortTitle" /></bool></th>
                    </tr>                        
                    
                    <tr>
                        <th colspan="2" style= "font-family:'Calibri'; font-weight:bold;">Element Name</th>
                        <th colspan="4" style= "font-family:'Calibri';font-weight:bold;">Definition</th>
                        <th style= "font-family:'Calibri';font-weight:bold;">Required</th>
                        <th style= "font-family:'Calibri';font-weight:bold;">Data Type</th>                               
                        <th style= "font-family:'Calibri';font-weight:bold;">Example</th>    
                    </tr>

                    <xsl:for-each select="informationUnit">  

                        <tr>                                    
                            <td colspan="2"><xsl:value-of select="@name"/></td>
                            <td colspan="4"><xsl:value-of select="@definition" disable-output-escaping="yes"/></td>
                            <td style ="text-align: justify;">
                                <xsl:if test="@isMandatory='true'">
                                        <bool style ="text-align: center;" >O</bool> 
                                </xsl:if>
                                <xsl:if test="@isMandatory='false'">
                                        <bool style ="text-align: center;">X</bool> 
                                </xsl:if>
                            </td>
                            <td><xsl:value-of select="@dataType"/></td>   
                            <td><xsl:value-of select="examples/description/content"/></td>                                      
                        </tr>

                        <xsl:if test="subInformationUnit/informationUnit/@name != ''">                                                            
                                                            
                            <xsl:for-each select="subInformationUnit/informationUnit">
                    
                                <tr>  
                                    <td style="width:20px;">&#8627;</td>            
                                    <td ><xsl:value-of select="@name"/></td>
                                    <td colspan="4"><xsl:value-of select="@definition" disable-output-escaping="yes"/></td>
                                    <td style ="text-align: justify;">
                                        <xsl:if test="@isMandatory='true'">
                                                <bool style ="text-align: center;" >O</bool> 
                                        </xsl:if>
                                        <xsl:if test="@isMandatory='false'">
                                                <bool style ="text-align: center;">X</bool> 
                                        </xsl:if>
                                    </td> 
                                    <td><xsl:value-of select="@dataType"/></td>   
                                    <td><xsl:value-of select="examples/description/content"/></td>                                               
                                </tr>

                                <xsl:for-each select="subInformationUnit/informationUnit">   

                                    <tr>  
                                        <td style="width:20px;">&#8627;</td>            
                                        <td style="background-color: #FFFFFF;"><xsl:value-of select="@name"/></td>
                                        <td style="background-color: #C6C6C6;" colspan="4"><xsl:value-of select="@definition" disable-output-escaping="yes"/></td>
                                        <td style ="background-color: #C6C6C6; text-align: justify;">
                                            <xsl:if test="@isMandatory='true'">
                                                    <bool style ="text-align: center;" >O</bool> 
                                            </xsl:if>
                                            <xsl:if test="@isMandatory='false'">
                                                    <bool style ="text-align: center;">X</bool> 
                                            </xsl:if>
                                        </td> 
                                        <td style="background-color: #C6C6C6;" ><xsl:value-of select="@dataType"/></td>  
                                        <td style="background-color: #C6C6C6;" ><xsl:value-of select="examples/description/content"/></td>                                                
                                    </tr>
                                </xsl:for-each>
                        
                            </xsl:for-each>
                            
                        </xsl:if>
            
                    </xsl:for-each>

                </table>
            
            </xsl:for-each>


                
                
                </div>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>