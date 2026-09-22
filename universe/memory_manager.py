import json
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


class UniverseMemoryManager:

    def __init__(self):

        self.memory = self.load_json(
            MEMORY_FILE,
            default=self.create_empty_memory()
        )

        self.arc = self.load_json(
            ARC_FILE,
            default=None
        )


    # ========================================================
    # EMPTY UNIVERSE
    # ========================================================

    def create_empty_memory(self):

        return {

            "universe": {

                "name": "Tamil Animated Shared Universe",

                "description":
                    "A continuously evolving Tamil animated "
                    "children's adventure universe.",

                "current_phase": 1,

                "current_arc": 0,

                "current_episode": 0
            },

            "characters": [],

            "locations": [],

            "artifacts": [],

            "villains": [],

            "relationships": [],

            "mysteries": [],

            "story_arcs": [],

            "episodes": [],

            "timeline": [],

            "unresolved_threads": []
        }


    # ========================================================
    # LOAD JSON
    # ========================================================

    def load_json(
        self,
        file_path,
        default=None
    ):

        if not file_path.exists():

            if default is not None:

                return default

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
    # SAVE MEMORY
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
    # NORMALIZE NAME
    # ========================================================

    def normalize_name(
        self,
        name
    ):

        return str(
            name
        ).strip().lower()


    # ========================================================
    # FIND CHARACTER
    # ========================================================

    def find_character(
        self,
        name
    ):

        target = (
            self.normalize_name(
                name
            )
        )

        for character in self.memory[
            "characters"
        ]:

            existing_name = (
                character.get(
                    "name",
                    ""
                )
            )

            if (
                self.normalize_name(
                    existing_name
                )
                == target
            ):

                return character

        return None


    # ========================================================
    # ADD OR UPDATE CHARACTER
    # ========================================================

    def add_character(
        self,
        character
    ):

        name = character.get(
            "name"
        )

        if not name:

            return

        existing = (
            self.find_character(
                name
            )
        )

        if existing:

            print(
                f"🔁 Existing character preserved: "
                f"{name}"
            )

            # Only add information that does not
            # already exist. Do not overwrite established
            # identity accidentally.

            for key, value in character.items():

                if key == "name":

                    continue

                if key not in existing:

                    existing[key] = value

            return

        character_copy = dict(
            character
        )

        character_copy.setdefault(
            "status",
            "active"
        )

        character_copy.setdefault(
            "first_arc",
            self.memory[
                "universe"
            ].get(
                "current_arc",
                0
            ) + 1
        )

        character_copy.setdefault(
            "return_history",
            []
        )

        self.memory[
            "characters"
        ].append(
            character_copy
        )

        print(
            f"🆕 New character added: "
            f"{name}"
        )


    # ========================================================
    # FIND GENERIC ITEM
    # ========================================================

    def find_item(
        self,
        collection_name,
        name
    ):

        target = (
            self.normalize_name(
                name
            )
        )

        collection = self.memory.get(
            collection_name,
            []
        )

        for item in collection:

            item_name = item.get(
                "name",
                ""
            )

            if (
                self.normalize_name(
                    item_name
                )
                == target
            ):

                return item

        return None


    # ========================================================
    # ADD GENERIC ITEM
    # ========================================================

    def add_item(
        self,
        collection_name,
        item
    ):

        if not isinstance(
            item,
            dict
        ):

            return

        name = item.get(
            "name"
        )

        if not name:

            return

        existing = (
            self.find_item(
                collection_name,
                name
            )
        )

        if existing:

            print(
                f"🔁 Existing "
                f"{collection_name[:-1]} preserved: "
                f"{name}"
            )

            for key, value in item.items():

                if key == "name":

                    continue

                if key not in existing:

                    existing[key] = value

            return

        self.memory[
            collection_name
        ].append(
            dict(item)
        )

        print(
            f"🆕 Added to "
            f"{collection_name}: "
            f"{name}"
        )


    # ========================================================
    # ADD RELATIONSHIP
    # ========================================================

    def add_relationship(
        self,
        relationship
    ):

        if not isinstance(
            relationship,
            dict
        ):

            return

        source = relationship.get(
            "source"
        )

        target = relationship.get(
            "target"
        )

        relation = relationship.get(
            "relationship"
        )

        if not source or not target:

            return

        for existing in self.memory[
            "relationships"
        ]:

            if (

                self.normalize_name(
                    existing.get(
                        "source",
                        ""
                    )
                )
                == self.normalize_name(
                    source
                )

                and

                self.normalize_name(
                    existing.get(
                        "target",
                        ""
                    )
                )
                == self.normalize_name(
                    target
                )

                and

                self.normalize_name(
                    existing.get(
                        "relationship",
                        ""
                    )
                )
                == self.normalize_name(
                    relation or ""
                )
            ):

                return

        self.memory[
            "relationships"
        ].append(
            dict(relationship)
        )


    # ========================================================
    # ADD ARC
    # ========================================================

    def add_arc(
        self,
        arc
    ):

        title = arc.get(
            "title"
        )

        if not title:

            return

        existing_arc = None

        for old_arc in self.memory[
            "story_arcs"
        ]:

            if (
                self.normalize_name(
                    old_arc.get(
                        "title",
                        ""
                    )
                )
                ==
                self.normalize_name(
                    title
                )
            ):

                existing_arc = old_arc

                break

        if existing_arc:

            print(
                f"🔁 Arc already exists: "
                f"{title}"
            )

            return

        arc_number = (
            len(
                self.memory[
                    "story_arcs"
                ]
            )
            + 1
        )

        arc_copy = dict(
            arc
        )

        arc_copy[
            "arc_number"
        ] = arc_number

        self.memory[
            "story_arcs"
        ].append(
            arc_copy
        )

        self.memory[
            "universe"
        ][
            "current_arc"
        ] = arc_number

        print(
            f"📚 Story Arc {arc_number} added: "
            f"{title}"
        )


    # ========================================================
    # ADD EPISODES
    # ========================================================

    def add_episodes(
        self,
        arc
    ):

        episodes = arc.get(
            "episodes",
            []
        )

        arc_number = (
            self.memory[
                "universe"
            ].get(
                "current_arc",
                0
            )
        )

        for episode in episodes:

            if not isinstance(
                episode,
                dict
            ):

                continue

            episode_number = episode.get(
                "episode_number"
            )

            title = episode.get(
                "title"
            )

            already_exists = False

            for existing in self.memory[
                "episodes"
            ]:

                if (

                    existing.get(
                        "arc_number"
                    )
                    == arc_number

                    and

                    existing.get(
                        "episode_number"
                    )
                    == episode_number
                ):

                    already_exists = True

                    break

            if already_exists:

                continue

            episode_copy = dict(
                episode
            )

            episode_copy[
                "arc_number"
            ] = arc_number

            episode_copy[
                "status"
            ] = "planned"

            self.memory[
                "episodes"
            ].append(
                episode_copy
            )

            print(
                f"🎬 Episode added: "
                f"EP {episode_number} - "
                f"{title}"
            )

            self.memory[
                "universe"
            ][
                "current_episode"
            ] = max(

                self.memory[
                    "universe"
                ].get(
                    "current_episode",
                    0
                ),

                int(
                    episode_number
                    or 0
                )
            )


    # ========================================================
    # ADD TIMELINE EVENT
    # ========================================================

    def add_timeline_event(
        self,
        event
    ):

        if not event:

            return

        if event in self.memory[
            "timeline"
        ]:

            return

        self.memory[
            "timeline"
        ].append(
            event
        )


    # ========================================================
    # ADD UNRESOLVED THREAD
    # ========================================================

    def add_unresolved_thread(
        self,
        thread
    ):

        if not thread:

            return

        normalized = (
            self.normalize_name(
                thread
            )
        )

        for existing in self.memory[
            "unresolved_threads"
        ]:

            if (
                self.normalize_name(
                    existing.get(
                        "name",
                        existing
                    )
                )
                == normalized
            ):

                return

        if isinstance(
            thread,
            dict
        ):

            self.memory[
                "unresolved_threads"
            ].append(
                dict(thread)
            )

        else:

            self.memory[
                "unresolved_threads"
            ].append(
                {
                    "name": str(
                        thread
                    ),

                    "status": "active"
                }
            )


    # ========================================================
    # PROCESS CHARACTERS
    # ========================================================

    def process_characters(
        self,
        arc
    ):

        existing_names = {
            self.normalize_name(
                c.get(
                    "name",
                    ""
                )
            )

            for c in self.memory[
                "characters"
            ]
        }

        # ----------------------------------------------------
        # NEW CHARACTERS
        # ----------------------------------------------------

        for character in arc.get(
            "new_characters",
            []
        ):

            name = character.get(
                "name"
            )

            if not name:

                continue

            normalized = (
                self.normalize_name(
                    name
                )
            )

            if normalized in existing_names:

                print(
                    f"⚠️ Character "
                    f"'{name}' was marked as new "
                    f"but already exists."
                )

                continue

            self.add_character(
                character
            )

            existing_names.add(
                normalized
            )


        # ----------------------------------------------------
        # MAIN / SUPPORTING CHARACTERS
        # ----------------------------------------------------

        participating_names = []

        participating_names.extend(
            arc.get(
                "main_characters",
                []
            )
        )

        participating_names.extend(
            arc.get(
                "supporting_characters",
                []
            )
        )

        for name in participating_names:

            if not isinstance(
                name,
                str
            ):

                continue

            character = (
                self.find_character(
                    name
                )
            )

            if character:

                history = character.setdefault(
                    "return_history",
                    []
                )

                arc_number = (
                    self.memory[
                        "universe"
                    ].get(
                        "current_arc",
                        0
                    )
                )

                if arc_number not in history:

                    history.append(
                        arc_number
                    )

                    print(
                        f"↩️ Returning character: "
                        f"{name}"
                    )


    # ========================================================
    # PROCESS ARC
    # ========================================================

    def process_arc(
        self
    ):

        if not self.arc:

            raise FileNotFoundError(
                "generated_arc.json was not found."
            )

        if "arc" not in self.arc:

            raise RuntimeError(
                "generated_arc.json does not "
                "contain an 'arc' object."
            )

        arc = self.arc[
            "arc"
        ]

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

        # ----------------------------------------------------
        # ARC
        # ----------------------------------------------------

        self.add_arc(
            arc
        )

        # ----------------------------------------------------
        # CHARACTERS
        # ----------------------------------------------------

        self.process_characters(
            arc
        )

        # ----------------------------------------------------
        # LOCATIONS
        # ----------------------------------------------------

        for location in arc.get(
            "locations",
            []
        ):

            self.add_item(
                "locations",
                location
            )

        # ----------------------------------------------------
        # ARTIFACTS
        # ----------------------------------------------------

        for artifact in arc.get(
            "artifacts",
            []
        ):

            self.add_item(
                "artifacts",
                artifact
            )

        # ----------------------------------------------------
        # MYSTERIES
        # ----------------------------------------------------

        for mystery in arc.get(
            "mysteries",
            []
        ):

            self.add_item(
                "mysteries",
                mystery
            )

            self.add_unresolved_thread(
                mystery
            )

        # ----------------------------------------------------
        # EPISODES
        # ----------------------------------------------------

        self.add_episodes(
            arc
        )

        # ----------------------------------------------------
        # CENTRAL MYSTERIES
        # ----------------------------------------------------

        for mystery_name in arc.get(
            "central_mysteries",
            []
        ):

            self.add_unresolved_thread(
                mystery_name
            )

        # ----------------------------------------------------
        # FORESHADOWING
        # ----------------------------------------------------

        for clue in arc.get(
            "foreshadowing",
            []
        ):

            self.add_timeline_event(
                {
                    "type": "foreshadowing",

                    "arc": self.memory[
                        "universe"
                    ].get(
                        "current_arc",
                        0
                    ),

                    "data": clue
                }
            )

        # ----------------------------------------------------
        # MAJOR EVENTS
        # ----------------------------------------------------

        for event in arc.get(
            "major_events",
            []
        ):

            self.add_timeline_event(
                {
                    "type": "major_event",

                    "arc": self.memory[
                        "universe"
                    ].get(
                        "current_arc",
                        0
                    ),

                    "event": event
                }
            )

        # ----------------------------------------------------
        # FUTURE ARC HOOK
        # ----------------------------------------------------

        future_hook = arc.get(
            "future_arc_hook"
        )

        if future_hook:

            self.add_unresolved_thread(
                {
                    "name":
                        "Future Arc Hook",

                    "description":
                        future_hook,

                    "status":
                        "active"
                }
            )

        # ----------------------------------------------------
        # ARC CONSEQUENCES
        # ----------------------------------------------------

        for consequence in arc.get(
            "arc_consequences",
            []
        ):

            self.add_timeline_event(
                {
                    "type": "arc_consequence",

                    "arc": self.memory[
                        "universe"
                    ].get(
                        "current_arc",
                        0
                    ),

                    "event": consequence
                }
            )

        print()

        print(
            "✅ ARC MEMORY UPDATE COMPLETE"
        )


    # ========================================================
    # SUMMARY
    # ========================================================

    def print_summary(
        self
    ):

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
            f"Characters: "
            f"{len(self.memory['characters'])}"
        )

        print(
            f"Locations: "
            f"{len(self.memory['locations'])}"
        )

        print(
            f"Artifacts: "
            f"{len(self.memory['artifacts'])}"
        )

        print(
            f"Mysteries: "
            f"{len(self.memory['mysteries'])}"
        )

        print(
            f"Story Arcs: "
            f"{len(self.memory['story_arcs'])}"
        )

        print(
            f"Episodes: "
            f"{len(self.memory['episodes'])}"
        )

        print(
            f"Timeline Events: "
            f"{len(self.memory['timeline'])}"
        )

        print(
            f"Unresolved Threads: "
            f"{len(self.memory['unresolved_threads'])}"
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
