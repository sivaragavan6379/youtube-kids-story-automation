import json
from pathlib import Path
from datetime import datetime


# ============================================================
# UNIVERSE MEMORY MANAGER
# ============================================================

MEMORY_FILE = Path(__file__).parent / "universe_memory.json"


class UniverseMemory:
    """
    Handles all reading, searching and updating of the
    shared Tamil Animated Universe memory.
    """

    def __init__(self, memory_file=MEMORY_FILE):
        self.memory_file = Path(memory_file)
        self.data = self.load()

    # --------------------------------------------------------
    # LOAD MEMORY
    # --------------------------------------------------------

    def load(self):
        """Load universe memory from JSON file."""

        if not self.memory_file.exists():
            return self.create_empty_memory()

        try:
            with open(self.memory_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            return data

        except json.JSONDecodeError:
            print("⚠️ Universe memory JSON is invalid.")
            return self.create_empty_memory()

    # --------------------------------------------------------
    # CREATE EMPTY MEMORY
    # --------------------------------------------------------

    def create_empty_memory(self):
        """Create the basic universe memory structure."""

        return {
            "universe": {
                "id": "UNIVERSE-001",
                "name": "Tamil Animated Universe",
                "description": "A connected Tamil animated story universe.",
                "current_phase": 1,
                "current_series": None,
                "current_arc": None,
                "current_episode": None
            },

            "characters": {},
            "series": {},
            "story_arcs": {},
            "episodes": {},
            "locations": {},
            "villains": {},
            "artifacts": {},
            "mysteries": {},
            "relationships": {},
            "timeline": [],
            "unresolved_threads": [],
            "foreshadowing": [],
            "major_events": []
        }

    # --------------------------------------------------------
    # SAVE MEMORY
    # --------------------------------------------------------

    def save(self):
        """Save current universe memory to JSON."""

        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.memory_file, "w", encoding="utf-8") as file:
            json.dump(
                self.data,
                file,
                indent=2,
                ensure_ascii=False
            )

        print("💾 Universe memory saved.")

    # --------------------------------------------------------
    # GENERATE ID
    # --------------------------------------------------------

    def generate_id(self, prefix, collection):
        """Generate a simple unique ID."""

        number = len(collection) + 1

        while f"{prefix}-{number:03d}" in collection:
            number += 1

        return f"{prefix}-{number:03d}"

    # ========================================================
    # CHARACTER MANAGEMENT
    # ========================================================

    def find_character(self, name):
        """
        Search for an existing character by name.

        Returns:
            character dictionary or None
        """

        name = name.strip().lower()

        for character_id, character in self.data["characters"].items():

            character_name = character.get("name", "").strip().lower()

            if character_name == name:
                return character

        return None

    def get_character(self, character_id):
        """Get character by ID."""

        return self.data["characters"].get(character_id)

    def create_character(self, character):
        """
        Create a new character automatically.

        The AI can provide the character details.
        """

        existing = self.find_character(character.get("name", ""))

        if existing:
            print(
                f"ℹ️ Character already exists: "
                f"{existing.get('name')}"
            )

            return existing

        character_id = self.generate_id(
            "CHAR",
            self.data["characters"]
        )

        character["id"] = character_id

        character.setdefault("status", "active")
        character.setdefault("first_appearance", None)
        character.setdefault("appearance", {})
        character.setdefault("personality", [])
        character.setdefault("voice", {})
        character.setdefault("abilities", [])
        character.setdefault("relationships", [])
        character.setdefault("known_locations", [])
        character.setdefault("story_history", [])
        character.setdefault("important_events", [])

        self.data["characters"][character_id] = character

        print(
            f"👤 New character created: "
            f"{character.get('name')} ({character_id})"
        )

        return character

    def update_character(self, character_id, updates):
        """Update an existing character."""

        if character_id not in self.data["characters"]:
            print(f"⚠️ Character not found: {character_id}")
            return None

        self.data["characters"][character_id].update(updates)

        print(f"🔄 Character updated: {character_id}")

        return self.data["characters"][character_id]

    # ========================================================
    # GENERIC ENTITY CREATION
    # ========================================================

    def add_entity(self, collection_name, prefix, entity):
        """
        Add an entity such as:

        series
        story_arcs
        episodes
        locations
        villains
        artifacts
        mysteries
        """

        if collection_name not in self.data:
            self.data[collection_name] = {}

        collection = self.data[collection_name]

        entity_id = self.generate_id(prefix, collection)

        entity["id"] = entity_id

        collection[entity_id] = entity

        print(
            f"➕ Added {collection_name}: "
            f"{entity_id}"
        )

        return entity

    # ========================================================
    # STORY ARC
    # ========================================================

    def create_arc(self, arc):
        """Create a new story arc."""

        return self.add_entity(
            "story_arcs",
            "ARC",
            arc
        )

    # ========================================================
    # SERIES
    # ========================================================

    def create_series(self, series):
        """Create a new series."""

        return self.add_entity(
            "series",
            "SERIES",
            series
        )

    # ========================================================
    # EPISODE
    # ========================================================

    def create_episode(self, episode):
        """Create a new episode."""

        return self.add_entity(
            "episodes",
            "EP",
            episode
        )

    # ========================================================
    # LOCATION
    # ========================================================

    def create_location(self, location):
        """Create a new location."""

        return self.add_entity(
            "locations",
            "LOC",
            location
        )

    # ========================================================
    # VILLAIN
    # ========================================================

    def create_villain(self, villain):
        """Create a new villain."""

        return self.add_entity(
            "villains",
            "VILLAIN",
            villain
        )

    # ========================================================
    # ARTIFACT
    # ========================================================

    def create_artifact(self, artifact):
        """Create a new artifact."""

        return self.add_entity(
            "artifacts",
            "ARTIFACT",
            artifact
        )

    # ========================================================
    # MYSTERY
    # ========================================================

    def create_mystery(self, mystery):
        """Create a new mystery."""

        return self.add_entity(
            "mysteries",
            "MYSTERY",
            mystery
        )

    # ========================================================
    # RELATIONSHIP
    # ========================================================

    def create_relationship(self, relationship):
        """Create relationship between characters."""

        relationship_id = self.generate_id(
            "REL",
            self.data["relationships"]
        )

        relationship["id"] = relationship_id

        self.data["relationships"][relationship_id] = relationship

        print(
            f"❤️ Relationship created: {relationship_id}"
        )

        return relationship

    # ========================================================
    # UNRESOLVED STORY THREAD
    # ========================================================

    def add_unresolved_thread(self, thread):
        """
        Store something that may become important
        in a future episode.
        """

        thread_id = self.generate_id(
            "THREAD",
            {
                item["id"]: item
                for item in self.data["unresolved_threads"]
                if "id" in item
            }
        )

        thread["id"] = thread_id
        thread.setdefault("status", "unresolved")

        self.data["unresolved_threads"].append(thread)

        print(
            f"🧩 Unresolved thread added: {thread_id}"
        )

        return thread

    # ========================================================
    # FORESHADOWING
    # ========================================================

    def add_foreshadowing(self, item):
        """
        Store clues that may become important later.
        """

        item_id = self.generate_id(
            "FORESHADOW",
            {
                entry["id"]: entry
                for entry in self.data["foreshadowing"]
                if "id" in entry
            }
        )

        item["id"] = item_id
        item.setdefault("status", "active")

        self.data["foreshadowing"].append(item)

        print(
            f"🔮 Foreshadowing added: {item_id}"
        )

        return item

    # ========================================================
    # TIMELINE
    # ========================================================

    def add_timeline_event(self, event):
        """Add an event to the universe timeline."""

        event["recorded_at"] = datetime.utcnow().isoformat()

        self.data["timeline"].append(event)

        print("🕒 Timeline event added.")

        return event

    # ========================================================
    # MAJOR EVENT
    # ========================================================

    def add_major_event(self, event):
        """Add a major universe event."""

        event["recorded_at"] = datetime.utcnow().isoformat()

        self.data["major_events"].append(event)

        print("🌟 Major universe event added.")

        return event

    # ========================================================
    # SEARCH
    # ========================================================

    def search_characters(self, keyword):
        """Search characters using a keyword."""

        keyword = keyword.lower()

        results = []

        for character in self.data["characters"].values():

            name = character.get("name", "").lower()

            personality = " ".join(
                character.get("personality", [])
            ).lower()

            if keyword in name or keyword in personality:
                results.append(character)

        return results

    # ========================================================
    # UNRESOLVED THREADS
    # ========================================================

    def get_unresolved_threads(self):
        """Return all unresolved story threads."""

        return [
            thread
            for thread in self.data["unresolved_threads"]
            if thread.get("status") == "unresolved"
        ]

    # ========================================================
    # UNIVERSE SUMMARY
    # ========================================================

    def get_summary(self):
        """
        Return a compact summary for Gemini.
        """

        return {
            "universe": self.data["universe"],

            "character_count": len(
                self.data["characters"]
            ),

            "series_count": len(
                self.data["series"]
            ),

            "arc_count": len(
                self.data["story_arcs"]
            ),

            "episode_count": len(
                self.data["episodes"]
            ),

            "location_count": len(
                self.data["locations"]
            ),

            "villain_count": len(
                self.data["villains"]
            ),

            "mystery_count": len(
                self.data["mysteries"]
            ),

            "unresolved_threads": self.get_unresolved_threads()
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n===================================")
    print("🌌 UNIVERSE MEMORY TEST")
    print("===================================\n")

    memory = UniverseMemory()

    print("Universe:")
    print(
        memory.data["universe"]["name"]
    )

    print("\nCharacters:")
    print(
        len(memory.data["characters"])
    )

    print("\nEpisodes:")
    print(
        len(memory.data["episodes"])
    )

    print("\nUnresolved Threads:")
    print(
        len(memory.get_unresolved_threads())
    )

    print("\n===================================")
    print("✅ MEMORY MANAGER WORKING")
    print("===================================\n")
