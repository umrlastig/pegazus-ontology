# Illustrated documentation of Taxpayers

This page proposes illustrated representation of the ```Taxpayer``` sub-module of the *PeGazUs* ontology.
Please refer to the ontology to get the full definitions of each property.

## Ontology
### Datatype properties
```mermaid
graph 
    %% 1. Nodes
    TaxpayerNode(("cad:Taxpayer"))
    LabelLit["string"]
    NameLit["string"]
    LastNameLit["string"]
    FirstNamesLit["string"]
    BirthNameLit["string"]
    SpouseOrChildrenFirstNames["string"]
    OrganisationNameLit["string"]
    ActivityLit["string"]
    AddressLit["string"]
    FamilyStatusLit["string"]
    TitleLit["string"]

    %% 2. Connect the unique IDs
    
    TaxpayerNode == "cad:taxpayerLabel" ==> LabelLit 
    TaxpayerNode == "cad:taxpayerFullName" ==> NameLit 
    TaxpayerNode == "cad:taxpayerLastName" ==> LastNameLit
    TaxpayerNode == "cad:taxpayerFirstNames" ==> FirstNamesLit
    TaxpayerNode == "cad:taxpayerBirthName" ==> BirthNameLit
    TaxpayerNode == "cad:taxpayerSpouseOrChildrenFirstNames" ==> SpouseOrChildrenFirstNames
    TaxpayerNode == "cad:taxpayerOrganisationName" ==> OrganisationNameLit
    TaxpayerNode == "cad:taxpayerActivity" ==> ActivityLit
    TaxpayerNode == "cad:taxpayerAddress" ==> AddressLit
    TaxpayerNode == "cad:taxpayerFamilyStatus" ==> FamilyStatusLit
    TaxpayerNode == "cad:taxpayerTitle" ==> TitleLit

    %%LabelLit ~~~ NameLit ~~~ LastNameLit ~~~ FirstNamesLit ~~~ BirthNameLit ~~~ SpouseOrChildrenFirstNames ~~~ OrganisationNameLit ~~~ ActivityLit ~~~ AddressLit ~~~ FamilyStatusLit ~~~ TitleLit

    %% 3. Apply WebVOWL Style
    classDef vowlClass fill:#aaccff,stroke:#3366cc,stroke-width:2px,color:#000,font-weight:bold;
    classDef vowlLiteral fill:#ffffcc,stroke:#ffcc00,stroke-width:2px,color:#000;

    class TaxpayerNode vowlClass;
    class LabelLit,NameLit,LastNameLit,FirstNamesLit,ActivityLit,AddressLit,TitleLit,OrganisationNameLit,SpouseOrChildrenFirstNames,BirthNameLit,FamilyStatusLit vowlLiteral;
```
### Object properties
```mermaid
graph 
    %% 1. Nodes
    TaxpayerNode(("cad:Taxpayer"))
    AddressThingNode(("owl:Thing"))

    %% 2. Connect the unique IDs
    TaxpayerNode == "cad:taxpayerAddressEntity" ==> AddressThingNode

    %% 3. Apply WebVOWL Style
    classDef vowlClass fill:#aaccff,stroke:#3366cc,stroke-width:2px,color:#000,font-weight:bold;
    %% WebVOWL Style for owl:Thing
    classDef vowlThing fill:#f5f5f5,stroke:#999999,stroke-width:2px,stroke-dasharray: 4,color:#000,font-style:italic;
    
    class TaxpayerNode,AddressEnt vowlClass;
    class AddressThingNode vowlThing;
```
### Note
* ```cad:taxpayerLabel``` is a super-property for ```cad:taxpayerFullName``` (natural person) and ```cad:taxpayerOrganisationName``` (legal person). It can be used when the kind of taxpayer is not known.
* ```cad:taxpayerAddressEntity``` can be used when the value associated to ```cad:taxpayerAddress``` as been linked to any geographical entity of a KG. For instance, it can be an ```addr:Landmark``` entity.
* Upcomming developpements will create object properties for actitivies, family status and titles.

## Examples
*Barbaroux quincailler à Paris*
```mermaid
graph 
    %% ----- Noeuds -----
    %% 1. Syntaxe : ID("Nom affiché <br> <i>[Type de la classe]</i>")
    TaxpayerInst("taxpayer:barbaroux<br><small>a cad:Taxpayer</small>")
    
    %% Littéraux (Valeurs concrètes de Datatype Properties)
    FullNameLit["'Barbaroux'^^xsd:string"]
    LastNameLit["'Barbaroux'^^xsd:string"]
    ActivityLit["'quincailler'^^xsd:string"]
    AddressLit["'Paris'^^xsd:string"]

    %% ------ Relations -------
    %% Object Property (Lien entre individus) : Ligne pleine
    %% TaxpayerInst -- "cad:hasAddress" --> AddressInst
    
    %% Datatype Properties
    TaxpayerInst -- "cad:taxpayerFullName" --> FullNameLit
    TaxpayerInst -- "cad:taxpayerLastName" --> LastNameLit
    TaxpayerInst -- "cad:taxpayerActivity" --> ActivityLit
    TaxpayerInst -- "cad:taxpayerAddress" --> AddressLit

    %% ------- STYLES ------
    %% Violet VOWL pour les instances
    classDef vowlInstance fill:#ece0f8,stroke:#d397d3,stroke-width:2px,color:#000;
    %% Jaune VOWL pour les valeurs litérales
    classDef vowlValue fill:#ffffcc,stroke:#ffcc00,stroke-width:1px,color:#000,font-family:monospace;

    %% Application des styles aux données
    class TaxpayerInst,InstanceNode vowlInstance;
    class FullNameLit,LastNameLit,AddressLit,ActivityLit,LiteralVal vowlValue;
    class Src1,Tgt1,Src2,Tgt2 invisible;

    %% Couleur violette pour les flèches d'Object Properties (Liens entre instances)
    %% Index 0 (hasAddress) et Index 2 (Légende Object Property)
    %% linkStyle 0,2 stroke:#b573b5,stroke-width:2px;
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