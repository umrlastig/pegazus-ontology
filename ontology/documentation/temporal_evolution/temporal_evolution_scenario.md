# Time modelet argument

## Name
Modelling the temporal evolution of geographic features

## Description

The objective of this thesis is to propose an approach for creating a knowledge base of addresses and streets in the city of Paris from the end of the 18th century to the 1950s. The work is not done at a given moment but over a period of time. The temporal aspect must therefore be taken into account in order to link in time all the attestations of names or the location of landmarks making up a given address.

These statements are references to the value or modification of a landmark characteristic in a historical source: they describe the **states** of the landmarks or the **events** that happen to them. These states and events occur one after the other over time and are linked by cause and effect: for example, two successive states of a street, associated with different name values, are linked by a **name change event**. This name change event cannot appear in the evolution model unless this condition of different names is verified.

The events that can occur during the existence of a benchmark are:
* appearance
* disappearance
* reincarnation
* change of property value: official name, customary name, location (merger, split, extension), etc.

See the typology of events given in *Kathleen Hornsby and Max J. Egenhofer. Identity-based change: a foundation for spatio-temporal knowledge representation. International Journal of Geographical Information Science, 14(3) :207-224, April 2000.

A landmark may be mentioned in a source before it exists in the field: its creation is planned by the town hall, for example. It may be mentioned after it has disappeared (‘old hotel X’).

The properties of landmarks mentioned in sources are:
* existence
* name (official or customary)
* location (from textual cartographic sources as landmarks)

These properties are characterised by:
* a valid time
* source(s) that attest to their value
* their type
* their value

Valid time corresponds to an interval whose boundaries correspond to events.

Time-related quantities can be distinguished:
* an instant: very short duration (tending towards 0) which can be described by a time value with a defined level of granularity (~precision). An instant can be used to describe an event, indicating the moment during which it occurs.
* a time interval: this corresponds to a more or less long duration defined (if possible) by two instants which indicate the beginning and the end. An instant can be used to describe a state, indicating the period during which the state is valid.

However, there may be differences in granularity between the data we wish to create and that found in geohistorical sources. There may also be inaccuracies. For example, we often find precise data on the creation of tracks but rarely on their destruction.

This is why it is important to introduce the notion of vagueness. For example, an instant can be described in the form of an interval with a probability distribution around an instant. The same can be done with an interval. Similarly, the existence of events which are not dated but which have relationships with others which are (X before Y, X during Y) also implies the use of these fuzzy times.

Since it is necessary to track the evolution of streets and addresses, we need to know which state follows the other, hence the need to be able to make comparisons between these temporal quantities. Comparing two instants is easy (t1 < t2 if t1 exists before t2, t1=t2 if they exist at the same moment, t1). For two intervals, there are more relationships defined by Allen's interval algebra.

### Expected characteristics of time quantities

An instant is defined by :
* {mandatory} time value (date, time...)
* {mandatory} granularity (precision to the year, day, second, etc.)
* {mandatory} time reference (calendar used, time zone)

An interval is defined by :
* {required} an initial time
* {required} a final time
* {optional} method of defining the interval (the interval can be defined from an initial instant and a duration, which implies knowledge of the final instant / the extreme instants can simply be known...)
* {optional} relationship with another interval (Allen algebra)

A fuzzy interval is defined by :
* {mandatory} a core interval I_core (or instant), the interval where we are certain of the existence of the object (the set of instants such that their membership function is 1);
* {mandatory} an interval I_start such that I_start m I_core, designates the instants whose membership function is in ]0,1[ and located before I_core ;
* {mandatory} an interval I_end such that I_end mi I_core, designates the instants whose membership function is in ]0,1[ and located after I_core;

:warning: We can add membership functions if we assume that they are not linear.

A duration is defined (:warning: interesting?) by :
* {mandatory} value
* {mandatory} unit of time (years, minutes...)

## Examples

### Instants / events

In the database of *Names of rights-of-way for existing roads* (in Paris), we find dates of naming decrees which describe an event (creation/modification of a name) with a level of granularity to the day:
>*Dénomination complète minuscule;Date de l'arrété
promenade Germaine Sablon;2022-01-24
rue du Général Appert;1900-12-07
rue Leneveux;1899-08-02
rue Isabey;1867-03-02*

### Intervals / states
Sur la page Wikipédia sur la rue Abel Laurent (https://fr.wikipedia.org/wiki/Rue_Abel-Laurent), on trouve l'information suivante :
*Cette rue a été ouverte en 1878. Elle disparait vers 1993, lors de la démolition des entrepôts de Bercy, dans le cadre de l'aménagement de la ZAC de Bercy.*
Cette phrase décrit l'état d'existence de la rue, l'intervalle a un instant de fin flou.

The French Wikipedia page on rue Abel Laurent (https://fr.wikipedia.org/wiki/Rue_Abel-Laurent) contains the following information: *Cette rue a été ouverte en 1878. Elle disparait vers 1993, lors de la démolition des entrepôts de Bercy, dans le cadre de l'aménagement de la ZAC de Bercy.* (*This street was opened in 1878. It disappeared around 1993, when the Bercy warehouses were demolished as part of the development of the Bercy ZAC*.) This sentence describes the state of existence of the street, the interval has a vague end.

### Fuzzy time
On Verniquet's atlas: ‘parachevé en 1791’ (‘completed in 1791’), no information on the date of the survey. Title at the bottom of the map: ‘Paris de 1789 à 1798’.

### Granularity
Extract of *Dictionnaire administratif et historique des rues de Paris et de ses monuments* by Félix Lazare :
>*ALIGRE (RUE D') [...] <br/>Cette rue, ouverte en décembre 1778 [...] <br/> avait été autorisée par des lettres-patentes du 17 février 1777*
