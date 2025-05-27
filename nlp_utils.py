def load_spacy_model(model_name="en_core_web_md"):
    """
    Load the spaCy model for NLP tasks.

    Args:
        model_name (str): The name of the spaCy model to load.

    Returns:
        nlp: Loaded spaCy model.
    """
    import spacy
    nlp = spacy.load(model_name)
    return nlp


def detect_intent(user_question, intent_docs, nlp, threshold=0.75):
    """
    Matches user question to the best intent using spaCy similarity.
    Returns intent name if similarity exceeds threshold; otherwise None.

    Args:
        user_question (str): The question asked by the user.
        intent_docs (dict): A dictionary of intents and their example documents.
        nlp: Loaded spaCy model.
        threshold (float): Similarity threshold for intent detection.

    Returns:
        str or None: The best matching intent or None if no match is found.
    """
    user_doc = nlp(user_question)
    best_intent = None
    best_score = 0.0

    for intent, examples in intent_docs.items():
        for example_doc in examples:
            score = user_doc.similarity(example_doc)
            if score > best_score:
                best_score = score
                best_intent = intent

    return best_intent if best_score >= threshold else None