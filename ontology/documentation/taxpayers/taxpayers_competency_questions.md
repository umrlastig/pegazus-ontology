# Competency Questions for the Taxpayers Modelet

## Question 1
### Question
Who are the owners of the municipality X?
### Expected Result
List of owners whose last name starts with V
### Example of Response
*Extract from the list of owners of the municipality of Marolles-en-Brie whose last name starts with V*
#### French text
```
- Vigoureux Gabriel fabriquant de Bar à marolles
- Vigoureux, F<sup>ois</sup> vigneron à Marolles
- Vigoureux Jean Antoine militaire
```
#### English translation
```
- Vigoureux Gabriel, bar manufacturer in Marolles
- Vigoureux, F<sup>ois</sup>, winemaker in Marolles
- Vigoureux Jean Antoine, military
```
## Question 2
### Question
Who are the owners of plot X in section C of a given municipality?
### Expected Result
List of owners or usufructuaries of the plot
### Example of Response
>Owners of plot 191 in section C of Marolles en Brie
* Mazarot Pierre
* D’Auvergne
* Fleury Jn Btp
* Guillot Pierre Louis Victor
* Guillot Pierre Louis Nicolas
* Vandermassen Rémy

## Question 3
### Question
Who are the owners residing in a given municipality?
### Expected Result
List of owners identified at least once in the municipality since the creation of the cadastre.
### Example of Response
*Extract from the list of owners residing in the municipality of Marolles en Brie (idem/id refers to Marolles)*
#### English translation
```
* Huguet Louis, winemaker in Marolles
* Dubief Louis, cart driver in id
* Guérin Joseph son, winemaker in idem
* Vigoureux François, winemaker in id
* Coudrai Augte André, winemaker in id
```
#### French text
```
* Huguet Louis vigon à Marolles
* Dubief Louis Charetier à id
* Guérin Joseph fils vigon à idem
* Vigoureux François vigon à id
* Coudrai Augte André vigon à id
```
## Question 4
### Question
Who are the owners whose profession is XX in a given municipality?
### Expected Result
List of corresponding owners
### Example of Response
*Extract from the list of winemakers in the municipality of Marolles en Brie*
#### English translation
```
* Guérin Joseph son, win<sup>on</sup> in idem
* Vigoureux François, win<sup>on</sup> in id
* Coudrai Augte André, win<sup>on</sup> in id
* Guérin Joseph, father, win<sup>on</sup> in id
* Lamblet Pierre, win<sup>on</sup> in id
* Galland auguste, win<sup>on</sup> in id
* Galland Pierre, win<sup>on</sup> in Marolles
* Galland François, win<sup>on</sup> in id
* Galland Louis Nicolas, win<sup>on</sup> in id
* Mazarot Ve Pierre, win<sup>one</sup> in id
* Lefèvre Jacques, win<sup>on</sup> and deputy in id
```
#### French text
```
* Guérin Joseph fils vig<sup>on</sup> à idem
* Vigoureux François vig<sup>on</sup> à id
* Coudrai Augte André vig<sup>on</sup> à id
* Guérin Joseph, père vig<sup>on</sup> à id
* Lamblet Pierre vig<sup>on</sup> à id
* Galland auguste vig<sup>on</sup> à id
* Galland Pierre vig<sup>on</sup> à marolles
* Galland françois vig<sup>on</sup> à id
* Galland Louis nicolas vig<sup>on</sup> à id
* Mazarot Ve Pierre vig<up>one</sup> à id
* Lefèvre Jacques vig<up>on</sup> et adjoint à id
```
## Question 5
### Question
Who inherits the plots of owner X?
### Expected Result
List of all individuals who have inherited from owner X (ownership or usufruct).

<p style="color: green">The names of the heirs can be aggregated under the mention heirs XX</p>