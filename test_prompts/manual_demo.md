# Manual Demo Test Prompts

This file contains test prompts for manually verifying the Neo4j AI Agent system. Each test case includes the natural language question, expected Cypher query, and expected results based on our seed data.

## Database Schema Overview

**Nodes:**
- Person(name)
- Country(name) 
- Product(name)

**Relationships:**
- (Person)-[:LIVES_IN]->(Country)
- (Person)-[:BUYS]->(Product)

**Seed Data:**
- People: Alice, Bob, Charlie, Diana, Erik
- Countries: USA, Canada, France, Japan
- Products: Laptop, Phone, Book, Coffee

---

## Test Case 1: Single Country Query

**Natural Language:** "Who lives in France?"

**Expected Cypher:**
```cypher
MATCH (p:Person)-[:LIVES_IN]->(c:Country {name: 'France'}) RETURN p.name
```

**Expected Results:**
```
┌─────────┐
│ Name    │
├─────────┤
│ Charlie │
└─────────┘
```

**How to Test:**
```bash
python app.py "who lives in france?"
```

---

## Test Case 2: All People and Countries

**Natural Language:** "Show all people and their countries"

**Expected Cypher:**
```cypher
MATCH (p:Person)-[:LIVES_IN]->(c:Country) RETURN p.name, c.name
```

**Expected Results:**
```
┌─────────┬─────────┐
│ Country │ Name    │
├─────────┼─────────┤
│ USA     │ Alice   │
│ Canada  │ Bob     │
│ France  │ Charlie │
│ Japan   │ Diana   │
│ USA     │ Erik    │
└─────────┴─────────┘
```

**How to Test:**
```bash
python app.py "show all people and their countries"
```

---

## Test Case 3: Product Purchases

**Natural Language:** "What products does Alice buy?"

**Expected Cypher:**
```cypher
MATCH (p:Person {name: 'Alice'})-[:BUYS]->(pr:Product) RETURN pr.name
```

**Expected Results:**
```
┌─────────┐
│ Product │
├─────────┤
│ Coffee  │
│ Laptop  │
└─────────┘
```

**How to Test:**
```bash
python app.py "what products does alice buy?"
```

---

## Test Case 4: People-Product Relationships

**Natural Language:** "Show all people and what they buy"

**Expected Cypher:**
```cypher
MATCH (p:Person)-[:BUYS]->(pr:Product) RETURN p.name, pr.name
```

**Expected Results:**
```
┌─────────┬─────────┐
│ Name    │ Product │
├─────────┼─────────┤
│ Alice   │ Coffee  │
│ Alice   │ Laptop  │
│ Bob     │ Book    │
│ Bob     │ Phone   │
│ Charlie │ Coffee  │
│ Charlie │ Laptop  │
└─────────┴─────────┘
```

**How to Test:**
```bash
python app.py "show all people and what they buy"
```

---

## Test Case 5: Count Query

**Natural Language:** "How many people are there?"

**Expected Cypher:**
```cypher
MATCH (p:Person) RETURN count(p) as total_people
```

**Expected Results:**
```
┌──────────────┐
│ Total_People │
├──────────────┤
│ 5            │
└──────────────┘
```

**How to Test:**
```bash
python app.py "how many people are there?"
```

---

## Testing Notes

### Current System Configuration
- **LLM Service**: Mock mode (USE_MOCK_LLM=true) to save API credits
- **Neo4j Service**: Real mode (USE_MOCK_NEO4J=false) using live database
- **Database**: Neo4j running in Docker with complete seed data

### Expected Behavior
1. All queries should return real data from the Neo4j database
2. Results should be displayed in clean table format
3. Cypher queries should be shown prominently above results
4. System should handle edge cases gracefully

### Mock LLM Limitations
Note: With mock LLM enabled, the system may generate similar queries for different questions. For full testing with varied query generation, enable real OpenAI API:

```bash
# In .env file:
USE_MOCK_LLM=false
OPENAI_API_KEY=your_actual_api_key
```

### Troubleshooting
- Ensure Neo4j Docker container is running: `docker ps`
- Check database connection: Test direct query in Neo4j browser at http://localhost:7474
- Verify seed data loaded: `MATCH (n) RETURN count(n)` should return 13 nodes 