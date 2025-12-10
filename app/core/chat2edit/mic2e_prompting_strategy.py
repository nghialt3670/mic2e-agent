from chat2edit.models import Feedback
from chat2edit.prompting.strategies import OtcPromptingStrategy

PROMPT_BASED_OBJECT_DETECTION_QUANTITY_MISMATCH_FEEDBACK_TEXT = "Expected to extract {expected_quantity} object(s) with prompt '{prompt}', but found {detected_quantity} object(s)."


class Mic2ePromptingStrategy(OtcPromptingStrategy):
    def __init__(self) -> None:
        super().__init__()

    def create_feedback_text(self, feedback: Feedback) -> str:
        feedback_type = feedback.type
        details = feedback.details

        if feedback_type == "prompt_based_object_detection_quantity_mismatch":
            return PROMPT_BASED_OBJECT_DETECTION_QUANTITY_MISMATCH_FEEDBACK_TEXT.format(
                prompt=details.get("prompt"),
                expected_quantity=details.get("expected_quantity"),
                detected_quantity=details.get("detected_quantity"),
            )

        return super().create_feedback_text(feedback)
