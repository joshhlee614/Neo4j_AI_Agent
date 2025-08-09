// sample cypher schema for nypd crime data
// based on schema design - 5 node types with 6 relationships

// create nodes and relationships in single transaction
CREATE (i1:Incident {
  cmplntNum: 298725583,
  cmplntStartDate: '1/1/2025',
  cmplntEndDate: '1/1/2025', 
  cmplntStartTime: '7:00:00',
  cmplntEndTime: '7:10:00',
  crimeStatus: 'COMPLETED',
  lawCategory: 'FELONY'
}),
(l1:Location {
  borough: 'MANHATTAN',
  precinct: 34,
  lonLat: 'POINT (40.7589, -73.9851)'
}),
(o1:Offense {
  offenseDescription: 'GRAND LARCENY',
  offenseCode: 126,
  nypdCode: 'PL 1551'
}),
(v1:Victim {
  vicId: 'V001',
  vicAgeGroup: '25-44',
  vicRace: 'WHITE',
  vicSex: 'M'
}),
(s1:Suspect {
  suspId: 'S001', 
  suspAgeGroup: '18-24',
  suspRace: 'BLACK',
  suspSex: 'M'
}),

// create relationships
(i1)-[:OCCURRED_IN]->(l1),
(i1)-[:CLASSIFIED_AS]->(o1),
(i1)-[:INVOLVES_VICTIM]->(v1),
(i1)-[:INVOLVES_SUSPECT]->(s1),
(v1)-[:ENCOUNTERED_SUSPECT]->(s1),
(o1)-[:REPORTED_IN]->(l1);