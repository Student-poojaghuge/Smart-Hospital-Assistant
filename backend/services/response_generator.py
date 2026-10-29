def generate_medical_response(query, results):
    if not results:
        return (
            "I could not find enough relevant information in the medical "
            "knowledge base. Please consult a qualified healthcare professional."
        )

    topic = results[0]["topic"]

    response = f"### {topic.get('topic', 'Medical Information')}\n\n"

    if topic.get("description"):
        response += f"**Overview:** {topic['description']}\n\n"

    if topic.get("symptoms"):
        response += f"**Common Symptoms:** {topic['symptoms']}\n\n"

    if topic.get("risk_factors"):
        response += f"**Risk Factors:** {topic['risk_factors']}\n\n"

    if topic.get("prevention"):
        response += f"**Prevention:** {topic['prevention']}\n\n"

    if topic.get("when_to_see_doctor"):
        response += f"**When to See a Doctor:** {topic['when_to_see_doctor']}\n\n"

    response += (
        "⚠️ Medical Information Notice: This information is for educational "
        "purposes only. It is not a medical diagnosis or personalized "
        "prescription. Consult a qualified healthcare professional before "
        "making health-related decisions."
    )

    return response


def generate_emergency_response(query, results):
    if not results:
        return (
            "I could not find specific first-aid information for this query. "
            "If this is an emergency, contact local emergency services immediately."
        )

    topic = results[0]["topic"]

    response = f"### 🚨 {topic.get('topic_name', 'Emergency / First Aid')}\n\n"

    if topic.get("warning_signs"):
        response += f"**Warning Signs:** {topic['warning_signs']}\n\n"

    if topic.get("immediate_first_aid"):
        response += f"**Immediate First Aid:** {topic['immediate_first_aid']}\n\n"

    if topic.get("what_not_to_do"):
        response += f"**What Not To Do:** {topic['what_not_to_do']}\n\n"

    if topic.get("when_to_call_emergency"):
        response += (
            f"**When to Call Emergency Services:** "
            f"{topic['when_to_call_emergency']}\n\n"
        )

    if topic.get("hospital_care_needed"):
        response += (
            f"**Hospital Care:** {topic['hospital_care_needed']}\n\n"
        )

    if topic.get("source_name"):
        response += f"**Source:** {topic['source_name']}\n\n"

    if topic.get("last_reviewed"):
        response += f"**Last Reviewed:** {topic['last_reviewed']}\n\n"

    response += (
        "🚨 Emergency Notice: If you are experiencing severe symptoms or a "
        "medical emergency, contact local emergency services or visit the "
        "nearest hospital immediately. Do not rely only on this application."
    )

    return response