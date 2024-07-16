# Motivation Scenario for the Sources modelet

## Name

Sources

## Description

The Sources model aims to link the information described in the knowledge graph to the sources from which its originate.

A source has two main forms:
* Concept/general idea: content of the source considered independently of its concrete form;
* Concrete form, which can be:
    * Physical: physical copy of a document, usually characterised by an identifier and a location;
    * Digital: digitised version of a physical document, database, archive inventory...;
    * Derived: version obtained after automatic or manual processing (e.g., georeferenced map, transcribed page...) of a physical/digital source. There may be several derived forms of the same source.

A source may be divided into several parts, which in turn may be divided into coherent documentary elements (e.g., a register contains several pages that contain several zones, etc.).

A **source** can be described by the following properties:
* {*mandatory*} its **title**;
* {*mandatory*} its **type** (e.g., cadastral index map, assembly map of cadastral index maps, initial register, mutation register, folio, geographic reference...)
* {*optional*} its **type detail** (e.g., map from an atlas, original map, revised map, etc.)
* {*optional*} its **author** (individual or entity)
* {*optional*} its **creation date**
* {*optional*} its **start date of validity**
* {*optional*} its **end date of validity**
* {*optional*} its **description**
* {*if folio, mandatory*} its **folio number**
* {*if folio, optional*} its **alternative folio numbers**
* {*if folio, optional*} the **number of an equivalent folio** in another mutation register (previous, following, built)
* {*if physical or digitized archive: mandatory*} its **archive reference**
* {*physical: optional*} its **geographic location**
* {*physical, digital: optional*} its **dimensions**
* {*digital source: optional*} its **URL**
* {*digitized archive: optional*} its **coordinates in the image**
* {*digitized archive: optional*} its **order in an image**
* {*digitized archive: optional*} its **resolution**
* {*digitized archive: optional*} its **IIIF URL**
* {*digitized archive, derived: mandatory*} its **distribution license**
* {*derived: mandatory*} its **creation process**
(e.g., georeferencing, vectorization, transcription)
* {*derived: optional*} its **DOI**

## Examples

### Example 1: Forms of Sources (archival records)
- A mutation register contains an alphabetical list of taxpayers. This list is a serie of pages consisting in a list that contains multiple mentions of taxpayers.
- A paper copy of the mutation register is kept in an archive service and is identified by an archive reference.
- Each page has been digitised and has an archive reference.
- The elements contained in each page are identified and transcribed with a model (DAN).

### Example 2
> Example description of the initial register of Marolles-en-Brie in its different forms.

#### [Concept]

* **Title**: Initial register of Marolles-en-Brie
* **Type**: initial register
* **Creation Date**: 1810
* **Type Detail**: original register produced before 1822

#### [Physical Source]

* **Title**: Initial register of Marolles-en-Brie
* **Type**: initial register
* **Creation Date**: 1810
* **Type Detail**: original register produced before 1822
* **Archive Reference**: 3 P 387
* **Location**: Departmental Archives of Val-de-Marne

#### [Digitized Source]

* **Title**: Digitized initial register of Marolles-en-Brie
* **Type**: initial register
* **Type Detail**: original register produced before 1822
* **Creation Date**: 1810
* **Archive Reference**: FRAD094_3P_000387_01
* **License**: Etalab

#### [Derived Source]

* **Title**: Dataset containing the transcription of the initial register of Marolles-en-Brie
* **Type**: structured transcription
* **Creation Date**: November and December 2023
* **Creation Process**: manual annotation with Callico

### Example 3

> Example description of the cadastral index map of Section C of Marolles-en-Brie in its different forms

#### [Concept]

* **Title**: Cadastral index map of Section C "called the Village" Marolles-en-Brie
* **Type**: cadastral index map
* **Creation Date**: 1810

#### [Physical Source]

* **Title**: Cadastral index map of Section C "called the Village" Marolles-en-Brie
* **Type**: cadastral index map
* **Type Detail**: map from an atlas
* **Creation Date**: 1810
* **Archive Reference**: 3 P 1197
* **Location**: Departmental Archives of Val-de-Marne

#### [Digitized Source]

* **Title**: Digitized cadastral index map of Section C "called the Village" Marolles-en-Brie
* **Type**: cadastral index map
* **Type Detail**: map from an atlas
* **Creation Date**: 1810
* **Archive Reference**: FRAD094_3P_001197_01
* **License**: Etalab

#### [Derived Source]

* **Title**: Vectorized cadastral index map of Section C of Marolles-en-Brie
* **Type**: vectorized map
* **Creation Date**: May 2023
* **Creation Process**: manual annotation with QGIS