class ContextBuilder:

    def __init__(self):
        pass

    # =====================================================
    # Build Context for Gemini
    # =====================================================

    def build(self, search_results):

        context = []

        context.append("=" * 80)
        context.append("OKAI ERP KNOWLEDGE BASE")
        context.append("=" * 80)
        context.append("")

        for result in search_results:

            topic = result["topic_data"]

            context.append("-" * 80)
            context.append(f"Similarity : {result['score']}")
            context.append(f"Module : {topic.get('module','')}")
            context.append(f"Topic : {topic.get('topic','')}")
            context.append("")

            # ------------------------------------------------
            # Summary
            # ------------------------------------------------

            summary = topic.get("summary")

            if summary:

                context.append("SUMMARY")
                context.append(summary)
                context.append("")

            # ------------------------------------------------
            # Navigation
            # ------------------------------------------------

            navigation = topic.get("navigation", [])

            if navigation:

                context.append("NAVIGATION")

                for item in navigation:
                    context.append(f"• {item}")

                context.append("")

            # ------------------------------------------------
            # Steps
            # ------------------------------------------------

            steps = topic.get("steps", [])

            if steps:

                context.append("STEPS")

                for i, step in enumerate(steps, start=1):
                    context.append(f"{i}. {step}")

                context.append("")

            # ------------------------------------------------
            # Business Rules
            # ------------------------------------------------

            rules = topic.get("business_rules", [])

            if rules:

                context.append("BUSINESS RULES")

                for rule in rules:
                    context.append(f"• {rule}")

                context.append("")

            # ------------------------------------------------
            # Important Notes
            # ------------------------------------------------

            notes = topic.get("important_notes", [])

            if notes:

                context.append("IMPORTANT NOTES")

                for note in notes:
                    context.append(f"• {note}")

                context.append("")

            # ------------------------------------------------
            # Keywords
            # ------------------------------------------------

            keywords = topic.get("keywords", [])

            if keywords:

                context.append("KEYWORDS")

                context.append(", ".join(keywords))

                context.append("")

            context.append("=" * 80)
            context.append("")

        return "\n".join(context)