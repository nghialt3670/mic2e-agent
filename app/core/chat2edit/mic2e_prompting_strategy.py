from chat2edit.models import Feedback
from chat2edit.prompting.strategies import OtcPromptingStrategy

from app.core.chat2edit.mic2e_feedbacks import (
    PromptBasedObjectDetectionQuantityMismatchFeedback,
)

PROMPT_BASED_OBJECT_DETECTION_QUANTITY_MISMATCH_FEEDBACK_TEXT = "Expected to extract {expected_quantity} object(s) with prompt '{prompt}', but found {detected_quantity} object(s)."


class Mic2ePromptingStrategy(OtcPromptingStrategy):
    def __init__(self) -> None:
        super().__init__()

    def create_feedback_text(self, feedback: Feedback) -> str:
        if isinstance(feedback, PromptBasedObjectDetectionQuantityMismatchFeedback):
            return PROMPT_BASED_OBJECT_DETECTION_QUANTITY_MISMATCH_FEEDBACK_TEXT.format(
                prompt=feedback.prompt,
                expected_quantity=feedback.expected_quantity,
                detected_quantity=feedback.detected_quantity,
            )

        return super().create_feedback_text(feedback)
