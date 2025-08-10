#!/usr/bin/env python3

import json
import sys
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

def load_nypd_data(file_path = "data/nypd/data/flattened_nypd_data.json"):
    with open(file_path, 'r', encoding = 'utf-8') as f:
        return json.load(f)

def connect_to_neo4j():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j") 
    password = os.getenv("NEO4J_PASSWORD", "password")
    
    try:
        driver = GraphDatabase.driver(uri, auth = (user, password))
        driver.verify_connectivity()
        return driver
    except Exception as e:
        print(f"connection failed: {e}")
        return None

def clear_existing_data(driver):
    print("clearing existing data...")
    with driver.session() as session:
        result = session.run("MATCH (n) DETACH DELETE n")
        summary = result.consume()
        print("database cleared")

def create_incident_nodes(driver, data, limit = 50):
    print(f"creating {limit} incident nodes...")
    
    create_query = """
    UNWIND $incidents AS incident
    CREATE (i:Incident {
        cmplntNum: incident.cmplntNum,
        cmplntStartDate: incident.cmplntStartDate,
        cmplntEndDate: incident.cmplntEndDate,
        cmplntStartTime: incident.cmplntStartTime,
        cmplntEndTime: incident.cmplntEndTime,
        crimeStatus: incident.crimeStatus,
        lawCategory: incident.lawCategory,
        spatialContext: incident.spatialContext
    })
    """
    
    incidents_batch = data[:limit]
    
    with driver.session() as session:
        result = session.run(create_query, incidents = incidents_batch)
        summary = result.consume()
        print(f"created {summary.counters.nodes_created} incident nodes")

def create_location_nodes(driver, data, limit = 50):
    print("creating location nodes...")
    
    # collect unique locations from the data
    locations = {}
    for record in data[:limit]:
        if record.get('borough') and record.get('precinct'):
            key = f"{record['borough']}_{record['precinct']}"
            if key not in locations:
                locations[key] = {
                    'borough': record['borough'],
                    'precinct': record['precinct'],
                    'lonLat': record.get('lonLat', 'UNKNOWN')
                }
    
    create_query = """
    UNWIND $locations AS location
    CREATE (l:Location {
        borough: location.borough,
        precinct: location.precinct,
        lonLat: location.lonLat
    })
    """
    
    with driver.session() as session:
        result = session.run(create_query, locations = list(locations.values()))
        summary = result.consume()
        print(f"created {summary.counters.nodes_created} location nodes")

def create_offense_nodes(driver, data, limit = 50):
    print("creating offense nodes...")
    
    # collect unique offenses
    offenses = {}
    for record in data[:limit]:
        if record.get('offenseDescription'):
            key = record['offenseDescription']
            if key not in offenses:
                offenses[key] = {
                    'offenseDescription': record['offenseDescription'],
                    'offenseCode': record.get('offenseCode', 0),
                    'nypdCode': record.get('nypdCode', 'UNKNOWN')
                }
    
    create_query = """
    UNWIND $offenses AS offense
    CREATE (o:Offense {
        offenseDescription: offense.offenseDescription,
        offenseCode: offense.offenseCode,
        nypdCode: offense.nypdCode
    })
    """
    
    with driver.session() as session:
        result = session.run(create_query, offenses = list(offenses.values()))
        summary = result.consume()
        print(f"created {summary.counters.nodes_created} offense nodes")

def create_victim_nodes(driver, data, limit = 50):
    print("creating victim nodes...")
    
    create_query = """
    UNWIND $victims AS victim
    CREATE (v:Victim {
        vicId: victim.vicId,
        vicAgeGroup: victim.vicAgeGroup,
        vicRace: victim.vicRace,
        vicSex: victim.vicSex
    })
    """
    
    victims_batch = data[:limit]
    
    with driver.session() as session:
        result = session.run(create_query, victims = victims_batch)
        summary = result.consume()
        print(f"created {summary.counters.nodes_created} victim nodes")

def create_suspect_nodes(driver, data, limit = 50):
    print("creating suspect nodes...")
    
    create_query = """
    UNWIND $suspects AS suspect
    CREATE (s:Suspect {
        suspId: suspect.suspId,
        suspAgeGroup: suspect.suspAgeGroup,
        suspRace: suspect.suspRace,
        suspSex: suspect.suspSex
    })
    """
    
    suspects_batch = data[:limit]
    
    with driver.session() as session:
        result = session.run(create_query, suspects = suspects_batch)
        summary = result.consume()
        print(f"created {summary.counters.nodes_created} suspect nodes")

def create_relationships(driver, data, limit = 50):
    print("creating relationships...")
    
    # occurred_in relationships
    occurred_query = """
    UNWIND $incidents AS incident
    MATCH (i:Incident {cmplntNum: incident.cmplntNum})
    MATCH (l:Location {borough: incident.borough, precinct: incident.precinct})
    CREATE (i)-[:OCCURRED_IN]->(l)
    """
    
    # classified_as relationships  
    classified_query = """
    UNWIND $incidents AS incident
    MATCH (i:Incident {cmplntNum: incident.cmplntNum})
    MATCH (o:Offense {offenseDescription: incident.offenseDescription})
    CREATE (i)-[:CLASSIFIED_AS]->(o)
    """
    
    # involves_victim relationships
    victim_query = """
    UNWIND $incidents AS incident
    MATCH (i:Incident {cmplntNum: incident.cmplntNum})
    MATCH (v:Victim {vicId: incident.vicId})
    CREATE (i)-[:INVOLVES_VICTIM]->(v)
    """
    
    # involves_suspect relationships
    suspect_query = """
    UNWIND $incidents AS incident
    MATCH (i:Incident {cmplntNum: incident.cmplntNum})
    MATCH (s:Suspect {suspId: incident.suspId})
    CREATE (i)-[:INVOLVES_SUSPECT]->(s)
    """
    
    incidents_batch = data[:limit]
    
    with driver.session() as session:
        # create all relationship types
        result1 = session.run(occurred_query, incidents = incidents_batch)
        occurred_count = result1.consume().counters.relationships_created
        
        result2 = session.run(classified_query, incidents = incidents_batch) 
        classified_count = result2.consume().counters.relationships_created
        
        result3 = session.run(victim_query, incidents = incidents_batch)
        victim_count = result3.consume().counters.relationships_created
        
        result4 = session.run(suspect_query, incidents = incidents_batch)
        suspect_count = result4.consume().counters.relationships_created
        
        total_relationships = occurred_count + classified_count + victim_count + suspect_count
        print(f"created {total_relationships} relationships")
        print(f"  - occurred_in: {occurred_count}")
        print(f"  - classified_as: {classified_count}")  
        print(f"  - involves_victim: {victim_count}")
        print(f"  - involves_suspect: {suspect_count}")

def verify_graph(driver):
    print("\nverifying graph structure:")
    
    queries = [
        ("incidents", "MATCH (i:Incident) RETURN COUNT(i) as count"),
        ("locations", "MATCH (l:Location) RETURN COUNT(l) as count"),
        ("offenses", "MATCH (o:Offense) RETURN COUNT(o) as count"),
        ("victims", "MATCH (v:Victim) RETURN COUNT(v) as count"),
        ("suspects", "MATCH (s:Suspect) RETURN COUNT(s) as count"),
        ("relationships", "MATCH ()-[r]->() RETURN COUNT(r) as count")
    ]
    
    with driver.session() as session:
        for name, query in queries:
            result = session.run(query)
            count = result.single()["count"]
            print(f"  {name}: {count}")

def main():
    print("=== NYPD Full Graph Builder ===\n")
    
    data = load_nypd_data()
    print(f"loaded {len(data)} records")
    
    driver = connect_to_neo4j()
    if not driver:
        print("failed to connect to neo4j")
        sys.exit(1)
    
    try:
        clear_existing_data(driver)
        create_incident_nodes(driver, data, limit = 50)
        create_location_nodes(driver, data, limit = 50)
        create_offense_nodes(driver, data, limit = 50)
        create_victim_nodes(driver, data, limit = 50)
        create_suspect_nodes(driver, data, limit = 50)
        create_relationships(driver, data, limit = 50)
        verify_graph(driver)
        print("\nsuccess: full graph created with relationships")
        
    except Exception as e:
        print(f"error creating graph: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    main()