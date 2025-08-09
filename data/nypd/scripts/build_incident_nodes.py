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
        return summary.counters.nodes_created

def verify_count(driver):
    count_query = "MATCH (i:Incident) RETURN COUNT(i) as total"
    
    with driver.session() as session:
        result = session.run(count_query)
        count = result.single()["total"]
        print(f"total incident nodes in database: {count}")
        return count

def main():
    print("=== NYPD Incident Node Builder ===\n")
    
    data = load_nypd_data()
    print(f"loaded {len(data)} records")
    
    driver = connect_to_neo4j()
    if not driver:
        print("failed to connect to neo4j")
        sys.exit(1)
    
    try:
        created = create_incident_nodes(driver, data, limit = 50)
        if created > 0:
            verify_count(driver)
            print(f"\nsuccess: {created} incident nodes created")
        else:
            print("no nodes created")
            
    except Exception as e:
        print(f"error creating nodes: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    main()