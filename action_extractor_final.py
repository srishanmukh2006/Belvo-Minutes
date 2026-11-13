import spacy
import json

# Load the local NLP model
nlp = spacy.load("en_core_web_sm")

ACTION_KEYWORDS = ["will", "need to", "must", "supposed to", "deadline", "assigned", "complete by", "make sure"]

# Smart hack for the MVP: Tell the script exactly who is on the Belvo team
TEAM_NAMES = ["Deepak", "Akash", "Praveen", "Shanmuk", "Raunak", "Dilawar"]

def extract_tasks(transcript_text):
    doc = nlp(transcript_text)
    action_items = []
    
    for sent in doc.sents:
        sentence_lower = sent.text.lower()
        
        if any(keyword in sentence_lower for keyword in ACTION_KEYWORDS):
            
            # 1. First, check if any of our team members are mentioned in the sentence
            assignees = [name for name in TEAM_NAMES if name.lower() in sentence_lower]
            
            # 2. If no team member is found, let the AI try to find a person's name
            if not assignees:
                assignees = [ent.text for ent in sent.ents if ent.label_ == "PERSON"]
                
            # 3. Extract deadlines
            deadlines = [ent.text for ent in sent.ents if ent.label_ in ["DATE", "TIME"]]
            
            action_items.append({
                "task_description": sent.text.strip(),
                "assignee": assignees[0] if assignees else "Unassigned",
                "deadline": deadlines[0] if deadlines else "Not specified"
            })
            
    return json.dumps(action_items, indent=4)

# Test with ANY text you want
mock_transcript = """
Alright, let's wrap up this meeting. Deepak will set up the SQL database by tomorrow morning. 
Raunak, you need to finish the dashboard UI on Friday. 
I think the summarisation model is working fine. 
Dilawar must complete the testing and documentation by 11 PM tonight.
Also, Shanmuk needs to push the extraction code to GitHub.
"""

if __name__ == "__main__":
    print("Processing transcript offline...\n")
    final_json = extract_tasks(mock_transcript)
    print("Extracted Action Items (JSON for Frontend):")
    print(final_json)