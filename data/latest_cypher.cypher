CREATE (a:Person {name: "Alice", age: 30, location: "San Francisco", job_title: "Software Engineer", specialization: "Machine Learning"});
CREATE (b:Person {name: "Bob", job_title: "CEO"});
CREATE (c:Person {name: "Charlie", age: 28, job_title: "Data Scientist", specialization: "Machine Learning"});
CREATE (d:Company {name: "Acme Corporation", founded: 1990, location: "Silicon Valley", industry: "Technology", employee_count: 500});
CREATE (e:Company {name: "Tech Innovations Inc", founded: 2020, industry: "Artificial Intelligence", employee_count: 50});
CREATE (a)-[:FRIENDS_WITH]->(b);
CREATE (a)-[:COLLABORATOR]->(b);
CREATE (c)-[:ACQUAINTANCE]->(a);