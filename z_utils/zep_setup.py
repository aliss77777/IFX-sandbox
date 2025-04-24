# file: z_utils/zep_setup.py
"""
Create two persona users in Zep Cloud and preload their memory graphs.
Run once:  python z_utils/zep_setup.py
"""

import asyncio, os, uuid, json
from datetime import datetime, timezone
from dotenv import load_dotenv
from pathlib import Path
from zep_cloud.client import AsyncZep
from zep_cloud.errors import NotFoundError
from zep_cloud.types import User, Message

# Define the path for the UUIDs file relative to this script
UUID_FILE_PATH = Path(__file__).parent / "persona_uuids.json"
SESSION_ID_FILE_PATH = Path(__file__).parent / "persona_session_ids.json"

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env')) # Look for .env in parent dir
API_KEY = os.getenv("ZEP_API_KEY")
BASE_URL = os.getenv("ZEP_API_URL")  # optional for self-hosted

if not API_KEY:
    raise RuntimeError("ZEP_API_KEY missing in environment variables. Please ensure it's in ifx-sandbox/.env")

# Initialize AsyncZep client, handling optional base_url
zep_client_args = {"api_key": API_KEY}
if BASE_URL:
    zep_client_args["base_url"] = BASE_URL
zep = AsyncZep(**zep_client_args)

# -------- persona blue-prints -------------------------------------------------
# Removed FactRatingExamples definition as it's not part of the SDK
# FACT_EXAMPLES = FactRatingExamples(
#     high="Brock Purdy led the 49ers to the Super Bowl in 2024.",
#     medium="The 49ers play in the NFC West.",
#     low="Football games are played on a field."
# )

PERSONAS = {
    "Casual Fan": {
        "user_id": None,  # Will be generated or loaded
        "session_id": None,  # Will be generated or loaded
        "email": "casual.fan@example.com",
        "first_name": "Casual",
        "last_name": "Fan",
        "metadata": {"fan_type": "casual"}
    },
    "Super Fan": {
        "user_id": None,  # Will be generated or loaded
        "session_id": None,  # Will be generated or loaded
        "email": "super.fan@example.com",
        "first_name": "Super",
        "last_name": "Fan",
        "metadata": {"fan_type": "super"}
    }
}

# --- Message histories for each persona based on their knowledge ---

CASUAL_FAN_MESSAGES = [
    {"role": "user", "content": "Who are the 49ers?"},
    {"role": "assistant", "content": "The San Francisco 49ers are a professional football team in the NFL. They play at Levi's Stadium in Santa Clara."},
    {"role": "user", "content": "Who is their quarterback?"},
    {"role": "assistant", "content": "Brock Purdy is the current starting quarterback for the 49ers. He emerged as the starter after being the final pick in the 2022 NFL Draft, often called 'Mr. Irrelevant.'"},
    {"role": "user", "content": "Who are their best players?"},
    {"role": "assistant", "content": "The 49ers have several star players! Christian McCaffrey (often called CMC) is their key running back and an offensive weapon. George Kittle is their star tight end known for his catching and blocking abilities. On defense, Nick Bosa is a dominant defensive end who frequently pressures quarterbacks."},
    {"role": "user", "content": "Did they do well last season?"},
    {"role": "assistant", "content": "Yes! The 49ers have been very competitive recently, making several playoff runs. They've established themselves as one of the stronger teams in the NFC."},
    {"role": "user", "content": "What was their most exciting game?"},
    {"role": "assistant", "content": "While there have been several exciting games, casual fans often remember the big moments - like playoff victories and games with spectacular, highlight-reel plays. The 49ers have had many memorable comeback wins and offensive explosions that got fans on their feet!"}
]

SUPER_FAN_MESSAGES = [
    {"role": "user", "content": "Explain the 49ers' offensive scheme"},
    {"role": "assistant", "content": "The 49ers primarily run Kyle Shanahan's offensive scheme, which heavily features the outside zone run, play-action passing, and pre-snap motion. This system relies on precise timing, versatile players who can both block and catch, and a strong offensive line. Trent Williams, their All-Pro left tackle, is particularly crucial for their run game success, creating lanes for their zone running attack."},
    {"role": "user", "content": "What defensive system do they use?"},
    {"role": "assistant", "content": "Under their defensive coordinator, the 49ers utilize a scheme that emphasizes pressure from their front four, led by Nick Bosa, without excessive blitzing. This allows them to drop seven defenders into coverage while still disrupting the quarterback. Fred Warner is the key middle linebacker who orchestrates the defense, handling both run stops and pass coverage responsibilities."},
    {"role": "user", "content": "What's happening with their salary cap situation?"},
    {"role": "assistant", "content": "The 49ers' salary cap management is a constant challenge. Currently, they're navigating extensions for key players like Brandon Aiyuk while planning for Brock Purdy's future contract when he becomes eligible for an extension. They've become adept at structuring contracts to maintain their core while finding value in mid-round draft picks and undrafted free agents who fit their systems perfectly."},
    {"role": "user", "content": "What's their draft strategy been like?"},
    {"role": "assistant", "content": "Their draft strategy often focuses on finding scheme fits rather than just raw talent or conventional wisdom. They prioritize specific traits that work in their systems and aren't afraid to draft players earlier than consensus would suggest if they believe in the fit. They've been particularly good at replenishing depth on both lines and finding mid-round receivers who thrive in Shanahan's offense."},
    {"role": "user", "content": "Tell me about some of their role players beyond the stars"},
    {"role": "assistant", "content": "Beyond the stars, the 49ers get significant contributions from role players like their nickel cornerback, rotational defensive linemen who keep the pass rush fresh, and versatile offensive weapons. Players like Jauan Jennings (clutch third-down receiver), Tashaun Gipson (veteran safety presence), and Elijah Mitchell (change-of-pace running back) may not make headlines but are crucial to the team's success and highly valued by die-hard fans who understand their specific contributions."},
    {"role": "user", "content": "How does their current team compare historically?"},
    {"role": "assistant", "content": "The current 49ers team continues their tradition of innovative coaching and physical play that dates back to their dynasty years. While they haven't yet matched the Super Bowl success of the teams led by Joe Montana, Jerry Rice, and Steve Young, they've returned to being perennial contenders. The current team emphasizes a strong run game and defense, similar to their historical identity, though the specific schemes have evolved with the modern NFL."}
]

CASUAL_FAN_KNOWLEDGE = [
    {
        "type": "text",
        "data": """
        General knowledge about the San Francisco 49ers for a casual fan.
        Focuses on major stars and recent performance.
        - The 49ers play at Levi's Stadium in Santa Clara.
        - Brock Purdy is the current starting quarterback.
        - Christian McCaffrey (CMC) is a key running back and offensive weapon.
        - George Kittle is a star tight end.
        - Nick Bosa is a dominant defensive end.
        - The team has been competitive recently, often making playoff runs.
        - Big plays and game outcomes are the main interest.
        """
    }
]

SUPER_FAN_KNOWLEDGE = [
    {
        "type": "text",
        "data": """
        Detailed knowledge base for a San Francisco 49ers super fan.
        Includes strategic insights, player roles, and historical context.
        - The 49ers primarily run a Kyle Shanahan offensive scheme, heavily featuring the outside zone run, play-action passing, and pre-snap motion.
        - Key offensive line players are crucial for the run game's success (e.g., Trent Williams).
        - Defensive scheme under Steve Wilks (or current DC) utilizes a strong front four, led by Nick Bosa, aiming for pressure without excessive blitzing.
        - Fred Warner is the crucial middle linebacker, orchestrating the defense.
        - Salary cap management is a constant discussion point, especially regarding extensions for players like Brandon Aiyuk or Brock Purdy's future contract.
        - Draft strategy often focuses on finding scheme fits and replenishing depth.
        - Understanding specific player roles beyond stars (e.g., slot corner, rotational defensive linemen) is important.
        - Historical context, like past Super Bowl appearances or legendary players (Montana, Rice, Young), is frequently referenced.
        """
    },
    {
        "type": "json",
        "data": json.dumps({
            "team_focus": "49ers Strategy and Depth",
            "key_concepts": [
                "Shanahan Offense",
                "Outside Zone Scheme",
                "Defensive Line Pressure",
                "Salary Cap Implications",
                "Draft Capital Management",
                "Player Contract Negotiations"
            ],
            "recent_topics": [
                "Brandon Aiyuk contract situation",
                "Ricky Pearsall draft pick impact",
                "Defensive coordinator adjustments",
                "Offensive line performance analysis"
            ]
        })
    }
]

PERSONA_KNOWLEDGE_MAP = {
    "Casual Fan": CASUAL_FAN_KNOWLEDGE,
    "Super Fan": SUPER_FAN_KNOWLEDGE,
}

# Add mapping for persona message histories
PERSONA_MESSAGES_MAP = {
    "Casual Fan": CASUAL_FAN_MESSAGES,
    "Super Fan": SUPER_FAN_MESSAGES,
}

def load_or_generate_uuids():
    """Loads existing UUIDs from file or generates new ones if file doesn't exist."""
    uuids_changed = False
    if UUID_FILE_PATH.exists():
        try:
            with open(UUID_FILE_PATH, 'r') as f:
                saved_uuids = json.load(f)
                # Check if saved_uuids is a dict mapping names to strings
                if isinstance(saved_uuids, dict):
                    for name in PERSONAS:
                        if name in saved_uuids and isinstance(saved_uuids[name], str):
                            PERSONAS[name]["user_id"] = saved_uuids[name]
                            print(f"Loaded existing UUID for {name}: {saved_uuids[name]}")
                        else:
                            # Generate new if name missing, value isn't string, or empty
                            PERSONAS[name]["user_id"] = str(uuid.uuid4())
                            print(f"UUID for {name} not found or invalid in file, generated new: {PERSONAS[name]['user_id']}")
                            uuids_changed = True
                else:
                    # Invalid format, generate all new
                    print(f"UUID file ({UUID_FILE_PATH}) has unexpected format. Generating new UUIDs.")
                    for name in PERSONAS:
                        PERSONAS[name]["user_id"] = str(uuid.uuid4())
                        print(f"Generated new UUID for {name}: {PERSONAS[name]['user_id']}")
                    uuids_changed = True

        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading UUID file ({UUID_FILE_PATH}): {e}. Generating new UUIDs.")
            for name in PERSONAS:
                PERSONAS[name]["user_id"] = str(uuid.uuid4())
                print(f"Generated new UUID for {name}: {PERSONAS[name]['user_id']}")
            uuids_changed = True
    else:
        # File doesn't exist, generate all new UUIDs
        print(f"UUID file ({UUID_FILE_PATH}) not found. Generating new UUIDs.")
        for name in PERSONAS:
            PERSONAS[name]["user_id"] = str(uuid.uuid4())
            print(f"Generated new UUID for {name}: {PERSONAS[name]['user_id']}")
        uuids_changed = True

    if uuids_changed:
        save_persona_uuids() # Save if any UUIDs were generated or changed


def load_or_generate_session_ids():
    """Loads existing session IDs from file or generates new ones if file doesn't exist."""
    session_ids_changed = False
    
    # Use the specific session IDs from the task document for these personas
    hardcoded_session_ids = {
        "Casual Fan": "241b3478c7634492abee9f178b5341cb",
        "Super Fan": "dedcf5cb0d71475f976f4f66d98d6400"
    }
    
    if SESSION_ID_FILE_PATH.exists():
        try:
            with open(SESSION_ID_FILE_PATH, 'r') as f:
                saved_session_ids = json.load(f)
                # Check if saved_session_ids is a dict mapping names to strings
                if isinstance(saved_session_ids, dict):
                    for name in PERSONAS:
                        # Use hardcoded session IDs regardless of what's in the file
                        PERSONAS[name]["session_id"] = hardcoded_session_ids[name]
                        print(f"Using required session ID for {name}: {PERSONAS[name]['session_id']}")
                        
                        # If the saved value differs from hardcoded, we'll need to update the file
                        if name not in saved_session_ids or saved_session_ids[name] != hardcoded_session_ids[name]:
                            session_ids_changed = True
                else:
                    # Invalid format, use hardcoded IDs
                    print(f"Session ID file ({SESSION_ID_FILE_PATH}) has unexpected format. Using required session IDs.")
                    for name in PERSONAS:
                        PERSONAS[name]["session_id"] = hardcoded_session_ids[name]
                        print(f"Using required session ID for {name}: {PERSONAS[name]['session_id']}")
                    session_ids_changed = True
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading session ID file ({SESSION_ID_FILE_PATH}): {e}. Using required session IDs.")
            for name in PERSONAS:
                PERSONAS[name]["session_id"] = hardcoded_session_ids[name]
                print(f"Using required session ID for {name}: {PERSONAS[name]['session_id']}")
            session_ids_changed = True
    else:
        # File doesn't exist, use hardcoded IDs
        print(f"Session ID file ({SESSION_ID_FILE_PATH}) not found. Using required session IDs.")
        for name in PERSONAS:
            PERSONAS[name]["session_id"] = hardcoded_session_ids[name]
            print(f"Using required session ID for {name}: {PERSONAS[name]['session_id']}")
        session_ids_changed = True

    if session_ids_changed:
        save_persona_session_ids() # Save if any session IDs were updated


def save_persona_uuids():
    """Saves the current persona UUIDs (name -> user_id string) to the JSON file."""
    # Ensure we only save the user_id string
    uuids_to_save = {name: data["user_id"] for name, data in PERSONAS.items() if isinstance(data.get("user_id"), str)}
    if len(uuids_to_save) != len(PERSONAS):
        print("Warning: Not all personas had valid string UUIDs during save.")
        # Potentially raise an error or handle more robustly

    try:
        with open(UUID_FILE_PATH, 'w') as f:
            json.dump(uuids_to_save, f, indent=4)
        print(f"Persona UUIDs saved to {UUID_FILE_PATH}")
    except IOError as e:
        print(f"Error saving UUIDs to {UUID_FILE_PATH}: {e}")


def save_persona_session_ids():
    """Saves the current persona session IDs (name -> session_id string) to the JSON file."""
    # Ensure we only save the session_id string
    session_ids_to_save = {name: data["session_id"] for name, data in PERSONAS.items() if isinstance(data.get("session_id"), str)}
    if len(session_ids_to_save) != len(PERSONAS):
        print("Warning: Not all personas had valid string session IDs during save.")
        # Potentially raise an error or handle more robustly

    try:
        with open(SESSION_ID_FILE_PATH, 'w') as f:
            json.dump(session_ids_to_save, f, indent=4)
        print(f"Persona session IDs saved to {SESSION_ID_FILE_PATH}")
    except IOError as e:
        print(f"Error saving session IDs to {SESSION_ID_FILE_PATH}: {e}")


async def create_zep_user(client: AsyncZep, user_data: dict):
    """Creates or updates a Zep user, checking if they exist first."""
    user_id = user_data["user_id"]
    try:
        # Check if user exists
        await client.user.get(user_id)
        print(f"User {user_id} ({user_data.get('first_name', '')}) already exists. Updating...")
        # Update existing user (optional, could just skip)
        await client.user.update(
            user_id=user_id,
            email=user_data.get("email"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            metadata=user_data.get("metadata")
        )
        print(f"User {user_id} updated.")
    except NotFoundError:
        # User does not exist, create them
        print(f"User {user_id} ({user_data.get('first_name', '')}) not found. Creating...")
        try:
            await client.user.add(**user_data)
            print(f"User {user_id} created successfully.")
        except Exception as e:
            print(f"Error creating user {user_id}: {e}")
    except Exception as e:
        print(f"Error checking or updating user {user_id}: {e}")


async def preload_knowledge(client: AsyncZep, user_id: str, knowledge_items: list):
    """Preloads foundational knowledge into the user's graph using graph.add."""
    print(f"Preloading knowledge for user {user_id}...")
    success_count = 0
    for i, item in enumerate(knowledge_items):
        try:
            print(f"  Adding knowledge item {i+1}/{len(knowledge_items)} (type: {item['type']})...")
            await client.graph.add(
                user_id=user_id,
                type=item["type"],
                data=item["data"] # Expects string data, JSON already dumped
            )
            success_count += 1
            print(f"  Item {i+1} added successfully.")
            # Add a small delay to avoid overwhelming the API if adding many items
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"  Error adding knowledge item {i+1} for user {user_id}: {e}")
            # Decide whether to continue or stop on error
            # break # Uncomment to stop on first error
    print(f"Knowledge preloading completed for user {user_id}. {success_count}/{len(knowledge_items)} items added.")


async def preload_message_history(client: AsyncZep, user_id: str, session_id: str, messages: list):
    """Preloads message history for a user in a specific session."""
    print(f"Preloading message history for user {user_id} in session {session_id}...")
    
    try:
        # First, ensure the session exists or create it
        try:
            # Try to get the session to see if it exists
            await client.memory.get_session(session_id=session_id)
            print(f"Session {session_id} already exists.")
        except NotFoundError:
            # Session does not exist, create it
            await client.memory.add_session(
                session_id=session_id,
                user_id=user_id
            )
            print(f"Created new session {session_id} for user {user_id}")
        
        # Then add messages to the session
        zep_messages = []
        for msg in messages:
            # Map 'role' field to proper Zep role_type
            role_type = msg["role"]
            # If role is 'user', set role_type to 'user'
            # If role is 'assistant', keep role_type as 'assistant'
            
            zep_messages.append(
                Message(
                    role_type=role_type,  # Use the role directly as role_type
                    content=msg["content"],
                    role=None  # Using default role
                )
            )
        
        # Add the messages to the session
        await client.memory.add(
            session_id=session_id,
            messages=zep_messages
        )
        print(f"Added {len(zep_messages)} messages to session {session_id}")
        
    except Exception as e:
        print(f"Error preloading message history: {e}")


async def main():
    """Main function to set up Zep users and preload knowledge."""
    print("Starting Zep setup...")
    load_dotenv()

    api_key = os.environ.get("ZEP_API_KEY")
    api_url = os.environ.get("ZEP_API_URL") # Optional

    if not api_key:
        print("Error: ZEP_API_KEY environment variable not set.")
        return

    client_params = {"api_key": api_key}
    if api_url:
        client_params["api_url"] = api_url

    client = None # Initialize client variable
    try:
        # Instantiate client directly, remove async with
        client = AsyncZep(**client_params) 
        print("Zep client initialized.")

        # Load or generate UUIDs and update PERSONAS dict
        load_or_generate_uuids()
        
        # Load or use hardcoded session IDs from the task document
        load_or_generate_session_ids()

        # Create/Update users
        for persona_name, data in PERSONAS.items():
            await create_zep_user(client, data)

        # Preload knowledge for each persona
        for persona_name, data in PERSONAS.items():
            user_id = data["user_id"]
            knowledge = PERSONA_KNOWLEDGE_MAP.get(persona_name, [])
            if knowledge:
                await preload_knowledge(client, user_id, knowledge)
            else:
                print(f"No knowledge defined for persona: {persona_name}")
                
        # Preload message history for each persona
        for persona_name, data in PERSONAS.items():
            user_id = data["user_id"]
            session_id = data["session_id"]
            messages = PERSONA_MESSAGES_MAP.get(persona_name, [])
            if messages:
                await preload_message_history(client, user_id, session_id, messages)
            else:
                print(f"No message history defined for persona: {persona_name}")

    except Exception as e:
        print(f"An error occurred during Zep client initialization or operation: {e}")
    # finally:
        # Optional: Add any explicit cleanup if the client required it, 
        # but typically SDK clients manage their own connections.
        # if client and hasattr(client, 'close') and asyncio.iscoroutinefunction(client.close):
        #     await client.close()
        #     print("Zep client closed.")

    print("Zep setup finished.")


if __name__ == "__main__":
    # Ensure the script runs in an environment where asyncio is available
    # If running in a Jupyter notebook, you might need nest_asyncio
    # import nest_asyncio
    # nest_asyncio.apply()
    asyncio.run(main()) 