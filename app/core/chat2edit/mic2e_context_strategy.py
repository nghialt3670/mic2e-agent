import re
from copy import deepcopy
from typing import Any, Dict, List, Union

from chat2edit.context.strategies import ContextStrategy
from chat2edit.context.utils import assign_context_values, path_to_value
from chat2edit.models import Message
from pydantic import TypeAdapter
from chat2edit.utils import to_snake_case

from app.core.chat2edit.models import Box, Image, Object, Point, Scribble, Text
from app.core.chat2edit.models.image import Entity
from app.core.chat2edit.models.referent import Reference

CONTEXT_VALUE_BASE_TYPE = Union[
    Image,
    Object,
    Box,
    Point,
    Text,
    Scribble,
    int,
    str,
    float,
    bool,
]
# Single allowed item type (value or list of values) used for filtering
CONTEXT_ITEM_TYPE = Union[CONTEXT_VALUE_BASE_TYPE, List[CONTEXT_VALUE_BASE_TYPE]]
CONTEXT_TYPE = Dict[str, Union[CONTEXT_VALUE_BASE_TYPE, List[CONTEXT_VALUE_BASE_TYPE]]]


class Mic2eContextStrategy(ContextStrategy):
    def __init__(self) -> None:
        super().__init__()

    def filter_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        filtered_context: Dict[str, Any] = {}
        item_adapter = TypeAdapter(CONTEXT_ITEM_TYPE)

        for key, value in context.items():
            try:
                item_adapter.validate_python(value)
                filtered_context[key] = value
            except Exception:
                continue

        return filtered_context

    def contextualize_message(
        self, message: Message, context: Dict[str, Any]
    ) -> Message:
        message = deepcopy(message)
        if message.contextualized:
            return message

        references = self._extract_references_from_text(message.text)
        referenced_entities = self._extract_referenced_entities(
            message.attachments, references
        )
        self._remove_ephemeral_entities(message.attachments)
        referenced_varnames = assign_context_values(referenced_entities, context)
        message.text = self._contextualize_message_text(
            message.text, references, referenced_varnames
        )
        referenced_entity_ids = set(entity.id for entity in referenced_entities)
        attachment_varnames = assign_context_values(
            [attachment for attachment in message.attachments if attachment.id not in referenced_entity_ids],
            context,
            get_varname_prefix=self._make_prefix_fn(),
        )
        attachment_varnames.extend(referenced_varnames)
        message.attachments = attachment_varnames
        message.contextualized = True
        return message

    def decontextualize_message(
        self, message: Message, context: Dict[str, Any]
    ) -> Message:
        message = deepcopy(message)
        if not message.contextualized:
            return message

        varnames = self._extract_varnames_from_text(message.text)
        references = self._extract_references_from_varnames(varnames, context)
        message.text = self._decontextualize_message_text(
            message.text, varnames, references
        )
        message.attachments = [
            path_to_value(path, context) for path in message.attachments
        ]
        message.contextualized = False
        return message

    def _make_prefix_fn(self):
        def _prefix(value: Any) -> str:
            # If the value has an explicit variable name, honor it
            name = getattr(value, "name", None)
            if isinstance(name, str) and name:
                return name
            # Fallback to default snake_case basename
            return to_snake_case(type(value).__name__).split("_").pop()

        return _prefix

    def _extract_references_from_text(self, text: str) -> List[Reference]:
        # Match patterns like:
        #   #red[cat](123e4567-e89b-12d3-a456-426614174000)
        #   #45f23c[image](32b63eae-08e4-479f-9815-f13b0...)
        # Groups:
        #   1 -> label (alphanumeric/underscore after '#')
        #   2 -> inner text between [ ]
        #   3 -> value between parentheses, stopping at the first closing parenthesis
        # Use [^)] instead of [^@] so we don't greedily swallow subsequent references.
        ref_pattern = r"#([a-zA-Z0-9_]+)\[([^\]]+)\]\(([^)]+)\)"
        matches = re.findall(ref_pattern, text)
        return [
            Reference(label=label, value=value, color=color)
            for color, label, value in matches
        ]

    def _extract_varnames_from_text(self, text: str) -> List[str]:
        ref_pattern = r"(?<![A-Za-z0-9_])@([A-Za-z_][A-Za-z0-9_]*)(?![A-Za-z0-9_])"
        return re.findall(ref_pattern, text)

    def _extract_references_from_varnames(
        self, varnames: List[str], context: Dict[str, Any]
    ) -> List[Reference]:
        references = []
        for varname in varnames:
            referent = path_to_value(varname, context)
            if referent.reference:
                references.append(referent.reference)
            else:
                label = varname.split("_")[0].replace("@", "")
                reference = Reference(label=label)
                referent.reference = reference
                references.append(reference)
        return references

    def _extract_referenced_entities(
        self, attachments: List[Image], references: List[Reference]
    ) -> List[Entity]:
        reference_value_to_entity: Dict[str, Entity] = {}
        for attachment in attachments:
            if attachment.reference is not None:
                reference_value_to_entity[attachment.reference.value] = attachment

            for obj in attachment.get_objects():
                if obj.reference is not None:
                    reference_value_to_entity[obj.reference.value] = obj

        referenced_entities = []
        for reference in references:
            entity = reference_value_to_entity[reference.value]
            referenced_entities.append(entity)

        return referenced_entities

    def _remove_ephemeral_entities(self, attachments: List[Image]) -> None:
        for attachment in attachments:
            for obj in attachment.get_objects():
                if obj.ephemeral:
                    attachment.remove_object(obj)

    def _contextualize_message_text(
        self, text: str, references: List[Reference], varnames: List[str]
    ) -> str:
        for reference, varname in zip(references, varnames):
            old = f"#{reference.color}[{reference.label}]({reference.value})"
            new = f"@{varname}"
            text = text.replace(old, new)
        return text

    def _decontextualize_message_text(
        self, text: str, varnames: List[str], references: List[Reference]
    ) -> str:
        for varname, reference in zip(varnames, references):
            old = f"@{varname}"
            new = f"#{reference.color}[{reference.label}]({reference.value})"
            text = text.replace(old, new)
        return text
