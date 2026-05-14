import re

class SHLGuardrails:
    def __init__(self):
        self.blocked_keywords = [
            "ignore previous instructions",
            "system prompt",
            "legal advice",
            "hiring policy",
            "netflix",
            "subscription",
            "hack",
            "exploit"
        ]

    def check_input(self, text):
        """
        Returns (is_safe, refusal_message)
        """
        text_lower = text.lower()
        
        # Simple keyword check
        for keyword in self.blocked_keywords:
            if keyword in text_lower:
                return False, f"I'm sorry, I can only assist with SHL assessments. I cannot provide information on '{keyword}'."

        # Check for prompt injection patterns
        if re.search(r"(ignore|disregard|forget).*(instruction|prompt|rule)", text_lower):
            return False, "I'm sorry, but I must follow my safety and topical guidelines."

        return True, None

    def is_on_topic(self, text):
        topic_keywords = ["hiring", "assessment", "test", "recruit", "candidate", "role", "skill", "shl", "opq", "verify"]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in topic_keywords)
