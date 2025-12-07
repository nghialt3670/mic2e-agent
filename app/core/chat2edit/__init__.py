# Import custom feedback classes early to ensure they're registered in FeedbackUnion
# This must be imported before any module that uses FeedbackUnion
from app.core.chat2edit.mic2e_feedbacks import (
    PromptBasedObjectDetectionQuantityMismatchFeedback,
)

__all__ = [
    "PromptBasedObjectDetectionQuantityMismatchFeedback",
]
