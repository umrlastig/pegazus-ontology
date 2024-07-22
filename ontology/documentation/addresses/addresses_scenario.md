# *Addresses* modelet description

## Name
Street and address modeling

## Description

The aim of this modelet is to propose an approach for creating a knowledge base of addresses and streets in the city of Paris, from the end of the 18th century to the 1950s. In particular, this database should be able to be used to geocode spatially and temporally different types of resources mentioning addresses via their wording, in this area and during this period. The wording of an address generally contains the name of the street giving access to the premises or plot designated by the address. It often also includes a number, which identifies the premises/plot/door within the street. The numbering logic varies over the two centuries covered by the database. A distinction is made between:
* 1779-1791: Royal numbering or Kreenfeldt numbering
* 1791-1805: Sectional numbering
* 1805: Empire numbering

In sectional numbering, unlike the other two, the numbers are chosen in relation to an area of the city (known as a ‘revolutionary section’) and not in relation to the street. Sectional’ addresses therefore generally specify the name of the section.
An address is therefore characterised by:
- {mandatory} name of geographical reference area (street or section)
- {mandatory} number
- {optional} number complement (bis, ter, quater)
- {mandatory if sectional numbering} sub-geographical reference area (street name)
- {optional} district/borough name
- {optional} direct spatial reference (coordinates, geometry, etc.)
- {optional} valid time (interval, instant)

For example, in the Duverneuil and La Tynna directory of 1801, we find the following addresses for cutlers:
>*Baillet, R. de Grenelle, 86. Unité.
Bardet, R. Aubry le Boucher, 28. Lombards.
Bariole, R. de Seine, 1434. Unité.*

The addresses below are examples of royal numbering, taken from the Almanach of 1787:
>*Abzac, Miſe d', R. Montmartre, 229.
Aché, Miſe d', S. André, 43.
Acheres, B.d',R. S. Thomas du L. 38.
Adelbert, C. d', R. de l'Université, 117

The addresses below are examples of Empire numbering, taken from the Bottin of 1838:
>*Arnoux, confiseur, Fg-Montmartre, 11.
Arsène, fab. biscuits de Reims, Fg-St-Antoine, 267.
Arpin (Hipp.), prop., Provence, 36.*

Directories give more general addresses, such as ‘opposite the royal palace’, or ‘at the corner of X street and Y avenue’.

## Examples

Here is an inventory of addresses that can be found in different sources.

### 1 - Historical sources: City of Paris trade directories
* "situé sur le blv. de Clichy, dans la partie comprise entre la place Blan- che et la rue Fontaine"
* "au centre de la capitale, entre le Palais-Royal et les Tuileries, à proximité des principaux the..."
* "Panorama national des Champs-Elysees, entre le cours de la Reine et le grand carre des fêtes"
* "Galerie Vivienne, en entrant par la rue Vivienne, le premier grand escalier à gauche"
* "Au chantier de la Victoire, boulevart des Invalides, au coin de la rue de Sèvres"
* "Jardin du Palais-Royal, pavillon de Foy, à droite de la rotonde, côté du théâtre"
* "Situé sur les trottoirs de la rue St-Charles, entre les rues de Javel et Cauchy"
* "avenue de Neuilly, rond-point de l’Arc-de-Triomphe, dans la cité de l'Etoile"
* "Rive droite de la Seine de la pointe orientale de l'ile Louviers au Pont-Neuf"
* "Sous les colonades du Theâtre Français, en face la petite rue du Rempart"
* "chemin de ronde de la barr. des Trois-Couronnes à celle de Ménilmontant"
* "boul. du Prince Eugène. entre la rue St-Sebastien et la rue des Amandiers"
* "aux Batignolles, sur le boulev. extér., entre les barr. Clichy et Monceaux"
* "maison de la Belle- Jardiniére, quai aux Fleurs, coin de la rue de la Cité"
* "boulevard exterieur de la barr. des Deux-Moulins, maison dité de la Jamaique"
* "en face les guichets de la galerie du Louvre, en-dessous du pont des Arts"
* "près la barr. de l'Etoile, chemin de ronde de la barrière de Neuilly"
* "R. de la Harpe, maison de l'épicier , en face la petite rue de Richelieu"
* "péristyle Beaujolais, Palais-National, en face le pass. des Pavillons"
* "rue Ambroise“ Paré (clos Saint-Lazare), près le chemin de fer du Nord"
* "route de Suresnes, a la pointe du Grand Lac, au Bois de Boulogne"
* "Boulev. et Div. du Temple, au coin de la R. Saintonge"
* "carré des Champs- Elysées (droite), pavillon Marigny"
* "à Bercy, place Cabanis, en face la barrière de Bercy"
* "au ministère des Colonies, pavillon de Flore (Tuileries)"
* "à la grille du gr. escalier du Palais du Tribunat"
* "petite rue St-Pierre- Popincourt, ruelle des Lillas"

### 2 - OpenStreetMap
* [way/225917239](https://www.openstreetmap.org/way/225917239): Tour Delphine, 6 rue Paul Langevin (Fontenay-sous-Bois)
* [way/282906977](https://www.openstreetmap.org/way/282906977):  164-35 O'Donnell Road, NY 11433
* [node/5691943406](https://www.openstreetmap.org/node/5691943406): 7165 Turakina Valley Road, Papanui Junction, Manawatū-Whanganui

### 3 - Wikidata
[Search for addresses in France via the SPARQL endpoint](https://query.wikidata.org/#SELECT%20%3Fadresse%20%3FcomLabel%20WHERE%20%7B%0A%20%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22fr%22.%20%7D%0A%20%20%3Fe%20wdt%3AP17%20wd%3AQ142.%0A%20%20%3Fe%20wdt%3AP6375%20%3Fadresse.%0A%20%20OPTIONAL%20%7B%3Fe%20wdt%3AP131%20%3Fcom%7D%0A%7D) (for other countries, change ```Q142``` to the Wikidata item for the associated country):
* "Pleine mer" (Île-d'Aix)
* "VC 4" (Sturzelbronn)
* 9, en Nexirue	(Metz)
* À côté de l'église de La Lande (Septfonds)
* à côté du passage à niveau (Saint-Chamassy)
* à l'angle de l'avenue du Maréchal-Leclerc	(Pertuis)
* à l'emplacement de l'ancien cimetière (Quéven)
* À proximité de la mairie (Luché-Pringé)
* Ancienne route du sel venant de Vintimille (Breil-sur-Roya)
* angle rue et plan de l'Aspic (Nîmes)
* au Bourguignon (Saint-Bernard)
* au Nord du bourg (Pons)
* auprès du mont Paon (Arles)
* C.I.C. 16 (Saint-Félix-de-Sorgues)
* camp de la Justice (Autun)
* chemin rural aboutissant à la D 25 (Castels)
* Chez Busset (Lugrin)
* cour du musée du Vieux Honfleur (Honfleur)
* Dans le cimetière de Lamalou-le-Poujol (Lamalou-les-Bains)
* Deux kilomètres au sud-ouest de Lassalle (Caylus)
* Domaine De Petite Anse (Bouillante)
* Hangar N° 4 Aérodrome de Vannes-Meucon 56250 MONTERBLANC (Monterblanc)
* Île de Taha'a - Zone de Patio - Îles-Sous-le Vent,98733,Tahaa (Tahaa)
* intersection RD 2144 et RD 92 (Bruère-Allichamps)
* lieu-dit Chamron (Ligny-en-Brionnais)
* Mont-de-Lans - 6 Rue des Sagnes Les Deux Alpes,38860,Les Deux Alpes (Les Deux Alpes)
* Pointe des Corbeaux (L'Île-d'Yeu)
* Pointe sud de l'île (Île-d'Aix)
* Près de la sous-préfecture (Gustavia)
* Sur la place du village (Fanlac)

### 4 - [Topographie du Vieux Paris par Adolphe Berty](https://gallica.bnf.fr/ark:/12148/bpt6k220710c)
* Maison des Images Sainct-Jehan et Saint-Denis faisant le coin occidental de la rue Jean-Saint-Denis
* Maison du Pied de Griffon [...] dont l'un formait le coin oriental de la rue du Chantre, et l'autre faisait front sur la rue de Beauvais
* situé rue du Coq, l'hôtel d'Étampes [...]

### 5 - Mérimée database (database of French monumental heritage)
* [Passerelle](https://www.pop.culture.gouv.fr/notice/merimee/IA00126986) : Grand Est ; Vosges (88) ; Brechainville ; R.D.71a
* [Tombeau de la famille Chrétien](https://www.pop.culture.gouv.fr/notice/palissy/IM88000325) : Grand Est ; Vosges (88) ; Houéville ; C.D. 27 A
* [Presbytère](https://www.pop.culture.gouv.fr/notice/merimee/IA00007311) : Bretagne ; Ille-et-Vilaine (35) ; Essé ; 100m sud-est de l'église
* [Maison](https://www.pop.culture.gouv.fr/notice/merimee/IA00002766) : Bourgogne-Franche-Comté ; Yonne (89) ; Accolay ; 2e maison rue de Reigny
* [Ferme](https://www.pop.culture.gouv.fr/notice/merimee/IA00002696) : Bourgogne-Franche-Comté ; Yonne (89) ; Prégilbert ; 1ère ferme rue des Miches
* [Maison](https://www.pop.culture.gouv.fr/notice/merimee/IA00017048) : Normandie ; Eure (27) ; Vascoeuil ; 4e maison
* [Calvaire](https://www.pop.culture.gouv.fr/notice/merimee/IA00061843) : Grand Est ; Bas-Rhin (67) ; Wintershouse ; route d'Ohlungen au nord-est du village
* [Château](https://www.pop.culture.gouv.fr/notice/merimee/IA00019815) : Normandie ; Seine-Maritime (76) ; La Vieux-Rue ; sur le C.D. 15
