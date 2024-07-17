# *Addresses* modelet glossary

## Named road or odonym

* **IGN[^1] definition**: communication route for cars, pedestrians, cycles or animals with a specific name and address[^2].
* **INSPIRE definition** : ‘equivalent’ concept: Thoroughfare. The address component subtype ‘thoroughfare name’ represents the name of a passage or thoroughfare from one place to another, such as a road or waterway. The most common examples of thoroughfare names are road names, but also names of watercourses, squares, cul-de-sacs or networks of small roads or paths, for example in a small village.

## Address

* **International Postal Union definition:** this is the complete location of the addressee of a letter[^3].
In France, a postal address consists of:
  * Line 1: the identity of the addressee (title, surname, first name).
  * Line 2: identification of the point of delivery (number of flat, floor, corridor, staircase).
  * Line 3: additional information on the location of the building (entrance, building, block of flats).
  * Line 4: house number and street name (street, avenue, hamlet).
  * Line 5: distribution service, additional information on the location of the road (poste restante, BP, locality for which the roads are named, etc.).
  * Line 6: postcode and town.
  * Line 7: name of country of destination [...].
* **ATILF[^4] definition:** The point at which an object is routed; by metonymy, the place where it is to be routed.
* **INSPIRE definition:** Location of properties based on address identifiers, usually street name, house number and postcode.
* **S. Baciocchi definition**: it is an interface between the plot of land/the premises/building and the street.

## Landmark
* A landmark here is a geographical feature or a geographical entity.
* **Commission toponymique du Québec definition**: ‘A named place or a place likely to be named. The entity is a specific portion of space; it is the geographic object considered in its individuality in relation to the surrounding space[^5].

## Number / Locator (INSPIRE)

**BAN[^6] Definition:** Numeric value giving the number of the address in the lane, without repetition index[^7].

## Complement
* A complement is a repetition index for BD TOPO[^8] or a suffix for BAN
* It allows to differentiate several numbers/locators with the same value

## Landmark types
### Thoroughfare
A thoroughfare defines any type of landmark whose goal is to move from one place to another. Here it includes streets, passageways, squares, culs-de-sac...

### City / Municipality
A municipality is an administrative division which may include a city or several agglomerations such as villages, hamlets... In France, a municipality is a commune.

### Postal code area
This kind of area also called *zip code area*, is an area used for postal distribution.

### District
A district is a subdivision a of city. For Paris, there are two levels of subdivision: arrondissement municipal (administrative district) and quartier administratif (administrative quarter). During the French Revolution, the districts of Paris were known as revolutionary sections and numbered 48.

### House number / Street number / District number
A house number is a unique number given to a building to ease its location. There are two ways of numbering:
* by thoroughfare (or street): the house number is a street number
* according to an area (a district for instance): the house number is a district number

For instance, "80 rue de Rivoli", 80 is a street number as *rue de Rivoli* is a thoroughfare whereas for "45 Palais-Royal", 45 is district number.

[^1]:IGN: Institut national de l'information géographique et forestière (French Mapping Agency).
[^2]:See BD TOPO V3.0 content description.
[^3]:See https://www.upu.int/UPU/media/upu/PostalEntitiesFiles/addressingUnit/FraFr.pdf
[^4]:ATILF: Analyse et Traitement Informatique de la Langue Française (French Language Analysis and Computer Processing Laboratory)
[^5]:See https://toponymie.gouv.qc.ca/ct/normes-procedures/terminologie-geographique/glossaire/entite-geographique.aspx
[^6]:BAN: Base adresse nationale (French national address database)
[^7]:See https://adresse.data.gouv.fr/docs/BAN_Descriptif_Donnees.pdf
[^8]:BD TOPO: vector database covering the whole of France and produced by IGN
