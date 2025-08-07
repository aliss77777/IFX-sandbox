# Project: Huge (IFX) Soccer League AI Demo

An AI-powered sports fan assistant that creates natural language, multimodal, and personalized experiences around professional sports teams, players, games, rules, and fan communities. The app delivers conversational responses enhanced with visuals and session memory.

**Fictional League:** Huge League  
- International soccer league, 23-player squads, 4-3-3 base formation.
- Teams:
    - Yucatán Force (Mérida, Mexico): Mayan pride, fortress stadium "El Templo del Sol".
    - Tierra Alta FC (San José, Costa Rica): Highlanders, eco-friendly, smart play.
    - Everglade FC (Miami, USA): Flashy, wild, South Florida flair.
    - Fraser Valley United (Abbotsford, Canada): Vineyard roots, top youth academy.

## Standards

@standards/tech-stack.md

@standards/code-style.md

@standards/best-practices.md

## Outline

Meant as a POC this app is not very big. In order to keep things light and simple data about the teams was generated and stored in the database (Langchain InMemoryVectorStore using OpenAIEmbeddings). The scripts that built this (located in api/scripts) are:
- create_player_profiles.py
- create_game_highlights.py
- vectorstore_load.py

We also wanted to test some different technologies:
- Hugging Face Spaces: as a host. It supports gradio so we use that for a UI. This is very basic where all we do here is deploy a Docker container. That space is in `IFX-huge-league` folder.
- Langchain Workflows: for flow management. These flows live in api/workflows/ and gradio is a wrapper to run these.
- Zep: context engineering platform that systematically assembles personalized context—user preferences, traits, and business data—for reliable agent applications. Zep combines agent memory, Graph RAG, and context assembly capabilities to deliver comprehensive personalized context that reduces hallucinations and improves accuracy.
- Freeplay: LLM prompt design, test, and version control tools for system prompts. We record messages there and get our system prompts from it. This allows for testing and updates to system prompts by non-engineers.

## Deploys

This is a 3 step process:
1. `make build-prod` - build the release docker image
2. `push-prod-ghcr-rbalch` - push to github
3. `cd IFX-huge-league && make trigger-build` - trigger a deployment on hugging face spaces (for this we need no changes just a git action to trigger it to fetch the new image and deploy it)

## Scratchpad

This is a temporary file for your notes, ideas, and my intermediate outputs. It's a messy, creative space that can be cleared at any time.

@SCRATCHPAD.md