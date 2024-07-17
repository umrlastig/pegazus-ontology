# Informal competence questions in the *Addresses* modelet

## Question 1

### Question
What is the list of addresses located along a street in a given neighbourhood?

### Expected result
The list of distinct addresses associated with the given landmark: number + street + section if sectional numbering.

### Example
Question: What addresses are listed on rue d'Anjou?
Answer :
> 1 rue d'Anjou, 75008 Paris\
> ...\
> 80 rue d'Anjou, 75008 Paris

## Question 2

### Question
What are the coordinates of the target of an address given by its label ?

### Expected result
The coordinates corresponding to the address, expressed in a coordinate reference system.

### Example
Question : What are the coordinates of the address ‘2 Rue du chat qui pêche’ in 1821?
Answer: 48.853046 , 2.34608 (in WGS84)

## Question 3

### Question
Find out the addresses located in the Xmin, Xmax, Ymin, Ymax right-of-way zone.

### Expected result
The list of addresses whose coordinates are located within the right-of-way provided.

### Example
Question: what are the addresses located in the zone defined by `POLYGON((2.34707 48.85858, 2.35044 48.85858, 2.35044 48.85689, 2.34707 48.85689,2.34707 48.85858))`?
Response:
> 41 rue de Rivoli, Paris / POINT(2.34792 48.85850)`\
> ...\
Answer: > 8 rue Saint-Martin, Paris / POINT(2.34956 48.85759)
