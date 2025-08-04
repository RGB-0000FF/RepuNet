import json
import os
import typing
from enum import Enum


class NodeType(Enum):
    CHAT = 1
    THOUGHT = 2
    EVENT = 3
    ACTION = 4

    def toJSON(self):
        return self.name


class Node:
    id: int
    type: NodeType

    subject: str
    predicate: str
    object: str

    description: str

    created_at: int

    def __init__(
        self,
        id: int,
        type: NodeType,
        subject: str,
        predicate: str,
        object: str,
        description: str,
        created_at: int,
    ) -> None:
        self.id = id
        self.type = type
        self.subject = subject
        self.predicate = predicate
        self.object = object
        self.description = description
        self.created_at = created_at

    def __str__(self) -> str:
        return f"{self.subject} {self.predicate} {self.object}"

    def toJSON(self):
        return {
            "id": self.id,
            "type": self.type.toJSON(),
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "description": self.description,
            "created_at": self.created_at,
        }


class Chat(Node):
    conversation: list[tuple[str, str]]

    def __init__(
        self,
        id: int,
        subject: str,
        predicate: str,
        object: str,
        description: str,
        conversation: list[tuple[str, str]],
        created_at: int,
    ) -> None:
        self.conversation = conversation
        super().__init__(
            id,
            NodeType.CHAT,
            subject,
            predicate,
            object,
            description,
            created_at,
        )

    def toJSON(self):
        return {
            "id": self.id,
            "type": self.type.toJSON(),
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "description": self.description,
            "conversation": self.conversation,
            "created_at": self.created_at,
        }


class Event(Node):
    def __init__(
        self,
        id: int,
        subject: str,
        predicate: str,
        object: str,
        description: str,
        created_at: int,
    ) -> None:
        super().__init__(
            id,
            NodeType.EVENT,
            subject,
            predicate,
            object,
            description,
            created_at,
        )


class AssociativeMemory:
    def __init__(self, base_path, do_load=False) -> None:
        self.id_to_node: typing.Dict[int, Node] = dict()

        self.chat_id_to_node: typing.Dict[int, Node] = dict()
        self.event_id_to_node: typing.Dict[int, Node] = dict()

        self.base_path = base_path
        if os.path.exists(f"{base_path}/nodes.json") and do_load:
            self._load(base_path)

    def _load(self, base_path):
        saved_nodes = json.load(open(f"{base_path}/nodes.json"))
        for node in saved_nodes:
            n_type = node["type"]
            # SAVE DESCRIPTION!!!!!TODO
            if type(node["description"]) is list:
                node["description"] = node["description"][0]
            if n_type != NodeType.CHAT.name:
                self.id_to_node[node["id"]] = Node(
                    node["id"],
                    NodeType[node["type"]],
                    node["subject"],
                    node["predicate"],
                    node["object"],
                    node["description"],
                    node["created_at"],
                )
            else:
                if "conversation" in node:
                    convo = node["conversation"]
                else:
                    convo = "THERE SOMETHING WRONG! BUT HAS FIXED!"
                self.id_to_node[node["id"]] = Chat(
                    node["id"],
                    node["subject"],
                    node["predicate"],
                    node["object"],
                    node["description"],
                    convo,
                    node["created_at"],
                )

            if n_type == NodeType.EVENT.name:
                self.event_id_to_node[node["id"]] = node

            if n_type == NodeType.CHAT.name:
                self.chat_id_to_node[node["id"]] = node

    def save(self):
        json.dump(
            [node.toJSON() for node in self.id_to_node.values()],
            open(f"{self.base_path}/nodes.json", "w"),
            indent=4,
        )

    def _add(
        self,
        subject,
        predicate,
        obj,
        description,
        type,
        conversation=None,
        created_at=None,
    ) -> Node:
        id = len(self.id_to_node) + 1

        if type == NodeType.CHAT:
            node = Chat(
                id=id,
                subject=subject,
                predicate=predicate,
                object=obj,
                description=description,
                conversation=conversation,
                created_at=created_at,
            )
            self.chat_id_to_node[id] = node
        elif type == NodeType.EVENT:
            node = Event(
                id=id,
                subject=subject,
                predicate=predicate,
                object=obj,
                description=description,
                created_at=created_at,
            )
            self.event_id_to_node[id] = node

        self.id_to_node[id] = node

        return node

    def add_chat(
        self,
        subject,
        predicate,
        obj,
        description,
        created_at,
        conversation,
    ) -> Chat:
        node = self._add(
            subject=subject,
            predicate=predicate,
            obj=obj,
            description=description,
            type=NodeType.CHAT,
            conversation=conversation,
            created_at=created_at,
        )
        return node

    def add_event(
        self,
        subject,
        predicate,
        obj,
        description,
        created_at,
    ) -> Event:
        return self._add(
            subject=subject,
            predicate=predicate,
            obj=obj,
            description=description,
            type=NodeType.EVENT,
            created_at=created_at,
        )

    def get_latest_event(self):
        if len(self.event_id_to_node) == 0:
            return []
        return self.event_id_to_node[max(self.event_id_to_node.keys())]

    def get_latest_event_with_target(self, target_name: str, by="object"):
        matched_nodes = []
        for node in self.event_id_to_node.values():
            if isinstance(node, Event):
                node = node.toJSON()
            if node[by] == target_name:
                matched_nodes.append(node)
        matched_nodes.sort(key=lambda x: x["created_at"], reverse=True)
        descriptions = ""
        for i, node in enumerate(matched_nodes[:5]):
            patch = f"Latest Round {i + 1}: {node['description']}\n\n"
            descriptions += patch

        return descriptions
