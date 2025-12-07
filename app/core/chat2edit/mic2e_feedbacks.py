from typing import Literal

# Import Feedback directly from the module to avoid triggering FeedbackUnion creation
from chat2edit.models.feedback import Feedback
from pydantic import Field


class PromptBasedObjectDetectionQuantityMismatchFeedback(Feedback):
    type: Literal["prompt_based_object_detection_quantity_mismatch"] = (
        "prompt_based_object_detection_quantity_mismatch"
    )
    severity: Literal["info", "warning", "error"] = Field(default="error")
    prompt: str
    expected_quantity: int
    detected_quantity: int
