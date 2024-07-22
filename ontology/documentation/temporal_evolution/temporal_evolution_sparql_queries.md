# SPARQL queries for *Temporal evolution* modelet

SPARQL queries describing informal competence questions

## To find out which geographical entities of a defined type exist at a given time

What roads existed in Paris in 1860? Note: `<http://www.wikidata.org/entity/Q1985727>` indicates that the calendar in which the date is written is the proleptic Gregorian calendar.

```sparql
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX addr: <http://rdf.geohistoricaldata.org/def/address#>
PREFIX ctype: <http://rdf.geohistoricaldata.org/id/codes/address/changeType/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?lm ?lmLabel ?lmType WHERE {
    VALUES (?timeStamp ?timePrecision ?timeCalendar) {
        ("1860-01-01T00:00:00"^^xsd:dateTime time:unitDay <http://www.wikidata.org/entity/Q1985727>)
    }

    ?lm a addr:Landmark ; addr:isLandmarkType ?lmType ; addr:changedBy [addr:isChangeType ctype:LandmarkAppearance ; addr:dependsOn ?evApp], [addr:isChangeType ctype:LandmarkDisappearance ; addr:dependsOn ?evDis] ; rdfs:label ?lmLabel.
    ?evApp a addr:Event ; ?pApp ?timeApp .
    ?evDis a addr:Event ; ?pDis ?timeDis .
    FILTER(?pApp IN (addr:hasTime, addr:hasLatestTimeInstant, addr:hasEarliestTimeInstant))
    FILTER(?pDis IN (addr:hasTime, addr:hasLatestTimeInstant, addr:hasEarliestTimeInstant))
    ?timeApp addr:timeStamp ?tsApp ; addr:timePrecision ?tpApp ; addr:timeCalendar ?timeCalendar .
    ?timeDis addr:timeStamp ?tsDis ; addr:timePrecision ?tpDis ; addr:timeCalendar ?timeCalendar .

    FILTER(
        ((?pApp = addr:hasTime && ?timeStamp >= ?tsApp) ||
            (?pApp = addr:hasLatestTimeInstant && ?timeStamp >= ?tsApp))
        &&
        ((?pDis = addr:hasTime && ?timeStamp <= ?tsDis) ||
            (?pDis = addr:hasEarliestTimeInstant && ?timeStamp <= ?tsDis)))
}
```

## To find out how long an address is valid under a given name

In what years can you find the address ‘50 rue Gérard’?

```sparql
```

## To obtain the history of a landmark

What events related to a change of geometry have occurred on rue Gérard?

```sparql
PREFIX addr: <http://rdf.geohistoricaldata.org/def/address#>
PREFIX ltype: <http://rdf.geohistoricaldata.org/id/codes/address/landmarkType/>
PREFIX atype: <http://rdf.geohistoricaldata.org/id/codes/address/attributeType/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT DISTINCT ?street ?change ?timeStamp ?timeStampEarliest ?timeStampLatest ?oudatedVersion ?madeEffectiveVersion WHERE {
    BIND("rue Gérard"@fr AS ?streetLabel)
    ?street a addr:Landmark ; addr:isLandmarkType ltype:Thoroughfare ; addr:hasAttribute ?attrGeom ; (rdfs:label|skos:altLabel) ?streetLabel.
    ?attrGeom a addr:Attribute ; addr:isAttributeType atype:Geometry .
    ?change addr:appliedTo ?attrGeom ; addr:dependsOn ?event.
    ?event a addr:Event.
    OPTIONAL {?event addr:hasTime [a addr:TimeInstant; addr:timeStamp ?timeStamp; addr:timePrecision ?timePrecision; addr:timeCalendar ?timeCalendar]}
    OPTIONAL {?event addr:hasEarliestTimeInstant [a addr:TimeInstant; addr:timeStamp ?timeStampEarliest; addr:timePrecision ?timePrecisionEarliest; addr:timeCalendar ?timeCalendarEarliest]}
    OPTIONAL {?event addr:hasLatestTimeInstant [a addr:TimeInstant; addr:timeStamp ?timeStampLatest; addr:timePrecision ?timePrecisionLatest; addr:timeCalendar ?timeCalendarLatest]}
    OPTIONAL {?change addr:makesEffective [addr:versionValue ?madeEffectiveVersion]}
    OPTIONAL {?change addr:outdates [addr:versionValue ?oudatedVersion]}
}
```

What is the history of the geometry of the rue Gérard? (set of geometries with their validity interval)

```sparql
PREFIX addr: <http://rdf.geohistoricaldata.org/def/address#>
PREFIX ltype: <http://rdf.geohistoricaldata.org/id/codes/address/landmarkType/>
PREFIX atype: <http://rdf.geohistoricaldata.org/id/codes/address/attributeType/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT DISTINCT ?street ?geomValue ?change ?timeStampME ?timeStampEarliestME ?timeStampLatestME ?timeStampO ?timeStampEarliestO ?timeStampLatestO WHERE {
    BIND("rue Gérard"@fr AS ?streetLabel)
    ?street a addr:Landmark ; addr:isLandmarkType ltype:Thoroughfare ; addr:hasAttribute ?attrGeom ; (rdfs:label|skos:altLabel) ?streetLabel.
    ?attrGeom a addr:Attribute ; addr:isAttributeType atype:Geometry ; addr:hasAttributeVersion ?geomVersion .
    ?geomVersion addr:versionValue ?geomValue .
    ?geomVersion addr:isMadeEffectiveBy [addr:appliedTo ?attrGeom ; addr:dependsOn ?eventME] ; addr:isOutdatedBy [addr:appliedTo ?attrGeom ; addr:dependsOn ?eventO].
    OPTIONAL {?eventME addr:hasTime [a addr:TimeInstant; addr:timeStamp ?timeStampME; addr:timePrecision ?timePrecisionME; addr:timeCalendar ?timeCalendarME]}
    OPTIONAL {?eventME addr:hasEarliestTimeInstant [a addr:TimeInstant; addr:timeStamp ?timeStampEarliestMEME; addr:timePrecision ?timePrecisionEarliestME; addr:timeCalendar ?timeCalendarEarliestME]}
    OPTIONAL {?eventME addr:hasLatestTimeInstant [a addr:TimeInstant; addr:timeStamp ?timeStampLatestME; addr:timePrecision ?timePrecisionLatestME; addr:timeCalendar ?timeCalendarLatestME]}
    OPTIONAL {?eventO addr:hasTime [a addr:TimeInstant; addr:timeStamp ?timeStampO; addr:timePrecision ?timePrecisionO; addr:timeCalendar ?timeCalendarO]}
OPTIONAL {?eventO addr:hasEarliestTimeInstant [a addr:TimeInstant; addr:timeStamp ?timeStampEarliestOO; addr:timePrecision ?timePrecisionEarliestO; addr:timeCalendar ?timeCalendarEarliestO]}
OPTIONAL {?eventO addr:hasLatestTimeInstant [a addr:TimeInstant; addr:timeStamp ?timeStampLatestO; addr:timePrecision ?timePrecisionLatestO; addr:timeCalendar ?timeCalendarLatestO]}
}
```
