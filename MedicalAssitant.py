
import google.generativeai as genai
import sqlite3
from typing import List, Dict, Optional

class MedicalAssistantAgent:
    """
    AI Medical Assistant Agent with long-term memory using Gemini 2.5 Flash
    Stores patient interactions and history in SQLite database
    """
    
    def __init__(self, api_key: str, db_path: str = "medical_assistant.db"):
        """
        Initialize the Medical Assistant Agent
        
        Args:
            api_key: Google AI API key for Gemini
            db_path: Path to SQLite database file
        """
        # Configure Gemini API
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Database setup
        self.db_path = db_path
        self.init_database()
        
        # System instructions
        self.system_instructions = """You are a medical assistant working with doctors to help diagnose and monitor patients.

Your responsibilities:
- Analyze patient symptoms and provide differential diagnoses
- Track patient history across conversations
- Provide clinical insights based on reported symptoms
- Monitor symptom progression over time
- Reference past patient visits when relevant

Important constraints:
- You CANNOT prescribe medications
- You CANNOT specify which tests to conduct
- You CANNOT provide definitive diagnoses (only differential considerations)
- Always format output using clear bullet points and sections
- Always consider patient history when available

When analyzing symptoms:
1. Summarize the patient's current presentation
2. List relevant general medical information
3. Provide differential considerations with reasoning
4. Suggest areas for further clinical evaluation
5. Reference any relevant past visits or symptom changes"""
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Patients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                name TEXT,
                age INTEGER,
                gender TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT,
                session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                chief_complaint TEXT,
                summary TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id)
            )
        """)
        
        # Patient history/symptoms table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patient_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT,
                conversation_id INTEGER,
                symptoms TEXT,
                diagnoses_considered TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
                FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def register_patient(self, patient_id: str, name: str, age: int, gender: str):
        """Register a new patient in the system"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO patients (patient_id, name, age, gender)
                VALUES (?, ?, ?, ?)
            """, (patient_id, name, age, gender))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Patient already exists
            return False
        finally:
            conn.close()
    
    def get_patient_info(self, patient_id: str) -> Optional[Dict]:
        """Retrieve patient information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT patient_id, name, age, gender, created_at
            FROM patients WHERE patient_id = ?
        """, (patient_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "patient_id": result[0],
                "name": result[1],
                "age": result[2],
                "gender": result[3],
                "created_at": result[4]
            }
        return None
    
    def get_all_patients(self) -> List[Dict]:
        """Get list of all patients"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT patient_id, name, age, gender
            FROM patients
            ORDER BY name
        """)
        
        patients = []
        for row in cursor.fetchall():
            patients.append({
                "patient_id": row[0],
                "name": row[1],
                "age": row[2],
                "gender": row[3]
            })
        
        conn.close()
        return patients
    
    def get_patient_history(self, patient_id: str, limit: int = 5) -> List[Dict]:
        """Retrieve patient's previous visits and symptoms"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                c.session_date,
                c.chief_complaint,
                c.summary,
                ph.symptoms,
                ph.diagnoses_considered
            FROM conversations c
            LEFT JOIN patient_history ph ON c.conversation_id = ph.conversation_id
            WHERE c.patient_id = ?
            ORDER BY c.session_date ASC
            LIMIT ?
        """, (patient_id, limit))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                "session_date": row[0],
                "chief_complaint": row[1],
                "summary": row[2],
                "symptoms": row[3],
                "diagnoses_considered": row[4]
            })
        
        conn.close()
        return history
    
    def create_conversation(self, patient_id: str, chief_complaint: str) -> int:
        """Create a new conversation session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conversations (patient_id, chief_complaint)
            VALUES (?, ?)
        """, (patient_id, chief_complaint))
        
        conversation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return conversation_id
    
    def save_message(self, conversation_id: int, role: str, content: str):
        """Save a message to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO messages (conversation_id, role, content)
            VALUES (?, ?, ?)
        """, (conversation_id, role, content))
        
        conn.commit()
        conn.close()
    
    def build_context_prompt(self, patient_id: str, current_message: str) -> str:
        """Build a context-aware prompt with patient history"""
        patient_info = self.get_patient_info(patient_id)
        patient_history = self.get_patient_history(patient_id)
        
        context = f"{self.system_instructions}\n\n"
        context += "=== PATIENT INFORMATION ===\n"
        
        if patient_info:
            context += f"Patient ID: {patient_info['patient_id']}\n"
            context += f"Name: {patient_info['name']}\n"
            context += f"Age: {patient_info['age']}\n"
            context += f"Gender: {patient_info['gender']}\n\n"
        
        if patient_history:
            context += "=== PREVIOUS VISITS ===\n"
            for i, visit in enumerate(patient_history, 1):
                context += f"\nVisit {i} ({visit['session_date']}):\n"
                context += f"Chief Complaint: {visit['chief_complaint']}\n"
                if visit['symptoms']:
                    context += f"Symptoms: {visit['symptoms']}\n"
                if visit['diagnoses_considered']:
                    context += f"Differential Diagnoses: {visit['diagnoses_considered']}\n"
                if visit['summary']:
                    context += f"Summary: {visit['summary']}\n"
        else:
            context += "=== PREVIOUS VISITS ===\n"
            context += "This is the patient's first visit.\n"
        
        context += f"\n=== CURRENT CONSULTATION ===\n"
        context += f"Doctor/User Query: {current_message}\n\n"
        context += "Please provide your analysis following the structured format outlined in your responsibilities."
        
        return context
    
    def chat(self, patient_id: str, conversation_id: int, user_message: str) -> str:
        """
        Process a chat message with context from patient history
        
        Args:
            patient_id: Patient identifier
            conversation_id: Current conversation session ID
            user_message: Message from the doctor/user
            
        Returns:
            AI assistant response
        """
        # Build context-aware prompt
        full_prompt = self.build_context_prompt(patient_id, user_message)
        
        # Save user message
        self.save_message(conversation_id, "user", user_message)
        
        # Get AI response
        response = self.model.generate_content(full_prompt)
        ai_response = response.text
        
        # Save AI response
        self.save_message(conversation_id, "assistant", ai_response)
        
        return ai_response
    
    def end_conversation(self, conversation_id: int, summary: str, 
                        symptoms: str, diagnoses: str):
        """
        End a conversation and save summary to patient history
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update conversation with summary
        cursor.execute("""
            UPDATE conversations
            SET summary = ?
            WHERE conversation_id = ?
        """, (summary, conversation_id))
        
        # Get patient_id for this conversation
        cursor.execute("""
            SELECT patient_id FROM conversations
            WHERE conversation_id = ?
        """, (conversation_id,))
        
        patient_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        
        # Save to patient history
        self.save_patient_history_entry(patient_id, conversation_id, 
                                       symptoms, diagnoses)
    
    def save_patient_history_entry(self, patient_id: str, conversation_id: int, 
                                   symptoms: str, diagnoses_considered: str):
        """Save a patient history entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO patient_history 
            (patient_id, conversation_id, symptoms, diagnoses_considered)
            VALUES (?, ?, ?, ?)
        """, (patient_id, conversation_id, symptoms, diagnoses_considered))
        
        conn.commit()
        conn.close()

    def generate_consultation_summary(self, conversation_id: int) -> Dict[str, str]:
        """
        Generate automated summary, symptoms, and diagnoses from conversation
        
        Returns:
            Dict with 'summary', 'symptoms', and 'diagnoses' keys
        """
        # Get all messages from the conversation
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
        """, (conversation_id,))
        
        messages = cursor.fetchall()
        
        # Get patient_id and chief_complaint
        cursor.execute("""
            SELECT patient_id, chief_complaint
            FROM conversations
            WHERE conversation_id = ?
        """, (conversation_id,))
        
        result = cursor.fetchone()
        patient_id = result[0]
        chief_complaint = result[1]
        
        conn.close()
        
        # Build conversation transcript
        transcript = f"Chief Complaint: {chief_complaint}\n\n"
        transcript += "Conversation:\n"
        for role, content in messages:
            transcript += f"{role.upper()}: {content}\n\n"
        
        # Create summarization prompt
        summary_prompt = f"""Based on the following medical consultation, provide a structured summary:

    {transcript}

    Please extract and format the following in a concise manner:

    1. CONSULTATION SUMMARY (2-3 sentences summarizing the entire consultation)
    2. KEY SYMPTOMS (comma-separated list of main symptoms discussed)
    3. DIFFERENTIAL DIAGNOSES (comma-separated list of conditions considered)

    Format your response EXACTLY as follows:
    SUMMARY: [your summary here]
    SYMPTOMS: [symptom1, symptom2, symptom3]
    DIAGNOSES: [diagnosis1, diagnosis2, diagnosis3]
    """
        
        # Get AI summary
        try:
            response = self.model.generate_content(summary_prompt)
            summary_text = response.text
            
            # Parse the response
            summary = ""
            symptoms = ""
            diagnoses = ""
            
            lines = summary_text.strip().split('\n')
            for line in lines:
                if line.startswith('SUMMARY:'):
                    summary = line.replace('SUMMARY:', '').strip()
                elif line.startswith('SYMPTOMS:'):
                    symptoms = line.replace('SYMPTOMS:', '').strip()
                elif line.startswith('DIAGNOSES:'):
                    diagnoses = line.replace('DIAGNOSES:', '').strip()
            
            # Fallback if parsing fails
            if not summary:
                summary = "Consultation completed. See conversation history for details."
            if not symptoms:
                symptoms = chief_complaint
            if not diagnoses:
                diagnoses = "Under evaluation"
            
            return {
                'summary': summary,
                'symptoms': symptoms,
                'diagnoses': diagnoses
            }
            
        except Exception as e:
            # Fallback summary if AI fails
            return {
                'summary': f"Consultation regarding: {chief_complaint}",
                'symptoms': chief_complaint,
                'diagnoses': "Pending further evaluation"
            }
        
    def clear_all_data(self):
        """Clear all data from all tables (WARNING: Irreversible!)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Delete in order to respect foreign key constraints
            cursor.execute("DELETE FROM patient_history")
            cursor.execute("DELETE FROM messages")
            cursor.execute("DELETE FROM conversations")
            cursor.execute("DELETE FROM patients")
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()

    def clear_patient_data(self, patient_id: str):
        """Clear all data for a specific patient"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get all conversation IDs for this patient
            cursor.execute("SELECT conversation_id FROM conversations WHERE patient_id = ?", (patient_id,))
            conversation_ids = [row[0] for row in cursor.fetchall()]
            
            # Delete related data
            for conv_id in conversation_ids:
                cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
                cursor.execute("DELETE FROM patient_history WHERE conversation_id = ?", (conv_id,))
            
            cursor.execute("DELETE FROM conversations WHERE patient_id = ?", (patient_id,))
            cursor.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()