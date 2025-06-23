// neo4j ai agent test data
// matches schema: Person, Country, Product with LIVES_IN and BUYS relationships

// clear existing data
MATCH (n) DETACH DELETE n;

// create countries
CREATE (usa:Country {name: "USA"})
CREATE (canada:Country {name: "Canada"}) 
CREATE (france:Country {name: "France"})
CREATE (japan:Country {name: "Japan"});

// create products
CREATE (laptop:Product {name: "Laptop"})
CREATE (phone:Product {name: "Phone"})
CREATE (book:Product {name: "Book"})
CREATE (coffee:Product {name: "Coffee"});

// create people
CREATE (alice:Person {name: "Alice"})
CREATE (bob:Person {name: "Bob"})
CREATE (charlie:Person {name: "Charlie"})
CREATE (diana:Person {name: "Diana"})
CREATE (erik:Person {name: "Erik"});

// create LIVES_IN relationships
CREATE (alice)-[:LIVES_IN]->(usa)
CREATE (bob)-[:LIVES_IN]->(canada)
CREATE (charlie)-[:LIVES_IN]->(france)
CREATE (diana)-[:LIVES_IN]->(japan)
CREATE (erik)-[:LIVES_IN]->(usa);

// create BUYS relationships
CREATE (alice)-[:BUYS]->(laptop)
CREATE (alice)-[:BUYS]->(coffee)
CREATE (bob)-[:BUYS]->(phone)
CREATE (bob)-[:BUYS]->(book)
CREATE (charlie)-[:BUYS]->(laptop)
CREATE (charlie)-[:BUYS]->(coffee)
CREATE (diana)-[:BUYS]->(phone)
CREATE (diana)-[:BUYS]->(book)
CREATE (erik)-[:BUYS]->(laptop)
CREATE (erik)-[:BUYS]->(phone); 