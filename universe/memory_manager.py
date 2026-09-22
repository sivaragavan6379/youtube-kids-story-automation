import json
import re
from pathlib import Path


# ============================================================
# UNIVERSE MEMORY MANAGER
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MEMORY_FILE = (
    BASE_DIR
    / "universe"
    / "universe_memory.json"
)

ARC_FILE = (
    BASE_DIR
    / "output"
    / "generated_arc.json"
)


# ============================================================
# UNIVERSE MEMORY MANAGER
# ============================================================

class UniverseMemoryManager:

    def __init__(self):

        self.memory = self.load_json(
            MEMORY_FILE
        )

        self.arc_data = self.load_json(
            ARC_FILE
        )

        self.arc = self.arc_data.get(
            "arc",
            {}
        )

        self.prepare_memory_structure()


    # ========================================================
    # LOAD JSON
    # ========================================================

    def load_json(
        self,
        file_path
    ):

        if not file_path.exists():

            raise FileNotFoundError(
                f"File not found:\n{file_path}"
            )

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except json.JSONDecodeError as error:

            raise RuntimeError(
                f"Invalid JSON file:\n"
                f"{file_path}\n\n"
                f"{error}"
            )


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
        print(
            "💾 Universe memory saved:"
        )
        print(
            MEMORY_FILE
        )


    # ========================================================
    # PREPARE MEMORY STRUCTURE
    # ========================================================

    def prepare_memory_structure(self):

        # ----------------------------------------------------
        # Universe
        # ----------------------------------------------------

        if not isinstance(
            self.memory.get("universe"),
            dict
        ):

            self.memory["universe"] = {}

        universe = self.memory["universe"]

        universe.setdefault(
            "id",
            "UNIVERSE-001"
        )

        universe.setdefault(
            "name",
            "Tamil Animated Universe"
        )

        universe.setdefault(
            "description",
            "A connected Tamil animated story universe."
        )

        universe.setdefault(
            "current_phase",
            1
        )

        universe.setdefault(
            "current_series",
            None
        )

        universe.setdefault(
            "current_arc",
            None
        )

        universe.setdefault(
            "current_episode",
            None
        )


        # ----------------------------------------------------
        # Dictionary collections
        # ----------------------------------------------------

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

            value = self.memory.get(
                collection
            )

            if value is None:

                self.memory[
                    collection
                ] = {}

            elif not isinstance(
                value,
                dict
            ):

                print(
                    f"⚠️ Converting "
                    f"{collection} "
                    f"to dictionary."
                )

                self.memory[
                    collection
                ] = {}


        # ----------------------------------------------------
        # List collections
        # ----------------------------------------------------

        list_collections = [

            "timeline",
            "unresolved_threads",
            "foreshadowing",
            "major_events"

        ]

        for collection in list_collections:

            value = self.memory.get(
                collection
            )

            if value is None:

                self.memory[
                    collection
                ] = []

            elif not isinstance(
                value,
                list
            ):

                self.memory[
                    collection
                ] = []


    # ========================================================
    # CREATE SAFE ID
    # ========================================================

    def make_id(
        self,
        text
    ):

        text = str(
            text or ""
        ).strip().lower()

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

        text = text.strip(
            "_"
        )

        if not text:

            text = "unknown"

        return text


    # ========================================================
    # UNIQUE ID
    # ========================================================

    def unique_id(
        self,
        collection,
        base_id
    ):

        collection_data = self.memory.get(
            collection,
            {}
        )

        if base_id not in collection_data:

            return base_id

        counter = 2

        while True:

            candidate = (
                f"{base_id}_{counter}"
            )

            if candidate not in collection_data:

                return candidate

            counter += 1


    # ========================================================
    # FIND BY NAME
    # ========================================================

    def find_by_name(
        self,
        collection,
        name
    ):

        target = self.make_id(
            name
        )

        data = self.memory.get(
            collection,
            {}
        )

        if not isinstance(
            data,
            dict
        ):

            return None

        # Direct key match

        if target in data:

            return data[target]

        # Search stored names

        for item in data.values():

            if not isinstance(
                item,
                dict
            ):

                continue

            stored_name = self.make_id(
                item.get(
                    "name",
                    ""
                )
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

        if not isinstance(
            item,
            dict
        ):

            return None

        name = item.get(
            "name"
        )

        if not name:

            return None

        existing = self.find_by_name(
            collection,
            name
        )

        if existing:

            print(
                f"🔁 Existing "
                f"{collection[:-1]} preserved: "
                f"{name}"
            )

            # Add only missing information.
            # Existing established information
            # is never randomly overwritten.

            for key, value in item.items():

                if key not in existing:

                    existing[key] = value

            return existing


        base_id = (
            preferred_id
            or self.make_id(
                name
            )
        )

        item_id = self.unique_id(
            collection,
            base_id
        )

        item_copy = dict(
            item
        )

        item_copy.setdefault(
            "id",
            item_id
        )

        self.memory[
            collection
        ][
            item_id
        ] = item_copy

        print(
            f"🆕 Added {collection[:-1]}: "
            f"{name}"
        )

        return item_copy


    # ========================================================
    # ADD CHARACTER
    # ========================================================

    def add_character(
        self,
        character
    ):

        if not isinstance(
            character,
            dict
        ):
            return

        name = character.get(
            "name"
        )

        if not name:
            return

        existing = self.find_by_name(
            "characters",
            name
        )

        current_arc = self.arc.get(
            "title"
        )

        if existing:

            print(
                f"🔁 Returning character detected: "
                f"{name}"
            )

            history = existing.setdefault(
                "arc_history",
                []
            )

            if (
                current_arc
                and current_arc not in history
            ):
                history.append(
                    current_arc
                )

            existing[
                "appearance_type"
            ] = "returning"

            existing[
                "status"
            ] = "active"

            existing[
                "last_arc"
            ] = current_arc

            # Preserve established information.
            # Only fill fields that do not already exist.
            for key, value in character.items():
                if key not in existing:
                    existing[key] = value

            return existing

        character_copy = dict(
            character
        )

        character_id = self.make_id(
            name
        )

        character_id = self.unique_id(
            "characters",
            character_id
        )

        character_copy[
            "id"
        ] = character_id

        character_copy.setdefault(
            "status",
            "active"
        )

        character_copy[
            "appearance_type"
        ] = "new"

        character_copy[
            "first_arc"
        ] = current_arc

        character_copy[
            "last_arc"
        ] = current_arc

        character_copy.setdefault(
            "arc_history",
            []
        )

        if current_arc and current_arc not in character_copy[
            "arc_history"
        ]:
            character_copy[
                "arc_history"
            ].append(
                current_arc
            )

        self.memory[
            "characters"
        ][
            character_id
        ] = character_copy

        print(
            f"🆕 New character added: "
            f"{name}"
        )

        return character_copy


    # ========================================================
    # PROCESS CHARACTERS
    # ========================================================

    def process_characters(self):

        # ----------------------------------------------------
        # New characters
        # ----------------------------------------------------

        new_characters = self.arc.get(
            "new_characters",
            []
        )

        if isinstance(
            new_characters,
            list
        ):

            for character in new_characters:

                self.add_character(
                    character
                )


        # ----------------------------------------------------
        # Main characters
        # ----------------------------------------------------

        main_characters = self.arc.get(
            "main_characters",
            []
        )

        if isinstance(
            main_characters,
            list
        ):

            for name in main_characters:

                if not isinstance(
                    name,
                    str
                ):

                    continue

                existing = self.find_by_name(
                    "characters",
                    name
                )

                if existing:

                    history = existing.setdefault(
                        "arc_history",
                        []
                    )

                    current_arc = self.arc.get(
                        "title"
                    )

                    if (
                        current_arc
                        and current_arc not in history
                    ):

                        history.append(
                            current_arc
                        )

                    existing[
                        "appearance_type"
                    ] = "returning"

                    existing[
                        "status"
                    ] = "active"

                    existing[
                        "last_arc"
                    ] = current_arc

                    print(
                        f"↩️ Returning character: "
                        f"{name}"
                    )


        # ----------------------------------------------------
        # Supporting characters
        # ----------------------------------------------------

        supporting_characters = self.arc.get(
            "supporting_characters",
            []
        )

        if isinstance(
            supporting_characters,
            list
        ):

            for name in supporting_characters:

                if not isinstance(
                    name,
                    str
                ):

                    continue

                existing = self.find_by_name(
                    "characters",
                    name
                )

                if existing:

                    history = existing.setdefault(
                        "arc_history",
                        []
                    )

                    current_arc = self.arc.get(
                        "title"
                    )

                    if (
                        current_arc
                        and current_arc not in history
                    ):

                        history.append(
                            current_arc
                        )

                    existing[
                        "appearance_type"
                    ] = "returning"

                    existing[
                        "status"
                    ] = "active"

                    existing[
                        "last_arc"
                    ] = current_arc

                    print(
                        f"↩️ Supporting character: "
                        f"{name}"
                    )


    # ========================================================
    # ADD STORY ARC
    # ========================================================

    def add_story_arc(self):

        title = self.arc.get(
            "title"
        )

        if not title:

            raise RuntimeError(
                "Generated ARC does not contain "
                "a title."
            )

        existing = self.find_by_name(
            "story_arcs",
            title
        )

        if existing:

            print(
                f"🔁 Story arc already exists: "
                f"{title}"
            )

            self.memory[
                "universe"
            ][
                "current_arc"
            ] = existing.get(
                "id"
            )

            return existing


        arc_number = (
            len(
                self.memory[
                    "story_arcs"
                ]
            )
            + 1
        )

        arc_id = (
            f"arc_{arc_number:03d}"
        )

        arc_copy = dict(
            self.arc
        )

        arc_copy[
            "id"
        ] = arc_id

        arc_copy[
            "arc_number"
        ] = arc_number

        self.memory[
            "story_arcs"
        ][
            arc_id
        ] = arc_copy

        self.memory[
            "universe"
        ][
            "current_arc"
        ] = arc_id

        print()
        print(
            f"📚 Story Arc {arc_number} added:"
        )
        print(
            f"   {title}"
        )

        return arc_copy


    # ========================================================
    # ADD EPISODES
    # ========================================================

    def add_episodes(
        self,
        arc_record
    ):

        episodes = self.arc.get(
            "episodes",
            []
        )

        if not isinstance(
            episodes,
            list
        ):

            return


        arc_id = arc_record.get(
            "id"
        )

        arc_number = arc_record.get(
            "arc_number",
            1
        )


        for index, episode in enumerate(
            episodes,
            start=1
        ):

            if not isinstance(
                episode,
                dict
            ):

                continue

            episode_number = episode.get(
                "episode_number",
                index
            )

            title = episode.get(
                "title",
                f"Episode {episode_number}"
            )

            episode_id = (
                f"{arc_id}_ep_"
                f"{int(episode_number):02d}"
            )

            episode_copy = dict(
                episode
            )

            episode_copy[
                "id"
            ] = episode_id

            episode_copy[
                "arc_id"
            ] = arc_id

            episode_copy[
                "arc_number"
            ] = arc_number

            episode_copy.setdefault(
                "status",
                "planned"
            )

            allowed_statuses = {
                "planned",
                "scripted",
                "generated",
                "completed",
                "published"
            }

            status = str(
                episode_copy.get(
                    "status",
                    "planned"
                )
            ).strip().lower()

            if status not in allowed_statuses:
                status = "planned"

            episode_copy[
                "status"
            ] = status

            existing = self.memory[
                "episodes"
            ].get(
                episode_id
            )

            if existing:

                print(
                    f"🔁 Episode already exists: "
                    f"{episode_id}"
                )

                continue

            self.memory[
                "episodes"
            ][
                episode_id
            ] = episode_copy

            print(
                f"🎬 Episode added: "
                f"EP {episode_number} - "
                f"{title}"
            )


    # ========================================================
    # PROCESS LOCATIONS
    # ========================================================

    def process_locations(self):

        locations = self.arc.get(
            "locations",
            []
        )

        if not isinstance(
            locations,
            list
        ):

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

        if not isinstance(
            artifacts,
            list
        ):

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

        if not isinstance(
            villains,
            list
        ):

            return

        for villain in villains:

            self.add_dictionary_item(
                "villains",
                villain
            )


    # ========================================================
    # PROCESS MYSTERIES
    # ========================================================

    def process_mysteries(self):

        mysteries = self.arc.get(
            "mysteries",
            []
        )

        if not isinstance(
            mysteries,
            list
        ):

            return

        for mystery in mysteries:

            added = self.add_dictionary_item(
                "mysteries",
                mystery
            )

            if added:

                self.add_unresolved_thread(
                    mystery
                )


        # Central mysteries

        central_mysteries = self.arc.get(
            "central_mysteries",
            []
        )

        if isinstance(
            central_mysteries,
            list
        ):

            for mystery in central_mysteries:

                self.add_unresolved_thread(
                    {
                        "name": mystery,

                        "type":
                            "central_mystery",

                        "arc":
                            self.arc.get(
                                "title"
                            ),

                        "status":
                            "active"
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

            relationship_id = self.unique_id(
                "relationships",
                relationship_id
            )

            # Check if same relationship already exists

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
                        existing.get(
                            "source"
                        )
                    )
                    ==
                    self.make_id(
                        source
                    )
                    and
                    self.make_id(
                        existing.get(
                            "target"
                        )
                    )
                    ==
                    self.make_id(
                        target
                    )
                    and
                    self.make_id(
                        existing.get(
                            "relationship"
                        )
                    )
                    ==
                    self.make_id(
                        relation
                    )
                ):

                    already_exists = True

                    break

            if already_exists:

                continue

            relationship_copy = dict(
                relationship
            )

            relationship_copy[
                "id"
            ] = relationship_id

            self.memory[
                "relationships"
            ][
                relationship_id
            ] = relationship_copy

            print(
                f"🔗 Relationship added: "
                f"{source} → {target}"
            )


    # ========================================================
    # ADD UNRESOLVED THREAD
    # ========================================================

    def add_unresolved_thread(
        self,
        thread
    ):

        if isinstance(
            thread,
            dict
        ):

            name = thread.get(
                "name",
                "Unknown Thread"
            )

            thread_copy = dict(
                thread
            )

        else:

            name = str(
                thread
            )

            thread_copy = {
                "name": name
            }


        normalized_name = self.make_id(
            name
        )

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

            if (
                existing_name
                == normalized_name
            ):

                return


        thread_copy.setdefault(
            "status",
            "active"
        )

        thread_copy.setdefault(
            "arc",
            self.arc.get(
                "title"
            )
        )

        self.memory[
            "unresolved_threads"
        ].append(
            thread_copy
        )

        print(
            f"❓ Unresolved thread added: "
            f"{name}"
        )


    # ========================================================
    # PROCESS FORESHADOWING
    # ========================================================

    def process_foreshadowing(self):

        clues = self.arc.get(
            "foreshadowing",
            []
        )

        if not isinstance(
            clues,
            list
        ):

            return

        for clue in clues:

            if not isinstance(
                clue,
                dict
            ):

                continue

            event = dict(
                clue
            )

            event[
                "arc"
            ] = self.arc.get(
                "title"
            )

            self.memory[
                "foreshadowing"
            ].append(
                event
            )

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

        if not isinstance(
            events,
            list
        ):

            return

        for event in events:

            event_record = {

                "arc":
                    self.arc.get(
                        "title"
                    ),

                "event":
                    event
            }

            self.memory[
                "major_events"
            ].append(
                event_record
            )

            self.memory[
                "timeline"
            ].append(
                {
                    "type":
                        "major_event",

                    "arc":
                        self.arc.get(
                            "title"
                        ),

                    "event":
                        event
                }
            )

            print(
                f"📜 Major event saved: "
                f"{event}"
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
                    "type":
                        "arc_consequence",

                    "arc":
                        self.arc.get(
                            "title"
                        ),

                    "event":
                        consequence
                }
            )


    # ========================================================
    # PROCESS FUTURE HOOK
    # ========================================================

    def process_future_hook(self):

        future_hook = self.arc.get(
            "future_arc_hook"
        )

        if not future_hook:

            return

        self.add_unresolved_thread(
            {
                "name":
                    "Future Arc Hook",

                "description":
                    future_hook,

                "type":
                    "future_arc_hook",

                "status":
                    "active",

                "arc":
                    self.arc.get(
                        "title"
                    )
            }
        )


    # ========================================================
    # UPDATE UNIVERSE STATE
    # ========================================================

    def update_universe_state(
        self,
        arc_record
    ):

        universe = self.memory[
            "universe"
        ]

        universe[
            "current_arc"
        ] = arc_record.get(
            "id"
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

        if isinstance(episodes, list):
            for episode in episodes:
                if not isinstance(episode, dict):
                    continue

                status = str(
                    episode.get("status", "planned")
                ).strip().lower()

                if status in completed_statuses:
                    completed_episodes.append(episode)

        if completed_episodes:
            last_episode = completed_episodes[-1]
            universe[
                "current_episode"
            ] = last_episode.get(
                "episode_number"
            )
        else:
            universe[
                "current_episode"
            ] = None

        universe[
            "current_phase"
        ] = universe.get(
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
            "title"
        )

        print()
        print(
            "============================================"
        )
        print(
            "🧠 MEMORY MANAGER"
        )
        print(
            "============================================"
        )
        print()

        print(
            f"📖 Processing ARC:"
        )

        print(
            f"   {title}"
        )

        print()


        # ----------------------------------------------------
        # 1. Story Arc
        # ----------------------------------------------------

        arc_record = self.add_story_arc()


        # ----------------------------------------------------
        # 2. Characters
        # ----------------------------------------------------

        self.process_characters()


        # ----------------------------------------------------
        # 3. Locations
        # ----------------------------------------------------

        self.process_locations()


        # ----------------------------------------------------
        # 4. Artifacts
        # ----------------------------------------------------

        self.process_artifacts()


        # ----------------------------------------------------
        # 5. Villains
        # ----------------------------------------------------

        self.process_villains()


        # ----------------------------------------------------
        # 6. Mysteries
        # ----------------------------------------------------

        self.process_mysteries()


        # ----------------------------------------------------
        # 7. Relationships
        # ----------------------------------------------------

        self.process_relationships()


        # ----------------------------------------------------
        # 8. Episodes
        # ----------------------------------------------------

        self.add_episodes(
            arc_record
        )


        # ----------------------------------------------------
        # 9. Foreshadowing
        # ----------------------------------------------------

        self.process_foreshadowing()


        # ----------------------------------------------------
        # 10. Major Events
        # ----------------------------------------------------

        self.process_major_events()


        # ----------------------------------------------------
        # 11. Consequences
        # ----------------------------------------------------

        self.process_consequences()


        # ----------------------------------------------------
        # 12. Future Hook
        # ----------------------------------------------------

        self.process_future_hook()


        # ----------------------------------------------------
        # 13. Universe State
        # ----------------------------------------------------

        self.update_universe_state(
            arc_record
        )


        print()
        print(
            "============================================"
        )

        print(
            "✅ ARC MEMORY UPDATE COMPLETE"
        )

        print(
            "============================================"


        )


    # ========================================================
    # SUMMARY
    # ========================================================

    def print_summary(self):

        print()
        print(
            "============================================"
        )

        print(
            "📊 UNIVERSE MEMORY SUMMARY"
        )

        print(
            "============================================"
        )

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

        print(
            "============================================"
        )


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
