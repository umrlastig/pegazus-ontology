# Illustrated documentation of the Land Registry Landmarks extension

This page proposes illustrated representation of the ```Land Registry Landmarks``` sub-module of the *PeGazUs* ontology (extension dedicated to the land registry).
Please refer to the ontology to get the full definitions of each property.

## Ontology
*Exemple developped with a landmark of type plot. It reprents the additions provided to described land plots.
For the precise temporal evolution details (changes, events), please refer to the core PeGazUs ontology (temporal evolution sub module).*
```mermaid
graph 
    %% 1. Nodes
    LandmarkNode(("addr:Landmark"))
    %%SectionNode(("addr:Landmark"))

    PlotId["string"]
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

    TaxpayerAtt(("addr:Attribute"))
    NatureAtt(("addr:Attribute"))
    AddressAtt(("addr:Attribute"))

    TaxpayerAttT(("cad_atype:PlotTaxpayer"))
    NatureAttT(("cad_atype:PlotNature"))
    AddressAttT(("cad_atype:PlotAddress"))

    NatureAttV(("addr:AttributeVersion"))
    AddressAttV(("addr:AttributeVersion"))
    TaxpayerAttV(("addr:AttributeVersion"))

    TaxpayerValue(("cad:Taxpayer"))
    NatureValue(("cad:Nature"))
    AddressValue(("addr:Landmark"))

    %% 2. Connect the unique IDs
    
    LandmarkNode == "dcterms:identifier" ==> PlotId 
    LandmarkNode == "addr:isLandmarkType" ==> PlotType

    LandmarkNode == "addr:hasAttribute" ==> TaxpayerAtt
    LandmarkNode == "addr:hasAttribute" ==> NatureAtt
    LandmarkNode == "addr:hasAttribute" ==> AddressAtt

    TaxpayerAtt == "addr:isAttributeType" ==> TaxpayerAttT
    TaxpayerAttT == "a" ==> addrAttributeTypeT
    TaxpayerAtt == "addr:hasAttributeVersion" ==> TaxpayerAttV
    TaxpayerAttV == "cad:hasTaxpayer" ==> TaxpayerValue

    NatureAtt == "addr:isAttributeType" ==> NatureAttT
    NatureAttT == "a" ==> addrAttributeTypeN
    NatureAtt == "addr:hasAttributeVersion" ==> NatureAttV
    NatureAttV == "cad:hasPlotNature" ==> NatureValue

    AddressAtt == "addr:isAttributeType" ==> AddressAttT
    AddressAttT == "a" ==> addrAttributeTypeA
    AddressAtt == "addr:hasAttributeVersion" ==> AddressAttV
    AddressAttV == "cad:hasPlotAddress" ==> AddressValue

    %% 3. Apply WebVOWL Style
    classDef vowlClass fill:#aaccff,stroke:#3366cc,stroke-width:2px,color:#000,font-weight:bold;

    classDef vowlClassInstance fill:#CB8DD6,stroke:#5F2569,stroke-width:2px,color:#000,font-weight:bold;

    classDef vowlLiteral fill:#ffffcc,stroke:#ffcc00,stroke-width:2px,color:#000;

    classDef vowlThing fill:#f5f5f5,stroke:#999999,stroke-width:2px,stroke-dasharray: 4,color:#000,font-style:italic;

    class LandmarkNode,PlotType,addrLandmarkType,NatureAtt,TaxpayerAtt,AddressAtt,NatureAttV,TaxpayerAttV,AddressAttV,TaxpayerValue,AddressValue,NatureValue,addrAttributeTypeA,addrAttributeTypeT,addrAttributeTypeN vowlClass;

    class PlotType,NatureAttT,TaxpayerAttT,AddressAttT,pNature vowlClassInstance;

    class PlotId vowlLiteral;
    %%class  vowlThing;
```

### Note
* ```rdfs:label``` can be used to provide a nice complete label of the plot (including identifier and commune name for instance).
* ```dcterms:identifier``` is used to provide the plot id.


## Examples
*Barbaroux quincailler à Paris*
```mermaid
graph 
    %% ----- Noeuds -----
    %% 1. Syntaxe : ID("Nom affiché <br> <i>[Type de la classe]</i>")
    PlotInst(("'landmark:A 207 Boissy Saint Léger', <br><small>a addr:Landmark</small>"))
    
    %% Littéraux (Valeurs concrètes de Datatype Properties)
    PlotInstId["'A-207'^^xsd:string"]

    %% ------ Relations -------
    %% Object Property (Lien entre individus) : Ligne pleine
    %% TaxpayerInst -- "cad:hasAddress" --> AddressInst
    
    %% Datatype Properties
    PlotInst -- "dcterms:identifier" --> PlotInstId
    TaxpayerInst -- "cad:taxpayerLastName" --> LastNameLit
    TaxpayerInst -- "cad:taxpayerActivity" --> ActivityLit
    TaxpayerInst -- "cad:taxpayerAddress" --> AddressLit

    %% ------- STYLES ------
    %% Violet VOWL pour les instances
    classDef vowlInstance fill:#ece0f8,stroke:#d397d3,stroke-width:2px,color:#000;
    %% Jaune VOWL pour les valeurs litérales
    classDef vowlValue fill:#ffffcc,stroke:#ffcc00,stroke-width:1px,color:#000,font-family:monospace;

    %% Application des styles aux données
    class PlotInst,InstanceNode vowlInstance;
    class FullNameLit,LastNameLit,AddressLit,ActivityLit,LiteralVal vowlValue;
    class Src1,Tgt1,Src2,Tgt2 invisible;
```
*Pravel Louis Ve née Gerbuisson*
```mermaid
graph 
    %% ----- Noeuds -----
    %% 1. Syntaxe : ID("Nom affiché <br> <i>[Type de la classe]</i>")
    TaxpayerInst2("taxpayer:pravel_louis_vve<br><small>a cad:Taxpayer</small>")
    
    %% Littéraux (Valeurs concrètes de Datatype Properties)
    FullNameLit["'Pravel Louis Ve née Gerbuisson'^^xsd:string"]
    LastNameLit["'Pravel'^^xsd:string"]
    FirstNamesLit["'Louis'^^xsd:string"]
    FamilyStatusLit["'Ve'^^xsd:string"]
    BirthNameLit["'Gerbuisson'^^xsd:string"]
    
    %% Datatype Properties
    TaxpayerInst2 -- "cad:taxpayerFullName" --> FullNameLit
    TaxpayerInst2 -- "cad:taxpayerLastName" --> LastNameLit
    TaxpayerInst2 -- "cad:taxpayerFirstNames" --> FirstNamesLit
    TaxpayerInst2 -- "cad:taxpayerFamilyStatus" --> FamilyStatusLit
    TaxpayerInst2 -- "cad:taxpayerBirthName" --> BirthNameLit

    %% ------- STYLES ------
    %% Violet VOWL pour les instances
    classDef vowlInstance fill:#ece0f8,stroke:#d397d3,stroke-width:2px,color:#000;
    %% Jaune VOWL pour les valeurs litérales
    classDef vowlValue fill:#ffffcc,stroke:#ffcc00,stroke-width:1px,color:#000,font-family:monospace;

    %% Application des styles aux données
    class TaxpayerInst2,InstanceNode vowlInstance;
    class FullNameLit,LastNameLit,FirstNamesLit,FamilyStatusLit,BirthNameLit,LiteralVal vowlValue;
    class Src1,Tgt1,Src2,Tgt2 invisible;

    %% Couleur violette pour les flèches d'Object Properties (Liens entre instances)
    %% Index 0 (hasAddress) et Index 2 (Légende Object Property)
    %% linkStyle 0,2 stroke:#b573b5,stroke-width:2px;
```