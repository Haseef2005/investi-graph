import json
import logging
from neo4j import AsyncGraphDatabase
from neo4j.exceptions import ServiceUnavailable
from app.config import settings
from litellm import acompletion
from tenacity import retry, stop_after_attempt, wait_fixed

# Logger & Driver Setup
log = logging.getLogger("uvicorn.error")

driver = AsyncGraphDatabase.driver(
    settings.NEO4J_URI, 
    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
)

# --- Connection Management ---
async def check_neo4j_connection():
    """Checks the Neo4j connection status."""
    try:
        await driver.verify_connectivity()
        log.info("Neo4j connection verified successfully.")
        return True
    except ServiceUnavailable:
        log.error("Neo4j connection failed. Check Docker container status.")
        return False
    except Exception as e:
        log.error(f"Error checking Neo4j connection: {e}")
        return False

async def close_neo4j_driver():
    """Closes the Neo4j driver connection."""
    await driver.close()
    log.info("Neo4j driver closed.")


# --- Core Logic: AI Extraction ---

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def extract_graph_from_text(text_chunk: str) -> dict:
    """
    ส่ง Text ไปให้ LLM เพื่อสกัด Nodes และ Relationships ออกมาเป็น JSON
    """
    # Prompt ที่สั่งให้ AI ทำตัวเป็น Graph Extractor
    prompt = f"""
    You are a Knowledge Graph extraction system.
    Your task is to extract meaningful "Entities" (Nodes) and "Relationships" (Edges) from the given text.

    Rules:
    1. Nodes: Identify key people, organizations, locations, concepts, or products.
    2. Relationships: Identify how these nodes are connected (e.g., "IS_CEO_OF", "LOCATED_IN", "PRODUCED_BY").
    3. Output JSON ONLY. No markdown, no explanations.

    Format:
    {{
      "nodes": [
        {{"id": "Name of Entity", "type": "PERSON/ORG/ETC"}},
        ...
      ],
      "edges": [
        {{"source": "Name of Source Node", "target": "Name of Target Node", "relation": "RELATION_NAME"}},
        ...
      ]
    }}

    TEXT TO PROCESS:
    {text_chunk}
    """

    try:
        response = await acompletion(
            model=f"{settings.LLM_PROVIDER}/llama-3.1-8b-instant",
            api_key=settings.LLM_API_KEY,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            response_format={"type": "json_object"} # บังคับ JSON (ฟีเจอร์ใหม่ของ Groq/OpenAI)
        )
        
        content = response.choices[0].message.content
        
        # Clean string (เผื่อ LLM เผลอใส่ ```json ... ``` มา)
        content = content.replace("```json", "").replace("```", "").strip()
        
        # Parse JSON
        data = json.loads(content)
        return data

    except Exception as e:
        log.error(f"Graph extraction failed: {e}")
        return {"nodes": [], "edges": []} # คืนค่าว่างถ้าพัง


# --- Core Logic: Neo4j Storage ---

async def store_graph_data(document_id: int, graph_data: dict):
    raw_nodes = graph_data.get("nodes", [])
    raw_edges = graph_data.get("edges", [])

    if not raw_nodes and not raw_edges:
        return

    # --- 🛡️ FILTERING LOGIC (กรองขยะทิ้ง) ---
    valid_nodes = []
    valid_node_ids = set()
    
    # คำต้องห้าม
    BLACKLIST_TERMS = ["us-gaap", "srt:", "nvda:", "Member", "Domain", "Table"]
    
    for node in raw_nodes:
        node_id = node.get("id", "")
        node_type = node.get("type", "")
        
        # 1. กรองพวกที่มี : หรือเป็นวันที่
        if ":" in node_id or node_type in ["DATE", "TIMEPERIOD"]:
            continue
            
        # 2. กรองคำต้องห้าม (XBRL Tags)
        if any(term in node_id for term in BLACKLIST_TERMS):
            continue
            
        # 3. กรองพวกชื่อสั้นเกินไป (ขยะ)
        if len(node_id) < 2:
            continue

        valid_nodes.append(node)
        valid_node_ids.add(node_id)

    # กรอง Edges: ต้องเชื่อมกับ Node ที่รอดชีวิตเท่านั้น
    valid_edges = []
    for edge in raw_edges:
        if edge["source"] in valid_node_ids and edge["target"] in valid_node_ids:
            valid_edges.append(edge)
    # ---------------------------------------

    # ใช้ valid_nodes / valid_edges แทนของเดิม
    nodes = valid_nodes
    edges = valid_edges

    if not nodes and not edges:
        return

    # --- 💾 STORAGE LOGIC ---
    async with driver.session() as session:
        # 1. สร้าง Nodes ก่อน
        for node in nodes:
            query = """
            MERGE (n:Entity {name: $name, doc_id: $doc_id})
            SET n.type = $type
            """
            await session.run(query, 
                name=node["id"], 
                doc_id=document_id, 
                type=node.get("type", "Unknown")
            )

        # 2. สร้าง Relationships
        for edge in edges:
            query = """
            MATCH (a:Entity {name: $source, doc_id: $doc_id})
            MATCH (b:Entity {name: $target, doc_id: $doc_id})
            MERGE (a)-[r:RELATED_TO]->(b)
            SET r.type = $relation_type
            """
            await session.run(query,
                source=edge["source"],
                target=edge["target"], 
                doc_id=document_id,
                relation_type=edge["relation"]
            )

    log.info(f"📊 Stored {len(nodes)} nodes and {len(edges)} edges for Document {document_id}")

async def get_document_graph(document_id: int) -> dict:
    """
    ดึง Nodes และ Edges ทั้งหมดของเอกสาร ID นี้ออกมาจาก Neo4j
    """
    # Cypher Query:
    # 1. หา Node ทั้งหมดที่มี doc_id นี้
    # 2. หาความสัมพันธ์ (Relationship) ที่เชื่อมกับ Node เหล่านั้น
    query = """
    MATCH (n:Entity {doc_id: $doc_id})
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN n, r, m
    """
    
    nodes_dict = {}
    edges_list = []
    
    async with driver.session() as session:
        result = await session.run(query, doc_id=document_id)
        
        async for record in result:
            # --- 1. จัดการ Node ตั้งต้น (n) ---
            node_n = record["n"]
            if node_n:
                # ใช้ชื่อ (name) เป็น ID
                n_name = node_n.get("name")
                n_type = node_n.get("type", "Unknown")
                # เก็บลง Dict เพื่อตัดตัวซ้ำอัตโนมัติ
                nodes_dict[n_name] = {
                    "id": n_name, 
                    "label": n_name, 
                    "type": n_type
                }
            
            # --- 2. จัดการ Node ปลายทาง (m) ---
            # (ต้องเช็กเพราะ OPTIONAL MATCH อาจจะหาไม่เจอ)
            node_m = record["m"]
            if node_m:
                m_name = node_m.get("name")
                m_type = node_m.get("type", "Unknown")
                nodes_dict[m_name] = {
                    "id": m_name, 
                    "label": m_name, 
                    "type": m_type
                }

            # --- 3. จัดการเส้นเชื่อม (r) ---
            rel = record["r"]
            if rel and node_n and node_m:
                # ความสัมพันธ์ใน Neo4j จะมี .type (เช่น RELATED_TO)
                # แต่เราเก็บชื่อจริงไว้ใน property ชื่อ type ด้วย (ตามโค้ดเก่า) 
                # หรือจะใช้ rel.type ของ Neo4j เลยก็ได้
                rel_type = rel.get("type", rel.type) 
                
                edges_list.append({
                    "source": node_n.get("name"),
                    "target": node_m.get("name"),
                    "relation": rel_type
                })
                
    return {
        "nodes": list(nodes_dict.values()),
        "edges": edges_list
    }

# --- GraphRAG Logic ---

async def query_graph_context(query_text: str, doc_id: int = None) -> str:
    """
    1. Extract entities from user query (using LLM).
    2. Search for these entities in Neo4j.
    3. Return their relationships as text context.
    """
    # 1. ให้ AI ช่วยหา Keywords/Entities จากคำถาม
    extraction_prompt = f"""
    Extract key entities (Company, Person, Product, Concept) from this question.
    Return ONLY a JSON list of strings.
    Example: ["NVIDIA", "Jensen Huang"]
    
    Question: {query_text}
    """
    
    try:
        response = await acompletion(
            model=f"{settings.LLM_PROVIDER}/llama-3.1-8b-instant",
            api_key=settings.LLM_API_KEY,
            messages=[{"role": "user", "content": extraction_prompt}],
            temperature=0.8,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        # บางที LLM คืนค่า key ต่างกัน กันเหนียวไว้ก่อน
        entities = data.get("entities", data.get("keywords", list(data.values())[0]))
        
        if not entities: return ""
        
        log.info(f"GraphRAG searching for entities: {entities}")

    except Exception as e:
        log.error(f"Failed to extract entities for GraphRAG: {e}")
        return ""

    # 2. ค้นหาใน Neo4j (หาเพื่อนบ้าน 1 hop)
    # ใช้ CONTAINS เพื่อให้ค้นหาแบบ case-insensitive ง่ายๆ
    cypher_query = """
    UNWIND $entities AS target_name
    MATCH (n:Entity)
    WHERE toLower(n.name) CONTAINS toLower(target_name)
    """
    
    # ถ้าระบุ doc_id มาด้วย ให้กรองเฉพาะ doc นั้น (ถ้าไม่ระบุ คือ Global Search)
    if doc_id:
        cypher_query += " AND n.doc_id = $doc_id"
        
    cypher_query += """
    MATCH (n)-[r]-(neighbor)
    RETURN n.name AS source, type(r) AS rel, neighbor.name AS target
    LIMIT 20
    """

    context_lines = []
    async with driver.session() as session:
        result = await session.run(cypher_query, entities=entities, doc_id=doc_id)
        async for record in result:
            line = f"{record['source']} --[{record['rel']}]--> {record['target']}"
            context_lines.append(line)
            
    if not context_lines:
        return ""
        
    graph_context = "Knowledge Graph Connections:\n" + "\n".join(context_lines)
    log.info(f"GraphRAG found {len(context_lines)} connections.")
    return graph_context

async def delete_document_graph(document_id: int):
    """
    ลบ Nodes และ Relationships ทั้งหมดที่เป็นของเอกสารนี้
    """
    # DETACH DELETE = ลบเส้นความสัมพันธ์ออกก่อน แล้วค่อยลบโหนด (ไม่งั้นจะลบไม่ได้ถ้ามีเส้นติดอยู่)
    query = """
    MATCH (n {doc_id: $doc_id})
    DETACH DELETE n
    """
    
    async with driver.session() as session:
        try:
            await session.run(query, doc_id=document_id)
            log.info(f"🗑️ Deleted graph nodes for Document ID: {document_id}")
        except Exception as e:
            log.error(f"❌ Failed to delete graph for Doc {document_id}: {e}")