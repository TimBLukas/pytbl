"""Programmatic representations of commonly used Mermaid diagrams."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Iterable


def _identifier(value: str) -> str:
    value = str(value).strip()
    if not value:
        raise ValueError("diagram identifiers cannot be empty")
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_-]*$", value):
        raise ValueError(f"invalid Mermaid identifier: {value!r}")
    return value


def _label(value: object) -> str:
    return str(value).replace('"', "&quot;").replace("\n", " ")


class Direction(str, Enum):
    """Flowchart direction."""

    TB = "TB"
    TD = "TD"
    BT = "BT"
    RL = "RL"
    LR = "LR"


@dataclass(frozen=True)
class Node:
    id: str
    label: str | None = None
    shape: str = "rect"

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", _identifier(self.id))

    def syntax(self) -> str:
        label = _label(self.label if self.label is not None else self.id)
        forms = {
            "rect": f'{self.id}["{label}"]',
            "rounded": f'{self.id}("{label}")',
            "stadium": f'{self.id}(["{label}"])',
            "circle": f'{self.id}(("{label}"))',
            "diamond": f'{self.id}{{"{label}"}}',
            "hexagon": f'{self.id}{{{{"{label}"}}}}',
            "asymmetric": f'{self.id}>"{label}"]',
        }
        return forms.get(self.shape, forms["rect"])


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    label: str | None = None
    arrow: str = "-->"

    def syntax(self) -> str:
        source, target = _identifier(self.source), _identifier(self.target)
        if not self.arrow or any(character in self.arrow for character in "\r\n"):
            raise ValueError("invalid Mermaid edge marker")
        middle = f"|{_label(self.label)}|" if self.label is not None else ""
        return f"{source} {self.arrow}{middle} {target}"


@dataclass
class Subgraph:
    title: str
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    id: str | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("subgraph title cannot be empty")
        if self.id is not None:
            self.id = _identifier(self.id)

    def add_node(self, node: Node | str, label: str | None = None, shape: str = "rect") -> "Subgraph":
        self.nodes.append(node if isinstance(node, Node) else Node(node, label, shape))
        return self

    node = add_node

    def add_edge(self, source: str, target: str, label: str | None = None, arrow: str = "-->") -> "Subgraph":
        self.edges.append(Edge(source, target, label, arrow))
        return self

    edge = add_edge

    def syntax(self, indent: str = "    ") -> list[str]:
        header = f"subgraph {self.id} [{_label(self.title)}]" if self.id else f"subgraph {_label(self.title)}"
        lines = [header]
        lines.extend(indent + node.syntax() for node in self.nodes)
        lines.extend(indent + edge.syntax() for edge in self.edges)
        lines.append("end")
        return lines


class MermaidDiagram:
    """Base class for a Mermaid source-producing diagram."""

    diagram_type = ""

    def to_mermaid(self) -> str:
        raise NotImplementedError

    def render(self) -> str:
        return self.to_mermaid()

    def __str__(self) -> str:
        return self.to_mermaid()


class MermaidRenderer:
    """Render a Mermaid diagram to its source representation."""

    def render(self, diagram: MermaidDiagram | object) -> str:
        if hasattr(diagram, "to_mermaid"):
            return str(diagram.to_mermaid())
        return str(diagram)

    render_to_string = render


class Flowchart(MermaidDiagram):
    diagram_type = "flowchart"

    def __init__(
        self,
        direction: str | Direction = Direction.TD,
        nodes: Iterable[Node] = (),
        edges: Iterable[Edge] = (),
        subgraphs: Iterable[Subgraph] = (),
    ) -> None:
        direction = direction.value if isinstance(direction, Direction) else str(direction).upper()
        if direction not in {item.value for item in Direction}:
            raise ValueError("invalid flowchart direction")
        self.direction = direction
        self.nodes = [
            node if isinstance(node, Node) else Node(node[0], node[1] if len(node) > 1 else None)
            if isinstance(node, tuple) else Node(node)
            for node in nodes
        ]
        self.edges = [
            edge if isinstance(edge, Edge) else Edge(*edge) for edge in edges
        ]
        self.subgraphs = list(subgraphs)

    def add_node(self, node: Node | str, label: str | None = None, shape: str = "rect") -> "Flowchart":
        self.nodes.append(node if isinstance(node, Node) else Node(node, label, shape))
        return self

    node = add_node

    def add_edge(self, source: str, target: str, label: str | None = None, arrow: str = "-->") -> "Flowchart":
        self.edges.append(Edge(source, target, label, arrow))
        return self

    edge = add_edge

    def add_subgraph(self, subgraph: Subgraph | str, **kwargs: object) -> Subgraph:
        value = subgraph if isinstance(subgraph, Subgraph) else Subgraph(subgraph, **kwargs)
        self.subgraphs.append(value)
        return value

    subgraph = add_subgraph

    def to_mermaid(self) -> str:
        lines = [f"flowchart {self.direction}"]
        lines.extend(f"    {node.syntax()}" for node in self.nodes)
        lines.extend(f"    {edge.syntax()}" for edge in self.edges)
        for subgraph in self.subgraphs:
            lines.extend(f"    {line}" for line in subgraph.syntax())
        return "\n".join(lines)


@dataclass(frozen=True)
class SequenceMessage:
    source: str
    target: str
    message: str
    arrow: str = "->>"

    def syntax(self) -> str:
        return f"{_identifier(self.source)}{self.arrow}{_identifier(self.target)}: {_label(self.message)}"


class SequenceDiagram(MermaidDiagram):
    diagram_type = "sequenceDiagram"

    def __init__(self, participants: Iterable[str] = (), messages: Iterable[SequenceMessage] = ()) -> None:
        self.participants = list(participants)
        self.messages = [
            message if isinstance(message, SequenceMessage) else SequenceMessage(*message)
            for message in messages
        ]

    def add_participant(self, name: str, alias: str | None = None) -> "SequenceDiagram":
        _identifier(name)
        self.participants.append((name, alias) if alias else name)
        return self

    participant = add_participant

    def add_message(self, source: str, target: str, message: str, arrow: str = "->>") -> "SequenceDiagram":
        self.messages.append(SequenceMessage(source, target, message, arrow))
        return self

    message = add_message

    def to_mermaid(self) -> str:
        lines = ["sequenceDiagram"]
        for participant in self.participants:
            if isinstance(participant, tuple):
                name, alias = participant
                lines.append(f"    participant {_identifier(name)} as {_label(alias)}")
            else:
                lines.append(f"    participant {_identifier(participant)}")
        lines.extend(f"    {message.syntax()}" for message in self.messages)
        return "\n".join(lines)


@dataclass
class ClassDefinition:
    name: str
    members: list[str] = field(default_factory=list)

    def add_member(self, member: str) -> "ClassDefinition":
        self.members.append(str(member).replace("\n", " "))
        return self


class ClassDiagram(MermaidDiagram):
    diagram_type = "classDiagram"

    def __init__(self, classes: Iterable[ClassDefinition] = (), relationships: Iterable[str] = ()) -> None:
        self.classes = [
            value if isinstance(value, ClassDefinition) else ClassDefinition(_identifier(str(value)))
            for value in classes
        ]
        self.relationships = list(relationships)

    def add_class(self, name: str, members: Iterable[str] = ()) -> ClassDefinition:
        definition = ClassDefinition(_identifier(name), list(members))
        self.classes.append(definition)
        return definition

    class_def = add_class

    def add_relationship(self, source: str, target: str, relation: str = "-->") -> "ClassDiagram":
        self.relationships.append(f"{_identifier(source)} {relation} {_identifier(target)}")
        return self

    relationship = add_relationship

    def to_mermaid(self) -> str:
        lines = ["classDiagram"]
        for definition in self.classes:
            lines.append(f"    class {_identifier(definition.name)} {{")
            lines.extend(f"        {member}" for member in definition.members)
            lines.append("    }")
        lines.extend(f"    {relationship}" for relationship in self.relationships)
        return "\n".join(lines)


@dataclass(frozen=True)
class StateTransition:
    source: str
    target: str
    label: str | None = None

    def syntax(self) -> str:
        suffix = f" : {_label(self.label)}" if self.label else ""
        return f"{_identifier(self.source)} --> {_identifier(self.target)}{suffix}"


class StateDiagram(MermaidDiagram):
    diagram_type = "stateDiagram-v2"

    def __init__(self, states: Iterable[str] = (), transitions: Iterable[StateTransition] = ()) -> None:
        self.states = list(states)
        self.transitions = [
            transition if isinstance(transition, StateTransition) else StateTransition(*transition)
            for transition in transitions
        ]

    def add_state(self, state: str) -> "StateDiagram":
        self.states.append(_identifier(state))
        return self

    state = add_state

    def add_transition(self, source: str, target: str, label: str | None = None) -> "StateDiagram":
        self.transitions.append(StateTransition(source, target, label))
        return self

    transition = add_transition

    def to_mermaid(self) -> str:
        lines = ["stateDiagram-v2"]
        lines.extend(f"    state {_identifier(state)}" for state in self.states)
        lines.extend(f"    {transition.syntax()}" for transition in self.transitions)
        return "\n".join(lines)


@dataclass(frozen=True)
class ERRelationship:
    left: str
    cardinality: str
    right: str
    label: str

    def syntax(self) -> str:
        return f"{_identifier(self.left)} {self.cardinality} {_identifier(self.right)} : {_label(self.label)}"


class ERDiagram(MermaidDiagram):
    diagram_type = "erDiagram"

    def __init__(self) -> None:
        self.entities: dict[str, list[tuple[str, str]]] = {}
        self.relationships: list[ERRelationship] = []

    def add_entity(self, name: str, attributes: Iterable[tuple[str, str]] = ()) -> "ERDiagram":
        self.entities[_identifier(name)] = [(str(kind), str(attribute)) for kind, attribute in attributes]
        return self

    entity = add_entity

    def add_relationship(
        self, left: str, cardinality: str, right: str, label: str
    ) -> "ERDiagram":
        self.relationships.append(ERRelationship(left, cardinality, right, label))
        return self

    relationship = add_relationship

    def to_mermaid(self) -> str:
        lines = ["erDiagram"]
        for name, attributes in self.entities.items():
            if attributes:
                lines.append(f"    {name} {{")
                lines.extend(f"        {kind} {attribute}" for kind, attribute in attributes)
                lines.append("    }")
            else:
                lines.append(f"    {name}")
        lines.extend(f"    {relationship.syntax()}" for relationship in self.relationships)
        return "\n".join(lines)


class PieChart(MermaidDiagram):
    diagram_type = "pie"

    def __init__(self, title: str | None = None) -> None:
        self.title = title
        self.slices: list[tuple[str, float | int]] = []

    def add_slice(self, label: str, value: float | int) -> "PieChart":
        if value < 0:
            raise ValueError("pie slice values cannot be negative")
        self.slices.append((label, value))
        return self

    slice = add_slice

    def to_mermaid(self) -> str:
        lines = ["pie" + (f' title {_label(self.title)}' if self.title else "")]
        lines.extend(f'    "{_label(label)}" : {value}' for label, value in self.slices)
        return "\n".join(lines)


FlowChart = Flowchart
ER = ERDiagram
