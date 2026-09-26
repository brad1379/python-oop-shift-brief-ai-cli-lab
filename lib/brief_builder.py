class HandoffBriefBuilder:
    """Builds prompts and verifies output for shift handoff briefs."""

    REQUIRED_SECTIONS = (
        "Shift Summary:",
        "Open Issues:",
        "Action Items:",
        "Follow-Up Questions:",
        "Risk Notes:",
    )

    def build_brief_prompt(self, notes):
        """
        Build a prompt for creating a new shift handoff brief.

        Requirements:
        - Reject None, empty, or whitespace-only notes with ValueError.
        - Include the original shift notes in the prompt.
        - Include every required section label from REQUIRED_SECTIONS.
        - Tell the model not to invent unsupported details.
        - Tell the model to use "Unknown" when details are not provided.
        - Keep this domain-specific prompt logic in this builder class,
          not in the reusable AI client.
        """
        if not notes or not notes.strip():
            raise ValueError("Shift notes cannot be empty")

        sections = "\n".join(self.REQUIRED_SECTIONS)

        return (
            "You are helping a store manager write a shift handoff brief.\n"
            "Turn the shift notes below into a brief using exactly these section labels:\n"
            f"{sections}\n\n"
            "Only use information from the shift notes. Do not invent details.\n"
            'If a detail is not provided, write "Unknown".\n\n'
            f"Shift notes:\n{notes.strip()}"
        )

    def build_revision_prompt(self, feedback):
        """
        Build a prompt for revising the previous handoff brief.

        Requirements:
        - Reject None, empty, or whitespace-only feedback with ValueError.
        - Reference the previous brief or earlier conversation.
        - Include the manager's revision feedback.
        - Include every required section label from REQUIRED_SECTIONS.
        - Tell the model not to invent unsupported details.
        """
        if not feedback or not feedback.strip():
            raise ValueError("Revision feedback cannot be empty")

        sections = "\n".join(self.REQUIRED_SECTIONS)

        return (
            "Revise the previous shift handoff brief from earlier in this conversation.\n"
            f"Manager feedback:\n{feedback.strip()}\n\n"
            "Keep using exactly these section labels:\n"
            f"{sections}\n\n"
            "Only use information from the original shift notes and this feedback. "
            "Do not invent details."
        )

    def is_usable_brief(self, response_text):
        """
        Check whether the AI response includes the required handoff structure.

        Requirements:
        - Return False for None, empty, or whitespace-only responses.
        - Return True only when the response contains every required section label.
        - Return False if one or more required sections are missing.
        """
        if not response_text or not response_text.strip():
            return False

        return all(section in response_text for section in self.REQUIRED_SECTIONS)

    def format_brief(self, response_text):
        """
        Format a created handoff brief for display.

        Requirements:
        - Return a string.
        - Add a clear user-facing heading before the response text.
        - Preserve the AI response content.
        """
        return f"\nShift Handoff Brief\n{response_text}"

    def create_brief(self, ai_client, notes):
        """
        Create a new handoff brief.

        Requirements:
        - Build a prompt from the shift notes.
        - Send the prompt through ai_client.send().
        - Verify that the AI response includes the required sections.
        - Raise RuntimeError if the AI response is not usable.
        - Return a formatted user-facing brief.
        """
        prompt = self.build_brief_prompt(notes)
        response_text = ai_client.send(prompt)

        if not self.is_usable_brief(response_text):
            raise RuntimeError("AI response did not include required sections.")

        return self.format_brief(response_text)

    def revise_brief(self, ai_client, feedback):
        """
        Revise the previous handoff brief.

        Requirements:
        - Build a revision prompt from the feedback.
        - Send the prompt through ai_client.send().
        - Verify that the AI response includes the required sections.
        - Raise RuntimeError if the AI response is not usable.
        - Return a formatted user-facing revised brief.
        """
        prompt = self.build_revision_prompt(feedback)
        response_text = ai_client.send(prompt)

        if not self.is_usable_brief(response_text):
            raise RuntimeError("AI response did not include required sections.")

        return f"\nRevised Shift Handoff Brief\n{response_text}"

        pass