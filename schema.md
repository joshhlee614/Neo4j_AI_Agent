# Graph Schema

## Nodes
- Asset(community, id, type)
- Cluster(id, label)
- Country(name)
- Date(date)
- MacroIndicator(code, frequency, name, source)
- Year(year)

## Relationships
- (Cluster)-[:HAS_AVG_PRICE]->(Date)
- (Country)-[:HAS_INDICATOR]->(Year)
- (Asset)-[:HAS_PRICE]->(Date)
- (Date)-[:HAS_VALUE]->(MacroIndicator)
- (MacroIndicator)-[:HAS_VALUE]->(Date)
- (Asset)-[:SIMILAR]->(Asset) 