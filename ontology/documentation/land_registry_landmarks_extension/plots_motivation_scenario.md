# Motivation scenario of the Land Registry Landmarks extension

## Nom
Addresses modelet : land registry landmarks extension

## Description

A **plot** is a specific kind of landmark. It is the base **geographical features** used to decide the land taxes. It is defined by its son **identifier** (section letter + plot number), its **nature**, its **taxpayer**, its size and its value. A plot is localised in a cadstral section. Plot numbering is realized in each section.

A **section** is located in a commune. This **commune** is the base administrative unit of a hierarchy : cantons, arrondissements and départements. The land registry production was organised by each departement. 

To ease the retrieval of a plot in a section, each plot was associated with an address : a named place, a street, an other landmark...

Plots and non cadastral features (like roads, rivers etc.) are the two main types of geographical features that cover the whole territory.

A **plot** can be described by the following properties :
- {*mandatory*} its **type** (plot, section, commune etc.)
- {*mandatory*} its **adress** / its **location**
- {streets, *optionnal*} its **name** or **label**
- {plot, section:*mandatory*} its **cadastral number**
- {plot: *mandatory*} its **nature**
- {plot: *mandatory*} its **taxpayers**
- {*optional*} its **geometry**

## Examples

### Example 1 [Plot]
<ul>
    <li>Number : A-207</li>
    <li>Type : Plot</li>
    <li>Location : Lieu-dit Le Village, Section A, Commune de Boissy-Saint-Léger (The Village, Section A, Commune of Boissy-Saint-Léger) </li>
    <li>Taxpayer : Charlier</li>
    <li>Nature : Pasture</li>
</ul>
 - FRA094_3P_000065_01_0030, Initial register of Boissy-Saint-Léger, 1810

 ### Example 2 [Non-cadastral object]
<ul>
    <li>Name : Grande route de Paris à Provins (Great road fromParis to Provins)</li>
    <li>Type : road</li>
    <li>Location : Section A, Commune de Boissy-Saint-Léger (Section A, Commune of Boissy-Saint-Léger)</li>
</ul>
 - FRA094_3P_000851, Cadastral index map, section C, Boissy-Saint-Léger, 1810

### Example 3 [Section]
<ul>
    <li>Identifier : A</li>
    <li>Name : Section A dite du Piple</li>
    <li>Type : Section</li>
    <li>Location : Commune de Boissy-Saint-Léger, Justice de Paix de Boissy-Saint-Léger, Arrondissement de Corbeil, Département de Seine-et-Oise</li>
</ul>
 - FRA094_3P_000065_01_0001, Initial register of Boissy-Saint-Léger, 1810

### Example 4 [Commune]
<ul>
    <li>Name : Boissy-Saint-Léger</li>
    <li>Type : Commune</li>
    <li>Location : Justice de Paix de Boissy-Saint-Léger, Arrondissement de Corbeil, Département de Seine-et-Oise</li>
</ul>
 - FRA094_3P_000065_01_0001, Initial register of Boissy-Saint-Léger, 1810