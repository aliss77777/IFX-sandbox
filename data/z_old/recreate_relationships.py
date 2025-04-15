import pandas as pd
import os
from graph import graph  # Using the existing graph connection
from pathlib import Path

def recreate_fan_community_relationships():
    """
    Recreates the MEMBER_OF relationships between Fans and Communities
    using the existing CSV file and graph connection
    """
    base_dir = Path(__file__).parent
    relationships_file = base_dir / "data" / "relationship_csvs" / "fan_community_rels.csv"
    communities_file = base_dir / "data" / "niners_output" / "fan_communities.csv"

    if not relationships_file.exists() or not communities_file.exists():
        print(f"Error: Could not find required CSV files")
        return False

    try:
        # First, let's check if we can find any nodes
        fan_check = graph.query("""
            MATCH (f:Fan) 
            RETURN count(f) as fan_count, 
                   collect(distinct f.fan_id)[0..5] as sample_ids
        """)
        print(f"\nFan check results: {fan_check}")

        community_check = graph.query("""
            MATCH (c:Community) 
            RETURN count(c) as community_count,
                   collect(distinct c.fan_chapter_name)[0..5] as sample_names
        """)
        print(f"\nCommunity check results: {community_check}")

        # First check a community to see its structure
        community_structure = graph.query("""
            MATCH (c:Community) 
            RETURN c LIMIT 1
        """)
        print("\nCommunity node structure:")
        print(community_structure)

        # Read both CSVs
        rels_df = pd.read_csv(relationships_file)
        communities_df = pd.read_csv(communities_file)
        
        # Create UUID to fan_chapter_name mapping
        uuid_to_name = dict(zip(communities_df['community_id'], communities_df['Fan Chapter Name']))
        
        print(f"Found {len(uuid_to_name)} community mappings")
        print("Sample mappings:")
        for uuid, name in list(uuid_to_name.items())[:3]:
            print(f"{uuid} -> {name}")

        proceed = input("\nDo you want to proceed with creating relationships? (y/n): ")
        if proceed.lower() != 'y':
            print("Aborting operation.")
            return False

        # Create relationships in batches
        batch_size = 100
        total_created = 0

        for i in range(0, len(rels_df), batch_size):
            batch = rels_df.iloc[i:i + batch_size]
            
            # Convert UUIDs to fan_chapter_names
            rows = []
            for _, row in batch.iterrows():
                community_name = uuid_to_name.get(row['end_id'])
                if community_name:
                    rows.append({
                        'fan_id': row['start_id'],
                        'chapter_name': community_name
                    })
            
            if rows:
                query = """
                UNWIND $rows AS row
                MATCH (f:Fan {fan_id: row.fan_id})
                MATCH (c:Community {fan_chapter_name: row.chapter_name})
                MERGE (f)-[:MEMBER_OF]->(c)
                RETURN count(*) as created
                """
                
                result = graph.query(query, {'rows': rows})
                total_created += len(rows)
                print(f"Progress: Created {total_created}/{len(rels_df)} relationships")

        # Verify the relationships were created
        verification_query = """
        MATCH ()-[r:MEMBER_OF]->()
        RETURN count(r) as relationship_count
        """
        result = graph.query(verification_query)
        relationship_count = result[0]['relationship_count']
        
        print(f"\nVerification: Found {relationship_count} MEMBER_OF relationships in the database")
        return True

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting to recreate Fan-Community relationships...")
    success = recreate_fan_community_relationships()
    if success:
        print("Successfully completed relationship recreation")
    else:
        print("Failed to recreate relationships") 