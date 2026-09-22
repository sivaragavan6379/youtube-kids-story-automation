import json
import re
from pathlib import Path


# ============================================================
# UNIVERSE MEMORY MANAGER
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MEMORY_FILE = BASE_DIR / "universe" / "universe_memory.json"
ARC_FILE = BASE_DIR / "output" / "generated_arc.json"


class UniverseMemoryManager:

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):
        self.memory = self.load_json(MEMORY_FILE)
        self.arc_data = self.load_json(ARC_FILE)
        self.arc = self.arc_data.get("arc", {})

        if not isinstance(self.arc, dict):
            self.arc = {}

        self.prepare_memory_structure()

    # ========================================================
    # LOAD JSON
    # ========================================================

    def load_json(self, file_path):
        if not file_path.exists():
            raise FileNotFoundError(
                f"File not found:\n{file_path}"
            )

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)

        except json.JSONDecodeError as error:
            raise RuntimeError(
                f"Invalid JSON file:\n{file_path}\n\n{error}"
            ) from error

    # ========================================================
    # SAVE JSON
    # ========================================================

    def save_memory(self):
        MEMORY_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                self.memory,
                file,
                ensure_ascii=False,
                indent=2
            )

        print()
        print("💾 Universe memory saved:")
        print(MEMORY_FILE)

    # ========================================================
    # PREPARE MEMORY STRUCTURE
    # ========================================================

    def prepare_memory_structure(self):

        if not isinstance(self.memory.get("universe"), dict):
            self.memory["universe"] = {}

        universe = self.memory["universe"]

        universe.setdefault("id", "UNIVERSE-001")
        universe.setdefault("name", "Tamil Animated Universe")
        universe.setdefault(
            "description",
            "A connected Tamil animated story universe."
        )
        universe.setdefault("current_phase", 1)
        universe.setdefault("current_series", None)
        universe.setdefault("current_arc", None)
        universe.setdefault("current_episode", None)

        dictionary_collections = [
            "characters",
            "series",
            "story_arcs",
            "episodes",
            "locations",
            "villains",
            "artifacts",
            "mysteries",
            "relationships"
        ]

        for collection in dictionary_collections:
            value = self.memory.get(collection)

            if value is None:
                self.memory[collection] = {}

            elif not isinstance(value, dict):
                print(
                    f"⚠️ Converting {collection} to dictionary."
                )
                self.memory[collection] = {}

        list_collections = [
            "timeline",
            "unresolved_threads",
            "foreshadowing",
            "major_events"
        ]

        for collection in list_collections:
            value = self.memory.get(collection)

            if value is None:
                self.memory[collection] = []

            elif not isinstance(value, list):
                print(
                    f"⚠️ Converting {collection} to list."
                )
                self.memory[collection] = []

    # ========================================================
    # SAFE ID
    # ========================================================

    def make_id(self, text):
        text = str(text or "").strip().lower()

        text = re.sub(
            r"[^a-z0-9]+",
            "_",
            text
        )

        text = re.sub(
            r"_+",
            "_",
            text
        )

        text = text.strip("_")

        return text or "unknown"

    # ========================================================
    # UNIQUE ID
    # ========================================================

    def unique_id(self, collection, base_id):
        collection_data = self.memory.get(
            collection,
            {}
        )

        if base_id not in collection_data:
            return base_id

        counter = 2

        while True:
            candidate = f"{base_id}_{counter}"

            if candidate not in collection_data:
                return candidate

            counter += 1

    # ========================================================
    # FIND BY NAME
    # ========================================================

    def find_by_name(self, collection, name):
        target = self.make_id(name)

        data = self.memory.get(
            collection,
            {}
        )

        if not isinstance(data, dict):
            return None

        if target in data:
            return data[target]

        for item in data.values():

            if not isinstance(item, dict):
                continue

            stored_name = self.make_id(
                item.get("name", "")
            )

            if stored_name == target:
                return item

        return None

    # ========================================================
    # ADD DICTIONARY ITEM
    # ========================================================

    def add_dictionary_item(
        self,
        collection,
        item,
        preferred_id=None
    ):
        if not isinstance(item, dict):
            return None

        name = item.get("name")

        if not name:
            return None

        existing = self.find_by_name(
            collection,
            name
        )

        if existing:
            print(
                f"🔁 Existing {collection[:-1]} preserved: "
                f"{name}"
            )

            for key, value in item.items():
                if key not in existing:
                    existing[key] = value

            return existing

        base_id = (
            preferred_id
            or self.make_id(name)
        )

        item_id = self.unique_id(
            collection,
            base_id
        )

        item_copy = dict(item)
        item_copy.setdefault("id", item_id)

        self.memory[collection][item_id] = item_copy

        print(
            f"🆕 Added {collection[:-1]}: {name}"
        )

        return item_copy

    # ========================================================
    # ADD CHARACTER
    # ========================================================

    def add_character(self, character):
        """Add a new character without overwriting established continuity."""
        if not isinstance(character, dict):
            return None

        name = str(character.get("name", "")).strip()
        if not name:
            return None

        existing = self.find_by_name("characters", name)
        current_arc = self.arc.get("title")

        if existing:
            print(f"🔁 Returning character detected: {name}")
            history = existing.setdefault("arc_history", [])
            if current_arc and current_arc not in history:
                history.append(current_arc)

            existing["appearance_type"] = "returning"
            existing["status"] = "active"
            existing["last_arc"] = current_arc

            for key, value in character.items():
                if key in {"id", "first_arc", "last_arc", "arc_history", "appearance_type"}:
                    continue
                if key not in existing:
                    existing[key] = value

            existing.setdefault("return_history", [])
            existing.setdefault("appearance_history", [])
            return existing

        character_copy = dict(character)
        character_id = self.unique_id("characters", self.make_id(name))
        character_copy["id"] = character_id
        character_copy.setdefault("status", "active")
        character_copy["appearance_type"] = "new"
        character_copy["first_arc"] = current_arc
        character_copy["last_arc"] = current_arc
        history = character_copy.setdefault("arc_history", [])
        if current_arc and current_arc not in history:
            history.append(current_arc)
        character_copy.setdefault("return_history", [])
        character_copy.setdefault("appearance_history", [])

        self.memory["characters"][character_id] = character_copy
        print(f"🆕 New character added: {name}")
        return character_copy

    # ========================================================
    # RECORD RETURNING CHARACTER
    # ========================================================

    def record_returning_character(self, returning_character):
        """Persist why and how an existing character returns in this arc."""
        if not isinstance(returning_character, dict):
            return None

        name = str(returning_character.get("name", "")).strip()
        if not name:
            return None

        existing = self.find_by_name("characters", name)
        current_arc = self.arc.get("title")

        if not existing:
            print(
                f"⚠️ Returning character '{name}' does not exist in universe memory."
            )
            return None

        history = existing.setdefault("arc_history", [])
        if current_arc and current_arc not in history:
            history.append(current_arc)

        existing["appearance_type"] = "returning"
        existing["status"] = "active"
        existing["last_arc"] = current_arc
        existing.setdefault("return_history", [])
        existing.setdefault("appearance_history", [])

        record = {
            "arc": current_arc,
            "reason_for_return": str(returning_character.get("reason_for_return", "")).strip(),
            "role_in_arc": str(returning_character.get("role_in_arc", "")).strip(),
            "continuity_connection": str(returning_character.get("continuity_connection", "")).strip(),
        }

        duplicate = any(
            isinstance(old, dict)
            and old.get("arc") == record["arc"]
            and old.get("reason_for_return") == record["reason_for_return"]
            and old.get("role_in_arc") == record["role_in_arc"]
            for old in existing["return_history"]
        )
        if not duplicate:
            existing["return_history"].append(record)

        appearance = {
            "arc": current_arc,
            "type": "returning",
            "role": record["role_in_arc"],
        }
        if appearance not in existing["appearance_history"]:
            existing["appearance_history"].append(appearance)

        print(f"↩️ Returning character recorded: {name}")
        if record["reason_for_return"]:
            print(f"   Reason: {record['reason_for_return']}")
        if record["role_in_arc"]:
            print(f"   Role: {record['role_in_arc']}")
        return existing

    # ========================================================
    # PROCESS CHARACTERS
    # ========================================================

    def process_characters(self):
        current_arc = self.arc.get("title")

        # 1. New characters
        new_characters = self.arc.get("new_characters", [])
        if isinstance(new_characters, list):
            for character in new_characters:
                self.add_character(character)

        # 2. Explicit returning characters
        returning_characters = self.arc.get("returning_characters", [])
        if isinstance(returning_characters, list):
            for character in returning_characters:
                self.record_returning_character(character)

        # 3. Main characters
        main_characters = self.arc.get("main_characters", [])
        if isinstance(main_characters, list):
            for name in main_characters:
                self._record_simple_character_appearance(
                    name, "main", "main_character", current_arc
                )

        # 4. Supporting characters
        supporting_characters = self.arc.get("supporting_characters", [])
        if isinstance(supporting_characters, list):
            for name in supporting_characters:
                self._record_simple_character_appearance(
                    name, "supporting", "supporting_character", current_arc
                )

    def _record_simple_character_appearance(
        self,
        name,
        appearance_type,
        role,
        current_arc
    ):
        """Record main/supporting appearances without inventing missing characters."""
        if not isinstance(name, str):
            return None

        name = name.strip()
        if not name:
            return None

        existing = self.find_by_name("characters", name)
        if not existing:
            print(
                f"⚠️ Character '{name}' is listed as {appearance_type} "
                f"but does not exist in memory."
            )
            return None

        history = existing.setdefault("arc_history", [])
        if current_arc and current_arc not in history:
            history.append(current_arc)

        existing["appearance_type"] = "returning"
        existing["status"] = "active"
        existing["last_arc"] = current_arc
        existing.setdefault("appearance_history", [])

        appearance = {
            "arc": current_arc,
            "type": appearance_type,
            "role": role,
        }
        if appearance not in existing["appearance_history"]:
            existing["appearance_history"].append(appearance)

        print(f"↩️ {appearance_type.title()} character: {name}")
        return existing

    # ========================================================
    # ADD STORY ARC
    # ========================================================

    def add_story_arc(self):

        title = self.arc.get("title")

        if not title:
            raise RuntimeError(
                "Generated ARC does not contain a title."
            )

        existing = self.find_by_name(
            "story_arcs",
            title
        )

        if existing:

            print(
                f"🔁 Story arc already exists: {title}"
            )

            self.memory["universe"]["current_arc"] = (
                existing.get("id")
            )

            return existing

        arc_number = (
            len(self.memory["story_arcs"]) + 1
        )

        arc_id = f"arc_{arc_number:03d}"

        arc_copy = dict(self.arc)
        arc_copy["id"] = arc_id
        arc_copy["arc_number"] = arc_number

        self.memory["story_arcs"][arc_id] = arc_copy

        self.memory["universe"]["current_arc"] = arc_id

        print()
        print(
            f"📚 Story Arc {arc_number} added:"
        )
        print(title)

        return arc_copy

    # ========================================================
    # ADD EPISODES
    # ========================================================

    def add_episodes(self, arc_record):

        episodes = self.arc.get("episodes", [])

        if not isinstance(episodes, list):
            return

        arc_id = arc_record.get("id")
        arc_number = arc_record.get("arc_number", 1)

        allowed_statuses = {
            "planned",
            "scripted",
            "generated",
            "completed",
            "published"
        }

        for index, episode in enumerate(
            episodes,
            start=1
        ):

            if not isinstance(episode, dict):
                continue

            episode_number = episode.get(
                "episode_number",
                index
            )

            try:
                episode_number = int(episode_number)
            except (TypeError, ValueError):
                episode_number = index

            title = episode.get(
                "title",
                f"Episode {episode_number}"
            )

            episode_id = (
                f"{arc_id}_ep_{episode_number:02d}"
            )

            status = str(
                episode.get(
                    "status",
                    "planned"
                )
            ).strip().lower()

            if status not in allowed_statuses:
                status = "planned"

            episode_copy = dict(episode)

            episode_copy["id"] = episode_id
            episode_copy["arc_id"] = arc_id
            episode_copy["arc_number"] = arc_number
            episode_copy["episode_number"] = episode_number
            episode_copy["status"] = status

            existing = self.memory["episodes"].get(
                episode_id
            )

            if existing:

                # Preserve existing generated/published state.
                old_status = existing.get(
                    "status",
                    "planned"
                )

                priority = {
                    "planned": 0,
                    "scripted": 1,
                    "generated": 2,
                    "completed": 3,
                    "published": 4
                }

                if priority.get(
                    old_status,
                    0
                ) > priority.get(
                    status,
                    0
                ):
                    status = old_status

                existing.update({
                    "title": title,
                    "arc_id": arc_id,
                    "arc_number": arc_number,
                    "episode_number": episode_number,
                    "status": status
                })

                for key, value in episode_copy.items():
                    if key not in existing:
                        existing[key] = value

                print(
                    f"🔄 Episode updated: "
                    f"{episode_id} → {status}"
                )

                continue

            self.memory["episodes"][episode_id] = episode_copy

            print(
                f"🎬 Episode added: "
                f"EP {episode_number} - {title} "
                f"[{status}]"
            )

    # ========================================================
    # PROCESS LOCATIONS
    # ========================================================

    def process_locations(self):

        locations = self.arc.get(
            "locations",
            []
        )

        if not isinstance(locations, list):
            return

        for location in locations:
            self.add_dictionary_item(
                "locations",
                location
            )

    # ========================================================
    # PROCESS ARTIFACTS
    # ========================================================

    def process_artifacts(self):

        artifacts = self.arc.get(
            "artifacts",
            []
        )

        if not isinstance(artifacts, list):
            return

        for artifact in artifacts:
            self.add_dictionary_item(
                "artifacts",
                artifact
            )

    # ========================================================
    # PROCESS VILLAINS
    # ========================================================

    def process_villains(self):

        villains = self.arc.get(
            "villains",
            []
        )

        if not isinstance(villains, list):
            return

        for villain in villains:
            self.add_dictionary_item(
                "villains",
                villain
            )

    # ========================================================
    # NORMALIZE MYSTERY STATUS
    # ========================================================

    def normalize_mystery_status(self, status):

        if not status:
            return "active"

        status_text = str(
            status
        ).strip().lower()

        # Check partial before generic words such as "resolved".
        if any(
            phrase in status_text
            for phrase in [
                "partially solved",
                "partially revealed",
                "partially understood",
                "mostly revealed",
                "partially resolved"
            ]
        ):
            return "partially_revealed"

        if any(
            word in status_text
            for word in [
                "resolved",
                "solved",
                "complete",
                "completed",
                "ended",
                "vanquished"
            ]
        ):
            return "resolved"

        if any(
            word in status_text
            for word in [
                "ongoing",
                "active",
                "unsolved",
                "unresolved",
                "unknown",
                "introduced"
            ]
        ):
            return "active"

        return "active"

    # ========================================================
    # REMOVE UNRESOLVED THREAD
    # ========================================================

    def remove_unresolved_thread(self, mystery_name):

        normalized_name = self.make_id(
            mystery_name
        )

        remaining_threads = []

        for thread in self.memory[
            "unresolved_threads"
        ]:

            if not isinstance(thread, dict):
                remaining_threads.append(thread)
                continue

            thread_name = self.make_id(
                thread.get("name", "")
            )

            if thread_name == normalized_name:
                print(
                    f"✅ Removed resolved thread: "
                    f"{mystery_name}"
                )
                continue

            remaining_threads.append(thread)

        self.memory[
            "unresolved_threads"
        ] = remaining_threads

    # ========================================================
    # PROCESS MYSTERIES
    # ========================================================

    def process_mysteries(self):

        mysteries = self.arc.get(
            "mysteries",
            []
        )

        if not isinstance(mysteries, list):
            mysteries = []

        for mystery in mysteries:

            if not isinstance(mystery, dict):
                continue

            name = mystery.get("name")

            if not name:
                continue

            status = self.normalize_mystery_status(
                mystery.get("status")
            )

            existing = self.find_by_name(
                "mysteries",
                name
            )

            current_arc = self.arc.get(
                "title"
            )

            if existing:

                existing["status"] = status
                existing["last_arc"] = current_arc

                history = existing.setdefault(
                    "arc_history",
                    []
                )

                if (
                    current_arc
                    and current_arc not in history
                ):
                    history.append(current_arc)

                for key, value in mystery.items():
                    if key not in existing:
                        existing[key] = value

                print(
                    f"🔄 Mystery updated: "
                    f"{name} → {status}"
                )

            else:

                mystery_copy = dict(mystery)

                mystery_id = self.unique_id(
                    "mysteries",
                    self.make_id(name)
                )

                mystery_copy["id"] = mystery_id
                mystery_copy["status"] = status
                mystery_copy["first_arc"] = current_arc
                mystery_copy["last_arc"] = current_arc
                mystery_copy["arc_history"] = []

                if current_arc:
                    mystery_copy["arc_history"].append(
                        current_arc
                    )

                self.memory[
                    "mysteries"
                ][mystery_id] = mystery_copy

                print(
                    f"🆕 Mystery added: "
                    f"{name} → {status}"
                )

            if status == "resolved":

                self.remove_unresolved_thread(
                    name
                )

            else:

                self.add_unresolved_thread(
                    {
                        "name": name,
                        "description": mystery.get(
                            "description",
                            ""
                        ),
                        "type": "mystery",
                        "status": status,
                        "arc": current_arc
                    }
                )

        # ----------------------------------------------------
        # CENTRAL MYSTERIES
        # ----------------------------------------------------

        central_mysteries = self.arc.get(
            "central_mysteries",
            []
        )

        if not isinstance(
            central_mysteries,
            list
        ):
            return

        for mystery in central_mysteries:

            if isinstance(mystery, dict):

                name = mystery.get("name")

                status = self.normalize_mystery_status(
                    mystery.get(
                        "status",
                        "active"
                    )
                )

            else:

                name = str(mystery)
                status = "active"

            if not name:
                continue

            if status == "resolved":

                self.remove_unresolved_thread(
                    name
                )

            else:

                self.add_unresolved_thread(
                    {
                        "name": name,
                        "type": "central_mystery",
                        "arc": self.arc.get(
                            "title"
                        ),
                        "status": status
                    }
                )

    # ========================================================
    # PROCESS RELATIONSHIPS
    # ========================================================

    def process_relationships(self):

        relationships = self.arc.get(
            "relationships",
            []
        )

        if not isinstance(
            relationships,
            list
        ):
            return

        for relationship in relationships:

            if not isinstance(
                relationship,
                dict
            ):
                continue

            source = relationship.get(
                "source",
                "unknown"
            )

            target = relationship.get(
                "target",
                "unknown"
            )

            relation = relationship.get(
                "relationship",
                "connected"
            )

            relationship_id = self.make_id(
                f"{source}_{relation}_{target}"
            )

            # Reuse an existing relationship instead
            # of creating a new duplicate every run.

            already_exists = False

            for existing in self.memory[
                "relationships"
            ].values():

                if not isinstance(
                    existing,
                    dict
                ):
                    continue

                if (
                    self.make_id(
                        existing.get("source")
                    )
                    == self.make_id(source)
                    and
                    self.make_id(
                        existing.get("target")
                    )
                    == self.make_id(target)
                    and
                    self.make_id(
                        existing.get("relationship")
                    )
                    == self.make_id(relation)
                ):
                    already_exists = True
                    break

            if already_exists:
                continue

            relationship_id = self.unique_id(
                "relationships",
                relationship_id
            )

            relationship_copy = dict(
                relationship
            )

            relationship_copy["id"] = (
                relationship_id
            )

            self.memory[
                "relationships"
            ][relationship_id] = (
                relationship_copy
            )

            print(
                f"🔗 Relationship added: "
                f"{source} → {target}"
            )

    # ========================================================
    # ADD / UPDATE UNRESOLVED THREAD
    # ========================================================

    def add_unresolved_thread(
        self,
        thread
    ):

        if isinstance(thread, dict):

            name = thread.get(
                "name",
                "Unknown Thread"
            )

            thread_copy = dict(thread)

        else:

            name = str(thread)

            thread_copy = {
                "name": name
            }

        normalized_name = self.make_id(
            name
        )

        status = self.normalize_mystery_status(
            thread_copy.get("status")
        )

        thread_copy["status"] = status

        # ----------------------------------------------------
        # Existing thread
        # ----------------------------------------------------

        for existing in self.memory[
            "unresolved_threads"
        ]:

            if not isinstance(
                existing,
                dict
            ):
                continue

            existing_name = self.make_id(
                existing.get(
                    "name",
                    ""
                )
            )

            if existing_name != normalized_name:
                continue

            existing["status"] = status
            existing["last_arc"] = self.arc.get(
                "title"
            )

            if thread_copy.get("description"):
                existing["description"] = (
                    thread_copy["description"]
                )

            if status == "resolved":
                self.remove_unresolved_thread(
                    name
                )

            return

        # Resolved mysteries do not belong in
        # unresolved_threads.

        if status == "resolved":
            return

        thread_copy.setdefault(
            "arc",
            self.arc.get("title")
        )

        self.memory[
            "unresolved_threads"
        ].append(thread_copy)

        print(
            f"❓ Unresolved thread added: "
            f"{name} → {status}"
        )

    # ========================================================
    # PROCESS FORESHADOWING
    # ========================================================

    def process_foreshadowing(self):

        clues = self.arc.get(
            "foreshadowing",
            []
        )

        if not isinstance(clues, list):
            return

        for clue in clues:

            if not isinstance(clue, dict):
                continue

            event = dict(clue)
            event["arc"] = self.arc.get(
                "title"
            )

            self.memory[
                "foreshadowing"
            ].append(event)

            print(
                "🔮 Foreshadowing saved."
            )

    # ========================================================
    # PROCESS MAJOR EVENTS
    # ========================================================

    def process_major_events(self):

        events = self.arc.get(
            "major_events",
            []
        )

        if not isinstance(events, list):
            return

        for event in events:

            event_record = {
                "arc": self.arc.get("title"),
                "event": event
            }

            self.memory[
                "major_events"
            ].append(event_record)

            self.memory[
                "timeline"
            ].append(
                {
                    "type": "major_event",
                    "arc": self.arc.get("title"),
                    "event": event
                }
            )

            print(
                f"📜 Major event saved: {event}"
            )

    # ========================================================
    # PROCESS ARC CONSEQUENCES
    # ========================================================

    def process_consequences(self):

        consequences = self.arc.get(
            "arc_consequences",
            []
        )

        if not isinstance(
            consequences,
            list
        ):
            return

        for consequence in consequences:

            self.memory[
                "timeline"
            ].append(
                {
                    "type": "arc_consequence",
                    "arc": self.arc.get("title"),
                    "event": consequence
                }
            )

    # ========================================================
    # PROCESS FUTURE ARC HOOK
    # ========================================================

    def process_future_hook(self):

        future_hook = self.arc.get(
            "future_arc_hook"
        )

        if not future_hook:
            return

        self.add_unresolved_thread(
            {
                "name": "Future Arc Hook",
                "description": future_hook,
                "type": "future_arc_hook",
                "status": "active",
                "arc": self.arc.get("title")
            }
        )

        self.memory[
            "foreshadowing"
        ].append(
            {
                "type": "future_arc_hook",
                "arc": self.arc.get("title"),
                "description": future_hook
            }
        )

    # ========================================================
    # UPDATE UNIVERSE STATE
    # ========================================================

    def update_universe_state(
        self,
        arc_record
    ):

        universe = self.memory["universe"]

        universe["current_arc"] = (
            arc_record.get("id")
        )

        universe["current_series"] = (
            self.arc.get(
                "series",
                universe.get("current_series")
            )
        )

        episodes = self.arc.get(
            "episodes",
            []
        )

        completed_statuses = {
            "generated",
            "completed",
            "published"
        }

        completed_episodes = []

        if isinstance(
            episodes,
            list
        ):

            for episode in episodes:

                if not isinstance(
                    episode,
                    dict
                ):
                    continue

                status = str(
                    episode.get(
                        "status",
                        "planned"
                    )
                ).strip().lower()

                if status in completed_statuses:
                    completed_episodes.append(
                        episode
                    )

        if completed_episodes:

            last_episode = completed_episodes[-1]

            universe["current_episode"] = (
                last_episode.get(
                    "episode_number"
                )
            )

        else:

            universe["current_episode"] = None

        universe["current_phase"] = universe.get(
            "current_phase",
            1
        )

    # ========================================================
    # PROCESS COMPLETE ARC
    # ========================================================

    def process_arc(self):

        if not self.arc:
            raise RuntimeError(
                "generated_arc.json contains "
                "no 'arc' object."
            )

        title = self.arc.get(
            "title",
            "Untitled Arc"
        )

        print()
        print("=" * 44)
        print("🧠 MEMORY MANAGER")
        print("=" * 44)
        print()

        print("📖 Processing ARC:")
        print(f"   {title}")
        print()

        # 1. Story Arc
        arc_record = self.add_story_arc()

        # 2. Characters
        self.process_characters()

        # 3. Locations
        self.process_locations()

        # 4. Artifacts
        self.process_artifacts()

        # 5. Villains
        self.process_villains()

        # 6. Mysteries
        self.process_mysteries()

        # 7. Relationships
        self.process_relationships()

        # 8. Episodes
        self.add_episodes(
            arc_record
        )

        # 9. Foreshadowing
        self.process_foreshadowing()

        # 10. Major events
        self.process_major_events()

        # 11. Consequences
        self.process_consequences()

        # 12. Future hook
        self.process_future_hook()

        # 13. Universe state
        self.update_universe_state(
            arc_record
        )

        print()
        print("=" * 44)
        print("✅ ARC MEMORY UPDATE COMPLETE")
        print("=" * 44)

    # ========================================================
    # SUMMARY
    # ========================================================

    def print_summary(self):

        print()
        print("=" * 44)
        print("📊 UNIVERSE MEMORY SUMMARY")
        print("=" * 44)
        print()

        print(
            "Characters: "
            f"{len(self.memory['characters'])}"
        )

        print(
            "Story Arcs: "
            f"{len(self.memory['story_arcs'])}"
        )

        print(
            "Episodes: "
            f"{len(self.memory['episodes'])}"
        )

        print(
            "Locations: "
            f"{len(self.memory['locations'])}"
        )

        print(
            "Villains: "
            f"{len(self.memory['villains'])}"
        )

        print(
            "Artifacts: "
            f"{len(self.memory['artifacts'])}"
        )

        print(
            "Mysteries: "
            f"{len(self.memory['mysteries'])}"
        )

        print(
            "Relationships: "
            f"{len(self.memory['relationships'])}"
        )

        print(
            "Timeline events: "
            f"{len(self.memory['timeline'])}"
        )

        print(
            "Unresolved threads: "
            f"{len(self.memory['unresolved_threads'])}"
        )

        print(
            "Foreshadowing clues: "
            f"{len(self.memory['foreshadowing'])}"
        )

        print(
            "Major events: "
            f"{len(self.memory['major_events'])}"
        )

        print()
        print("=" * 44)


# ============================================================
# MAIN
# ============================================================

def main():

    manager = UniverseMemoryManager()

    manager.process_arc()

    manager.save_memory()

    manager.print_summary()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
