# Informal competence questions in the *Temporal evolution* modelet

## Question 1

### Question
What geographical entities of a defined type exist at a given time?

### Expected result
The list of geographical features according to the given type (street, district, etc.) with their period name.

### Example
Question: What roads existed in Paris in 1860?
Answer:<br>
> addr:LM_00534107-721b-49b6-b126-98b5fe0681a6,"rue de Rochechouart"@fr<br>
> ...<br>
> addr:LM_99c2ec65-89d1-404e-93a1-6b1cbd68ed5a,"place du Trône"@fr<br>

## Question 2

### Question
Over which time interval(s) is a given name address valid?

### Expected result
A list of time intervals giving the validity of the address.

### Example
Question: In which years can we find the address that reads ‘3 rue de la vieille place aux veaux’?<br>
Answer: the years when this address existed under the name ‘3 rue de la vieille place aux veaux’, represented in the form of one (or more) time interval(s) : `[1646-1855]`

## Question 3

### Question
What is the history of a landmark?<br>
There are two alternatives:
* (a) what events are associated with it?
* (b) what states are associated with it?

### Expected result
A list of events describing changes to the benchmark (a) or a list of ordered versions each describing the benchmark over a given time interval (b).

### Example
Question: What is the history of the Place de la Nation?<br>
Answers :<br>
(a)
> 1728 : place du Trône is created<br>
> 10 August 1792 : name change from *place du Trône* to *place du Trône Renversé*<br>
> around 1814 : name change from *place du Trône Renversé* to *place du Trône*<br>
> 2 July 1880 : name change from *place du Trône* to *place de la Nation*<br>

(b)
> * [1728,1792-08-10] : <br>
>   * name : place du Trône<br>
>   * geometry : "POLYGON(...)"<br>
>   * location : former 8th arrondissement of Paris<br>
> * ...<br>
> * [1880-07-02,...] :<br>
>   * name : place de la Nation<br>
>   * geometry : "POLYGON(...)"<br>
>   * location : 11th et 12th arrondissement of Paris

## Question 4

### Question
What states and events are missing from an address history?

### Expected result
A list of ‘phantom’ states (respectively events) and the events (respectively states) to which they are linked.
