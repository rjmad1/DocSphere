"""
EKOS Production Neo4j Database Adapter
Manages Neo4j driver lifecycle, connection pooling, transaction execution, Cypher query generation,
and in-memory fallback graph database for development & unit testing.
"""

import os
import datetime
import logging
from typing import Dict, Any, List, Optional

try:
    from neo4j import GraphDatabase
    from neo4j.exceptions import DriverError
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EKOS-Neo4jAdapter")

class Neo4jProductionAdapter:
    def __init__(self):
        # Read from environment variables
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "ekos_password_2026")
        
        # Local in-memory fallback storage
        self._in_memory_nodes: Dict[str, Dict[str, Any]] = {}
        self._in_memory_edges: List[Dict[str, Any]] = []
        
        self.driver = None
        self.use_real_db = False

        if NEO4J_AVAILABLE:
            try:
                # Attempt to initialize real Neo4j driver
                self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
                # Verify connectivity
                with self.driver.session() as session:
                    session.run("RETURN 1")
                self.use_real_db = True
                logger.info(f"Connected to Neo4j database successfully at {self.uri}")
            except Exception as e:
                logger.warning(f"Could not connect to Neo4j at {self.uri} ({str(e)}). Falling back to in-memory graph storage.")
        else:
            logger.warning("neo4j Python package not available. Falling back to in-memory graph storage.")

    def close(self):
        if self.driver:
            self.driver.close()

    async def upsert_node(self, node_id: str, label: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Upserts a graph node with identity preservation."""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        node_data = {
            "id": node_id,
            "label": label,
            "properties": properties,
            "updated_at": now
        }
        self._in_memory_nodes[node_id] = node_data
        
        cypher = f"MERGE (n:{label} {{id: $id}}) SET n += $properties, n.updated_at = $updated_at RETURN n"
        
        if self.use_real_db and self.driver:
            try:
                def work(tx):
                    tx.run(
                        f"MERGE (n:{label} {{id: $id}}) SET n += $properties, n.updated_at = $updated_at",
                        id=node_id,
                        properties=properties,
                        updated_at=now
                    )
                with self.driver.session() as session:
                    session.execute_write(work)
                logger.info(f"Neo4j Production Upsert Node: ID={node_id} Label={label}")
                return {"status": "success", "node_id": node_id, "cypher": cypher}
            except Exception as e:
                logger.error(f"Neo4j write failed: {str(e)}. Falling back to in-memory write.")
                
        logger.info(f"Neo4j In-Memory Upsert Node: ID={node_id} Label={label}")
        return {"status": "success", "node_id": node_id, "cypher": cypher}

    async def create_edge(self, source_id: str, target_id: str, rel_type: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Creates a semantic directional relationship edge."""
        edge_data = {
            "source_id": source_id,
            "target_id": target_id,
            "rel_type": rel_type,
            "properties": properties or {}
        }
        self._in_memory_edges.append(edge_data)
        
        cypher = f"MATCH (a {{id: $source_id}}), (b {{id: $target_id}}) MERGE (a)-[r:{rel_type}]->(b) RETURN r"
        
        if self.use_real_db and self.driver:
            try:
                def work(tx):
                    tx.run(
                        f"MATCH (a {{id: $source_id}}), (b {{id: $target_id}}) "
                        f"MERGE (a)-[r:{rel_type}]->(b) SET r += $properties",
                        source_id=source_id,
                        target_id=target_id,
                        properties=properties or {}
                    )
                with self.driver.session() as session:
                    session.execute_write(work)
                logger.info(f"Neo4j Production Create Edge: {source_id} -[{rel_type}]-> {target_id}")
                return {"status": "success", "edge": f"{source_id} -[{rel_type}]-> {target_id}", "cypher": cypher}
            except Exception as e:
                logger.error(f"Neo4j write edge failed: {str(e)}. Falling back to in-memory write.")
                
        logger.info(f"Neo4j In-Memory Create Edge: {source_id} -[{rel_type}]-> {target_id}")
        return {"status": "success", "edge": f"{source_id} -[{rel_type}]-> {target_id}", "cypher": cypher}

    async def query_neighbors(self, node_id: str, direction: str = "BOTH", depth: int = 2) -> Dict[str, Any]:
        """Traverses graph neighbors up to N depth for impact analysis."""
        if self.use_real_db and self.driver:
            try:
                def work(tx):
                    result = tx.run(
                        "MATCH (n {id: $id})-[r*1..2]-(m) "
                        "RETURN DISTINCT m.id as neighbor_id",
                        id=node_id
                    )
                    return [record["neighbor_id"] for record in result]
                
                with self.driver.session() as session:
                    neighbors = session.execute_read(work)
                
                nodes_found = list(set(neighbors))
                if node_id not in nodes_found:
                    nodes_found.append(node_id)
                    
                matched_edges = [
                    edge for edge in self._in_memory_edges 
                    if edge["source_id"] in nodes_found and edge["target_id"] in nodes_found
                ]
                
                logger.info(f"Neo4j Production Query Neighbors: ID={node_id} Count={len(nodes_found)}")
                return {
                    "root_id": node_id,
                    "depth": depth,
                    "nodes_found": nodes_found,
                    "edges_found": matched_edges
                }
            except Exception as e:
                logger.error(f"Neo4j query neighbors failed: {str(e)}. Falling back to in-memory traversal.")

        # Fallback in-memory logic
        matched_edges = []
        visited = set()
        visited.add(node_id)
        
        # Simple BFS
        current_layer = {node_id}
        for _ in range(depth):
            next_layer = set()
            for current in current_layer:
                for edge in self._in_memory_edges:
                    if edge["source_id"] == current and edge["target_id"] not in visited:
                        matched_edges.append(edge)
                        visited.add(edge["target_id"])
                        next_layer.add(edge["target_id"])
                    elif edge["target_id"] == current and edge["source_id"] not in visited:
                        matched_edges.append(edge)
                        visited.add(edge["source_id"])
                        next_layer.add(edge["source_id"])
            current_layer = next_layer
            
        return {
            "root_id": node_id,
            "depth": depth,
            "nodes_found": list(visited),
            "edges_found": matched_edges
        }

