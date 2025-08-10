#!/usr/bin/env python3

import json
import sys
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

class NodeCache:
    def __init__(self):
        self.locations = {}
        self.offenses = {}
        self.victims = {}
        self.suspects = {}
    
    def add_location(self, borough, precinct, lonlat):
        key = f"{borough}_{precinct}"
        if key not in self.locations:
            self.locations[key] = {
                'borough': borough,
                'precinct': precinct, 
                'lonLat': lonlat
            }
        return key
    
    def add_offense(self, description, code, nypd_code):
        key = description
        if key not in self.offenses:
            self.offenses[key] = {
                'offenseDescription': description,
                'offenseCode': code,
                'nypdCode': nypd_code
            }
        return key
    
    def get_stats(self):
        return {
            'locations': len(self.locations),
            'offenses': len(self.offenses)
        }

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
        print("database cleared")

def build_node_cache(data, limit = 50):
    print("building node cache for deduplication...")
    cache = NodeCache()
    
    for record in data[:limit]:
        # cache unique locations
        if record.get('borough') and record.get('precinct'):
            cache.add_location(
                record['borough'], 
                record['precinct'],
                record.get('lonLat', 'UNKNOWN')
            )
        
        # cache unique offenses
        if record.get('offenseDescription'):
            cache.add_offense(
                record['offenseDescription'],
                record.get('offenseCode', 0),
                record.get('nypdCode', 'UNKNOWN')
            )
    
    stats = cache.get_stats()
    print(f"cached {stats['locations']} unique locations")
    print(f"cached {stats['offenses']} unique offenses")
    
    return cache

def create_all_nodes(driver, data, cache, limit = 50):
    print("creating all nodes using cache...")
    
    # create incidents
    incident_query = """
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
    
    # create unique locations
    location_query = """
    UNWIND $locations AS location
    CREATE (l:Location {
        borough: location.borough,
        precinct: location.precinct,
        lonLat: location.lonLat
    })
    """
    
    # create unique offenses
    offense_query = """
    UNWIND $offenses AS offense
    CREATE (o:Offense {
        offenseDescription: offense.offenseDescription,
        offenseCode: offense.offenseCode,
        nypdCode: offense.nypdCode
    })
    """
    
    # create victims
    victim_query = """
    UNWIND $victims AS victim
    CREATE (v:Victim {
        vicId: victim.vicId,
        vicAgeGroup: victim.vicAgeGroup,
        vicRace: victim.vicRace,
        vicSex: victim.vicSex
    })
    """
    
    # create suspects
    suspect_query = """
    UNWIND $suspects AS suspect
    CREATE (s:Suspect {
        suspId: suspect.suspId,
        suspAgeGroup: suspect.suspAgeGroup,
        suspRace: suspect.suspRace,
        suspSex: suspect.suspSex
    })
    """
    
    with driver.session() as session:
        # create all node types
        session.run(incident_query, incidents = data[:limit])
        session.run(location_query, locations = list(cache.locations.values()))
        session.run(offense_query, offenses = list(cache.offenses.values()))
        session.run(victim_query, victims = data[:limit])
        session.run(suspect_query, suspects = data[:limit])
        
        print("all nodes created with deduplication")

def create_all_relationships(driver, data, limit = 50):
    print("creating relationships to shared nodes...")
    
    # all relationship queries use the cached/deduplicated nodes
    queries = [
        ("occurred_in", """
        UNWIND $incidents AS incident
        MATCH (i:Incident {cmplntNum: incident.cmplntNum})
        MATCH (l:Location {borough: incident.borough, precinct: incident.precinct})
        CREATE (i)-[:OCCURRED_IN]->(l)
        """),
        
        ("classified_as", """
        UNWIND $incidents AS incident
        MATCH (i:Incident {cmplntNum: incident.cmplntNum})
        MATCH (o:Offense {offenseDescription: incident.offenseDescription})
        CREATE (i)-[:CLASSIFIED_AS]->(o)
        """),
        
        ("involves_victim", """
        UNWIND $incidents AS incident
        MATCH (i:Incident {cmplntNum: incident.cmplntNum})
        MATCH (v:Victim {vicId: incident.vicId})
        CREATE (i)-[:INVOLVES_VICTIM]->(v)
        """),
        
        ("involves_suspect", """
        UNWIND $incidents AS incident
        MATCH (i:Incident {cmplntNum: incident.cmplntNum})
        MATCH (s:Suspect {suspId: incident.suspId})
        CREATE (i)-[:INVOLVES_SUSPECT]->(s)
        """)
    ]
    
    incidents_batch = data[:limit]
    relationship_counts = {}
    
    with driver.session() as session:
        for rel_name, query in queries:
            result = session.run(query, incidents = incidents_batch)
            count = result.consume().counters.relationships_created
            relationship_counts[rel_name] = count
    
    total = sum(relationship_counts.values())
    print(f"created {total} relationships to shared nodes")
    for rel_name, count in relationship_counts.items():
        print(f"  - {rel_name}: {count}")

def verify_deduplication(driver):
    print("\nverifying deduplication effectiveness:")
    
    queries = [
        ("total incidents", "MATCH (i:Incident) RETURN COUNT(i) as count"),
        ("unique locations", "MATCH (l:Location) RETURN COUNT(DISTINCT l) as count"), 
        ("unique offenses", "MATCH (o:Offense) RETURN COUNT(DISTINCT o) as count"),
        ("total victims", "MATCH (v:Victim) RETURN COUNT(v) as count"),
        ("total suspects", "MATCH (s:Suspect) RETURN COUNT(s) as count"),
        ("total relationships", "MATCH ()-[r]->() RETURN COUNT(r) as count")
    ]
    
    with driver.session() as session:
        for name, query in queries:
            result = session.run(query)
            count = result.single()["count"]
            print(f"  {name}: {count}")
        
        # show borough distribution to prove deduplication
        borough_result = session.run("MATCH (l:Location) RETURN l.borough, COUNT(*) as precincts ORDER BY l.borough")
        print("\nborough distribution (proves deduplication):")
        for record in borough_result:
            print(f"  {record['l.borough']}: {record['precincts']} precincts")

def main():
    print("=== NYPD Deduplicated Graph Builder ===\n")
    
    data = load_nypd_data()
    print(f"loaded {len(data)} records")
    
    driver = connect_to_neo4j()
    if not driver:
        print("failed to connect to neo4j")
        sys.exit(1)
    
    try:
        clear_existing_data(driver)
        cache = build_node_cache(data, limit = 50)
        create_all_nodes(driver, data, cache, limit = 50)
        create_all_relationships(driver, data, limit = 50)
        verify_deduplication(driver)
        print("\nsuccess: deduplicated graph created")
        
    except Exception as e:
        print(f"error creating graph: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    main()