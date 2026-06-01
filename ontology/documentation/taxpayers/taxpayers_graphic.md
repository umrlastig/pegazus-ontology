# Graphic documentation of Taxpayers

This page proposes a graphic representation of the ```Taxpayer``` modelet of the *PeGazUs* ontology.
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
    MaidenNameLit["string"]
    OrganisationNameLit["string"]
    ActivityLit["string"]
    AddressLit["string"]
    FamilyStatusLit["string"]
    TitleLit["string"]

    %% 2. Connect the unique IDs
    LabelLit <== "cad:taxpayerLabel" ==> TaxpayerNode
    NameLit == "cad:taxpayerFullName" ==> TaxpayerNode
    LastNameLit == "cad:taxpayerLastName" ==> TaxpayerNode
    FirstNamesLit == "cad:taxpayerFirstNames" ==> TaxpayerNode
    MaidenNameLit == "cad:taxpayerMaidenName" ==> TaxpayerNode
    OrganisationNameLit == "cad:taxpayerOrganisationName" ==> TaxpayerNode
    TaxpayerNode == "cad:taxpayerActivity" ==> ActivityLit
    TaxpayerNode == "cad:taxpayerAddress" ==> AddressLit
    TaxpayerNode == "cad:taxpayerFamilyStatus" ==> FamilyStatusLit
    TaxpayerNode == "cad:taxpayerTitle" ==> TitleLit

    %% 3. Apply WebVOWL Style
    classDef vowlClass fill:#aaccff,stroke:#3366cc,stroke-width:2px,color:#000,font-weight:bold;
    classDef vowlLiteral fill:#ffffcc,stroke:#ffcc00,stroke-width:2px,color:#000;

    class TaxpayerNode vowlClass;
    class LabelLit,NameLit,LastNameLit,FirstNamesLit,ActivityLit,AddressLit,TitleLit,OrganisationNameLit,MaidenNameLit,FamilyStatusLit vowlLiteral;
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
* ```cad:taxpayerLabel``` is a super-property for ```cad:taxpayerFullName``` and ```cad:taxpayerOrganisationName```.
* ```cad:taxpayerAddressEntity``` can be used when the value associated to ```cad:taxpayerAddress``` as been linked to any geographical entity of a KG. For instance, it can be an ```addr:Landmark``` entity.
* Upcomming developpements will create object properties for actitivies, family status and titles.