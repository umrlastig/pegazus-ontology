# Illustrated documentation of the Land Registry Landmarks extension

This page proposes illustrated representation of the ```Land Registry Landmarks``` sub-module of the *PeGazUs* ontology (extension dedicated to the land registry).
Please refer to the ontology to get the full definitions of each property.

## Ontology
### Plot properties
*Exemple developped with a landmark of type plot. It reprents the additions provided to described land plots.
For the precise temporal evolution details (changes, events), please refer to the core PeGazUs ontology (temporal evolution sub module).*
```mermaid
graph 
    %% 1. Nodes
    LandmarkNode(("addr:Landmark"))
    %%SectionNode(("addr:Landmark"))

    PlotId["string"]
    PlotLabel["string"]
    PlotType(("cad_ltype:Plot"))
    addrLandmarkType(("addr:LandmarkType"))

    %%PlotSectionLR
    %%SectionId["string"]
    %%SectionType(("cad_ltype:Section"))
    %%SectionCommuneLR
    %%CommuneId["string"]
    %%CommuneType(("cad_ltype:Commune"))

    addrAttributeTypeT(("addr:AttributeType"))
    addrAttributeTypeN(("addr:AttributeType"))
    addrAttributeTypeA(("addr:AttributeType"))
    addrAttributeTypeM(("addr:AttributeType"))

    TaxpayerAtt(("addr:Attribute"))
    NatureAtt(("addr:Attribute"))
    AddressAtt(("addr:Attribute"))
    MentionAtt(("addr:Attribute"))

    TaxpayerAttT(("cad_atype:PlotTaxpayer"))
    NatureAttT(("cad_atype:PlotNature"))
    AddressAttT(("cad_atype:PlotAddress"))
    MentionAttT(("cad_atype:PlotMention"))

    NatureAttV(("addr:AttributeVersion"))
    AddressAttV(("addr:AttributeVersion"))
    TaxpayerAttV(("addr:AttributeVersion"))
    MentionAttV(("addr:AttributeVersion"))

    TaxpayerValue(("cad:Taxpayer"))
    NatureValue(("cad:Nature"))
    AddressValue(("addr:Landmark"))
    MentionValue(("rico:Instantiation"))

    %% 2. Connect the unique IDs
    
    LandmarkNode == "dcterms:identifier" ==> PlotId 
    LandmarkNode == "rdfs:label" ==> PlotLabel
    LandmarkNode == "addr:isLandmarkType" ==> PlotType
    PlotType == "rdf:type" ==> addrLandmarkType

    LandmarkNode == "addr:hasAttribute" ==> TaxpayerAtt
    LandmarkNode == "addr:hasAttribute" ==> NatureAtt
    LandmarkNode == "addr:hasAttribute" ==> AddressAtt
    LandmarkNode == "addr:hasAttribute" ==> MentionAtt

    TaxpayerAtt == "addr:isAttributeType" ==> TaxpayerAttT
    TaxpayerAttT == "rdf:type" ==> addrAttributeTypeT
    TaxpayerAtt == "addr:hasAttributeVersion" ==> TaxpayerAttV
    TaxpayerAttV == "cad:hasTaxpayer" ==> TaxpayerValue

    NatureAtt == "addr:isAttributeType" ==> NatureAttT
    NatureAttT == "rdf:type" ==> addrAttributeTypeN
    NatureAtt == "addr:hasAttributeVersion" ==> NatureAttV
    NatureAttV == "cad:hasPlotNature" ==> NatureValue

    AddressAtt == "addr:isAttributeType" ==> AddressAttT
    AddressAttT == "rdf:type" ==> addrAttributeTypeA
    AddressAtt == "addr:hasAttributeVersion" ==> AddressAttV
    AddressAttV == "cad:hasPlotAddress" ==> AddressValue

    MentionAtt == "addr:isAttributeType" ==> MentionAttT
    MentionAttT == "rdf:type" ==> addrAttributeTypeM
    MentionAtt == "addr:hasAttributeVersion" ==> MentionAttV
    MentionAttV == "cad:isMentionnedIn" ==> MentionValue

    %% 3. Apply WebVOWL Style
    classDef vowlClass fill:#aaccff,stroke:#3366cc,stroke-width:2px,color:#000,font-weight:bold;

    classDef vowlClassInstance fill:#CB8DD6,stroke:#5F2569,stroke-width:2px,color:#000,font-weight:bold;

    classDef vowlLiteral fill:#ffffcc,stroke:#ffcc00,stroke-width:2px,color:#000;

    classDef vowlThing fill:#f5f5f5,stroke:#999999,stroke-width:2px,stroke-dasharray: 4,color:#000,font-style:italic;

    class LandmarkNode,PlotType,addrLandmarkType,NatureAtt,TaxpayerAtt,AddressAtt,MentionAtt,NatureAttV,TaxpayerAttV,AddressAttV,MentionAttV,TaxpayerValue,AddressValue,NatureValue,MentionValue,addrAttributeTypeA,addrAttributeTypeT,addrAttributeTypeN,addrAttributeTypeM vowlClass;

    class PlotType,NatureAttT,TaxpayerAttT,AddressAttT,MentionAttT,pNature vowlClassInstance;

    class PlotId,PlotLabel vowlLiteral;
    %%class  vowlThing;
```
### Plot relations with other landmarks

### Note
* ```rdfs:label``` can be used to provide a nice complete label of the plot (including identifier and commune name for instance).
* ```dcterms:identifier``` is used to provide the plot id.
* On use, instances of ```cad:Nature``` can be found in ```cad:NatureList``` SKOS concepts schema.

### Upcomming evolution
* ```cad_atype:PlotMention``` attribute type is going to be deprecated soon, replaced with by an attribute type with a more suitable name.
* ```cad:takenFrom``` property is going to be deprecated soon, replaced with by a property with a more suitable name.
* ```cad:passedTo``` property is going to be deprecated soon, replaced with by a property with a more suitable name.