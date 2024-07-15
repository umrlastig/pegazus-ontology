# Motivation Scenario for the land registry documents use modelet

## Name

Cadastral Documentation: Use of Registers

## Description

### Documents

The Napoleonic cadastre is composed of a set of documents created and supplemented according to defined rules. This modelet aims to describe cadastral documentation not as a source but as an administrative object whose operation can be likened to that of a handwritten database. The models **Sources** and **Cadastral Documentation** are intrinsically linked.

The registers that make up the cadastral documentation are the initial registers and the mutation registers.

The **initial registers** are composed of chapters. Each chapter begins with a cover page describing the section in question (name, identifier) and a table where each row corresponds to the initial register of a plot at the creation of the cadastre. Before 1822, there are also chapters dedicated to the taxation of built properties.
To assemble the data contained in the initial registers:
- the order of the pages "Covers" then "Table" must be taken into account to construct the plot identifiers.
- the table may contain a column indicating the identifier of a taxpayer in the mutation register (to be used as a join field)
- in the majority of cases, it is the name of the taxpayer in the initial register that allows finding their folio in the mutation register.

The **mutation registers** contain a set of tables whose structure varies over time. Called, "article", "**folio**" or "case", the main table pages associate an identifier number with one or more sets composed of a list of taxpayers and the states of plots associated with them.

If for a folio number, there are several sets 'successive taxpayers/list of plot states', each set will be called a **land account**.

According to the 1810 Collection, each folio is divided into two parts:
- the list of successive taxpayers associated with it, called "**mutation article**" in the <i>1811 Collection</i>:
- the states of plots held by this (these) taxpayer(s), called "**classification articles**" in the <i>1811 Collection</i>:

A **land account** is thus the list of plots belonging to a given taxpayer for a given period.
The land account of a taxpayer can be described in one or more folios, consecutive or not, in one or more mutation registers.

### Detailed Operation

In each plot state, it is indicated the folio in which the plot was found before its last modification ("Taken from") and in which folio it is added after the next modification ("Passed to").
Events concerning the properties (mainly built) are also indicated in these columns: "New construction" (C.N/N.C), "Increase" (Inc), "Building assessment" (B.A.), "Destruction", "Ruin".
Passages from one folio to another are particularly useful information for ordering the different states of the same plot in chronological order or deducing mergers/divisions.

The obsolete lines of a land account are crossed out.
A fully crossed out land account is closed.

## Examples

### Example 1 [Article (folio)]
> Article 42, Mutation Register (1810-1822), Marolles-en-Brie
- **Number**: 42
- **Taxpayer**: Lhuillier Veuve Vigneronne in Marolles (1812-1822)
- **List of mentioned plots**:
    - A-44 (1812-1822)
    - D-115 (1812-1822)
    - D-118 (1812-1822)
- **Mutation Register**: Mutation Register of Marolles-en-Brie (1810-1822)

### Example 2 [Folio]
> Folio 602/1040, Mutation Register of land/non-built properties (1822-1914), Champigny-sur-Marne (<a href="https://github.com/solenn-tl/ontologie-cadastre/blob/main/comptes_fonciers/img/folio_champigny_FRAD094_3P_000108_01_0004.PNG">View the image</a>)
- **Number**: 602 <i>AND</i> 1040
- **Taxpayer**:
    - Macreau Laurent in Chennevière
    - Bessault Louis in Champigny, rue du Bousquet
    - Coutable Eugène 141 Grande Rue in Champigny 1906
- **List of mentioned plots**:
    - C-1474 (1822-1861)
    - F-758p (1893-1847)
    - C-1028 (1906-1914)
- **Mutation Register**: Mutation Register of land/non-built properties (1822-1914), Champigny-sur-Marne