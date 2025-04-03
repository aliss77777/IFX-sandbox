// Load game summary embeddings into Neo4j
// This script adds embeddings as vector properties to Game nodes

LOAD CSV WITH HEADERS
FROM 'file:///game_summary_embeddings.csv'
AS row
MATCH (g:Game {game_id: row.game_id})
WITH g, row, 
     [x in keys(row) WHERE x STARTS WITH 'dim_'] AS embedding_keys
WITH g, row,
     [x in embedding_keys | toFloat(row[x])] AS embedding_vector
CALL db.create.setNodeVectorProperty(g, 'summaryEmbedding', embedding_vector)
RETURN count(*) as UpdatedGames 