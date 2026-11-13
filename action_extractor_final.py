import spacy
import json

# Load the local NLP model
nlp = spacy.load("en_core_web_sm")

ACTION_KEYWORDS = ["will", "need to", "must", "supposed to", "deadline", "assigned", "complete by", "make sure"]
TEAM_NAMES = ["Deepak", "Akash", "Praveen", "Shanmuk", "Raunak", "Dilawar"]

def extract_tasks(transcript_data):
    """
    Robust task extractor that handles unexpected input formats from other modules.
    """
    # 1. FAILSAFE: Check if the input is empty or None
    if not transcript_data:
        return json.dumps([]) # Safely return an empty JSON array

    # 2. FAILSAFE: If the previous team passes a list of strings instead of a paragraph, join them
    if isinstance(transcript_data, list):
        transcript_data = " ".join([str(item) for item in transcript_data])
        
    # 3. FAILSAFE: Force the input into a string format just in case it's a weird object
    transcript_text = str(transcript_data)

    action_items = []
    
    # 4. FAILSAFE: Wrap the AI processing in a try-except block so it never crashes the main app
    try:
        doc = nlp(transcript_text)
        
        for sent in doc.sents:
            sentence_lower = sent.text.lower()
            
            if any(keyword in sentence_lower for keyword in ACTION_KEYWORDS):
                
                # Check if any team members are mentioned
                assignees = [name for name in TEAM_NAMES if name.lower() in sentence_lower]
                
                # If no team member, let AI find a person
                if not assignees:
                    assignees = [ent.text for ent in sent.ents if ent.label_ == "PERSON"]
                    
                # Extract deadlines
                deadlines = [ent.text for ent in sent.ents if ent.label_ in ["DATE", "TIME"]]
                
                action_items.append({
                    "task_description": sent.text.strip(),
                    "assignee": assignees[0] if assignees else "Unassigned",
                    "deadline": deadlines[0] if deadlines else "Not specified"
                })
                
    except Exception as e:
        # If something breaks inside spaCy, print the error to the terminal but keep running
        print(f"[Warning] Extraction error: {e}")
        
    # Always return a valid JSON format so Raunak's frontend never crashes
    return json.dumps(action_items, indent=4)

# --- MOCK TESTING ---
if __name__ == "__main__":
    print("Testing with a normal string...")
    print(extract_tasks("Deepak will fix the backend by tonight."))
    
    print("\nTesting with a weird list format (in case Akash sends this)...")
    print(extract_tasks(["Sentence one.", "Raunak needs to build the UI on Friday."]))
    
    print("\nTesting with empty data (in case the meeting had no talking)...")
    print(extract_tasks(""))