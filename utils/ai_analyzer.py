"""
Sally 3.0 - AI Email Analyzer
The brain that understands school emails and categorizes them intelligently

EDUCATIONAL CONCEPTS:
- Prompt Engineering: Crafting AI instructions for consistent results
- Multi-Agent AI: Different AI models for different tasks
- Privacy by Design: Name encoding before AI processing
- Structured Data Extraction: Converting unstructured emails to organized info
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any
import anthropic
from anthropic import Anthropic
import os
from dotenv import load_dotenv

# We'll add AI service imports after setting up API keys
# import anthropic  # Claude AI
# import openai     # GPT AI

class AIAnalyzer:
    """
    Analyzes school emails using AI to categorize, extract info, and detect urgency
    This is Sally's intelligence layer with educational psychology awareness
    """
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.ai_client = None
        
        # Email categories Sally understands
        self.categories = {
            'Academic': ['grades', 'homework', 'test', 'assignment', 'teacher', 'class', 'subject'],
            'Administrative': ['policy', 'form', 'registration', 'announcement', 'newsletter'],
            'Financial': ['fee', 'payment', 'invoice', 'fundraising', 'donation', 'cost', 'money'],
            'Behavioral': ['behavior', 'discipline', 'incident', 'counselor', 'meeting', 'principal'],
            'Calendar': ['event', 'schedule', 'date', 'time', 'holiday', 'break', 'trip'],
            'Urgent': ['urgent', 'immediate', 'ASAP', 'deadline', 'today', 'tomorrow', 'required']
        }
        
        # Educational Psychology Guidelines for AI Processing
        self.educational_principles = {
            'language_tone': 'supportive and solution-focused',
            'child_privacy': 'protect all identifying information',
            'family_respect': 'assume positive intent from all parties',
            'developmental_awareness': 'consider age-appropriate expectations',
            'collaborative_approach': 'frame as school-family partnership'
        }
        
        print("🧠 AI Analyzer initialized with educational psychology awareness")
    
    def get_educational_prompt_context(self) -> str:
        """
        Returns educational institution context for AI prompts
        Ensures child-friendly, supportive analysis
        """
        return """
EDUCATIONAL CONTEXT:
You are analyzing communications from educational institutions about children and teenagers. 
Please maintain these principles:

1. CHILD-CENTERED APPROACH:
   - Use supportive, non-judgmental language
   - Frame challenges as opportunities for growth
   - Respect developmental stages and individual differences

2. FAMILY-SCHOOL PARTNERSHIP:
   - Assume positive intent from teachers and administrators
   - Present information to facilitate collaboration
   - Emphasize shared goals of student success and wellbeing

3. PRIVACY & DIGNITY:
   - All student names are coded for privacy protection
   - Focus on constructive information for parents
   - Avoid language that could stigmatize or label children

4. DEVELOPMENTAL AWARENESS:
   - Recognize age-appropriate expectations for different grade levels
   - Consider social-emotional development alongside academics
   - Acknowledge that children develop at different paces

5. SOLUTION-ORIENTED:
   - When behavioral concerns arise, focus on support strategies
   - Present academic challenges as learning opportunities
   - Emphasize resources and next steps rather than problems

This analysis will help parents stay informed and engaged in their children's educational journey.
"""
    
 
    def setup_ai_client(self, api_key=None):
        """
        Initialize Claude AI client for intelligent email analysis
        """
        if not api_key:
            # Try to get from environment
            import os
            from dotenv import load_dotenv
            
            load_dotenv()  # Load .env file
            api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key:
            print("❌ No Anthropic API key found. Please add to .env file.")
            return False
        
        try:
            self.ai_client = Anthropic(api_key=api_key)
            self.ai_service = 'anthropic'
            
            print("🤖 Claude AI client initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Claude: {str(e)}")
            return False

    def analyze_with_ai(self, email_text: str, email_subject: str) -> Dict:
        """
        Use Claude AI for intelligent email analysis
        Designed for token efficiency while maintaining accuracy
        """
        if not self.ai_client:
            print("⚠️ AI client not initialized, using rule-based analysis")
            return self._fallback_analysis(email_text, email_subject)
        
        # Create token-efficient prompt
        educational_context = self.get_educational_prompt_context()
        
        # Concise, structured prompt for consistent results
        prompt = f"""{educational_context}

    EMAIL TO ANALYZE:
    Subject: {email_subject}
    Content: {email_text[:800]}...

    Please analyze this school communication and respond in this exact JSON format:
    {{
        "category": "Academic/Administrative/Financial/Behavioral/Calendar",
        "urgency_score": 0.0-10.0,
        "student_association": "Student_Alpha/Student_Beta/Student_Gamma/All Students",
        "key_dates": ["date1", "date2"],
        "action_required": true/false,
        "summary": "One sentence family-friendly summary",
        "reasoning": "Brief explanation of categorization"
    }}

    Focus on: supportive language, privacy protection, partnership mindset."""

        try:
            # Call Claude with minimal tokens
            response = self.ai_client.messages.create(
                model="claude-3-haiku-20240307",  # Most cost-effective model
                max_tokens=200,  # Keep response concise
                messages=[{
                    "role": "user", 
                    "content": prompt
                }]
            )
            
            # Parse JSON response
            import json
            ai_analysis = json.loads(response.content[0].text)
            
            print(f"   🤖 AI analysis complete (tokens used: ~{len(prompt.split())*1.3:.0f})")
            return ai_analysis
            
        except Exception as e:
            print(f"   ⚠️ AI analysis failed: {str(e)}, using fallback")
            return self._fallback_analysis(email_text, email_subject)

    def _fallback_analysis(self, email_text: str, email_subject: str) -> Dict:
        """
        Fallback to rule-based analysis if AI fails
        Ensures Sally always works, even without AI
        """
        full_text = f"{email_subject} {email_text}".lower()
        
        return {
            "category": self._categorize_email(full_text),
            "urgency_score": self._calculate_urgency(full_text, email_subject.lower()),
            "student_association": self._identify_student(full_text),
            "key_dates": [],
            "action_required": False,
            "summary": f"[Rule-based] {email_subject}",
            "reasoning": "Analyzed using keyword matching (AI unavailable)"
        }
            
            
            
    def analyze_email_batch(self, emails: List[Dict]) -> List[Dict]:
        """
        Analyze a batch of emails and return structured data
        This is Sally's main intelligence function
        """
        print(f"🧠 Analyzing {len(emails)} school emails...")
        
        analyzed_emails = []
        
        for i, email in enumerate(emails, 1):
            print(f"   📧 Processing email {i}/{len(emails)}: {email['subject'][:50]}...")
            
            # Analyze this email
            analysis = self.analyze_single_email(email)
            
            # Add analysis to the email data
            email_with_analysis = {**email, **analysis}
            analyzed_emails.append(email_with_analysis)
            
            print(f"      📊 Category: {analysis['category']}")
            print(f"      🚨 Urgency: {analysis['urgency_score']:.1f}/10")
            print(f"      👤 Student: {analysis['student_association']}")
        
        print(f"✅ Email analysis complete!")
        return analyzed_emails
    
    def analyze_single_email(self, email: Dict) -> Dict:
        """
        Analyze a single email using AI when available, rules as fallback
        """
        
        # Initialize AI if not already done
        if not hasattr(self, 'ai_client') or not self.ai_client:
            self.setup_ai_client()
        
        # Get email content for analysis
        subject = email.get('subject', '')
        body_text = email.get('body_text', '')
        snippet = email.get('snippet', '')
        
        # Try AI analysis first, fallback to rules if needed
        if hasattr(self, 'ai_client') and self.ai_client:
            try:
                # Use AI for intelligent analysis
                ai_result = self.analyze_with_ai(f"{body_text} {snippet}", subject)
                
                # Add additional metadata
                return {
                    **ai_result,
                    'timestamp': email.get('timestamp'),
                    'sender': email.get('sender', ''),
                    'analysis_timestamp': datetime.now(),
                    'privacy_encoded': True,
                    'processing_method': 'AI'
                }
            except Exception as e:
                print(f"   ⚠️ AI analysis failed: {str(e)}, using fallback")
        
        # Fallback: Rule-based analysis
        full_text = f"{subject} {body_text} {snippet}".lower()
        
        return {
            'category': self._categorize_email(full_text),
            'urgency_score': self._calculate_urgency(full_text, subject.lower()),
            'student_association': self._identify_student(full_text),
            'key_information': self._extract_key_info(full_text, email),
            'summary': self._generate_summary(email, self._categorize_email(full_text)),
            'analysis_timestamp': datetime.now(),
            'requires_action': self._calculate_urgency(full_text, subject.lower()) > 7.0,
            'privacy_encoded': True,
            'processing_method': 'Rules'
        }
    
    def _categorize_email(self, text: str) -> str:
        """
        Categorize email based on content keywords
        Returns the most likely category
        """
        
        category_scores = {}
        
        # Score each category based on keyword matches
        for category, keywords in self.categories.items():
            score = 0
            for keyword in keywords:
                # Count keyword occurrences (case insensitive)
                score += text.count(keyword.lower())
            
            category_scores[category] = score
        
        # Return category with highest score
        if category_scores and max(category_scores.values()) > 0:
            return max(category_scores, key=category_scores.get)
        else:
            return 'Administrative'  # Default category
    
    def _calculate_urgency(self, text: str, subject: str) -> float:
        """
        Calculate urgency score from 0-10 based on content
        Higher scores indicate more urgent communications
        """
        urgency_score = 0.0
        
        # High urgency indicators
        high_urgency_words = [
            'urgent', 'immediate', 'asap', 'emergency', 'important',
            'deadline', 'due today', 'due tomorrow', 'overdue',
            'suspended', 'incident', 'injury', 'medical', 'principal office'
        ]
        
        # Medium urgency indicators
        medium_urgency_words = [
            'payment due', 'meeting required', 'response needed',
            'please respond', 'action required', 'sign up',
            'permission slip', 'field trip'
        ]
        
        # Time-sensitive indicators
        time_indicators = [
            'today', 'tomorrow', 'this week', 'deadline',
            'expires', 'closes', 'ends'
        ]
        
        # Check for high urgency (8-10 points)
        for word in high_urgency_words:
            if word in text:
                urgency_score += 3.0
        
        # Check for medium urgency (4-6 points)  
        for word in medium_urgency_words:
            if word in text:
                urgency_score += 2.0
        
        # Check for time sensitivity (2-3 points)
        for word in time_indicators:
            if word in text:
                urgency_score += 1.5
        
        # Subject line emphasis (all caps = more urgent)
        if subject.isupper() and len(subject) > 5:
            urgency_score += 2.0
        
        # Exclamation marks indicate urgency
        urgency_score += min(text.count('!'), 3) * 0.5
        
        # Cap at 10.0
        return min(urgency_score, 10.0)
    
    def _identify_student(self, text: str) -> str:
        """
        Identify which student(s) this email relates to
        Uses privacy-safe coded names
        """
        
        # Check for student name mentions (using coded names for privacy)
        student_mentions = []
        
        for real_name, info in self.config.students.items():
            coded_name = info['coded_name']
            
            # Look for real name in email (convert to coded name)
            if real_name.lower() in text:
                student_mentions.append(coded_name)
            
            # Also check for grade-level mentions
            grade = info.get('grade', '').lower()
            if grade in text:
                student_mentions.append(coded_name)
        
        if student_mentions:
            # Remove duplicates and return
            return ', '.join(list(set(student_mentions)))
        else:
            return 'All Students'  # General school communication
    
    def _extract_key_info(self, text: str, email: Dict) -> Dict:
        """
        Extract structured information from email content
        Dates, amounts, deadlines, etc.
        """
        
        key_info = {
            'dates': [],
            'amounts': [],
            'deadlines': [],
            'action_items': [],
            'contacts': []
        }
        
        # Extract dates (simple patterns)
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # MM-DD-YYYY
            r'\b[A-Za-z]+ \d{1,2},? \d{4}\b'  # Month DD, YYYY
        ]
        
        for pattern in date_patterns:
            dates = re.findall(pattern, text)
            key_info['dates'].extend(dates)
        
        # Extract dollar amounts
        amount_pattern = r'\$\d+\.?\d*'
        amounts = re.findall(amount_pattern, text)
        key_info['amounts'] = amounts
        
        # Extract phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        key_info['contacts'] = phones
        
        # Extract action items (sentences with action words)
        action_words = ['please', 'must', 'need to', 'required to', 'should']
        sentences = text.split('.')
        
        for sentence in sentences:
            for action_word in action_words:
                if action_word in sentence.lower():
                    key_info['action_items'].append(sentence.strip())
                    break
        
        # Clean up data
        key_info['dates'] = list(set(key_info['dates']))[:5]  # Limit to 5 dates
        key_info['amounts'] = list(set(key_info['amounts']))[:3]  # Limit to 3 amounts
        key_info['action_items'] = key_info['action_items'][:3]  # Limit to 3 actions
        
        return key_info
    
    def _generate_summary(self, email: Dict, category: str) -> str:
        """
        Generate a concise, family-friendly summary of the email
        Uses educational psychology principles for supportive language
        """
        
        subject = email.get('subject', 'No Subject')
        snippet = email.get('snippet', '')
        sender = email.get('sender', '').split('<')[0].strip()  # Extract name from "Name <email>"
        
        # Apply educational lens to summary generation
        summary = f"[{category}] {sender}: "
        
        # Use supportive language based on category
        if category == 'Behavioral':
            # Frame behavioral communications positively
            if any(word in subject.lower() for word in ['incident', 'behavior', 'discipline']):
                summary += f"Partnership opportunity regarding {subject.replace('Incident', 'situation').replace('INCIDENT', 'situation')}"
            else:
                summary += subject
        elif category == 'Academic':
            # Frame academic communications constructively
            if any(word in subject.lower() for word in ['failing', 'poor', 'low']):
                summary += f"Academic support opportunity: {subject.replace('failing', 'needs support in').replace('poor', 'developing in')}"
            else:
                summary += subject
        else:
            # Standard summary for other categories
            summary += subject
        
        # Add educational context to snippet
        if snippet and len(snippet) > 20:
            # Clean snippet of potentially harsh language
            educational_snippet = snippet
            
            # Replace potentially concerning terms with supportive alternatives
            replacements = {
                'failing': 'needs support',
                'poor behavior': 'behavioral growth opportunity',
                'discipline': 'guidance',
                'problem': 'area for development',
                'concerning': 'worth discussing'
            }
            
            for harsh_term, supportive_term in replacements.items():
                educational_snippet = educational_snippet.replace(harsh_term, supportive_term)
            
            # Add snippet preview (first 100 characters)
            preview = educational_snippet[:100] + "..." if len(educational_snippet) > 100 else educational_snippet
            summary += f" | {preview}"
        
        return summary
    
    def get_urgent_emails(self, analyzed_emails: List[Dict], threshold: float = 7.0) -> List[Dict]:
        """
        Filter emails that require immediate attention
        """
        urgent_emails = [
            email for email in analyzed_emails 
            if email.get('urgency_score', 0) >= threshold
        ]
        
        print(f"🚨 Found {len(urgent_emails)} urgent emails (threshold: {threshold})")
        return urgent_emails
    
    def generate_category_summary(self, analyzed_emails: List[Dict]) -> Dict:
        """
        Generate summary statistics by category
        """
        
        category_counts = {}
        urgency_distribution = {'Low (0-3)': 0, 'Medium (4-7)': 0, 'High (8-10)': 0}
        
        for email in analyzed_emails:
            # Count by category
            category = email.get('category', 'Unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # Count by urgency level
            urgency = email.get('urgency_score', 0)
            if urgency <= 3:
                urgency_distribution['Low (0-3)'] += 1
            elif urgency <= 7:
                urgency_distribution['Medium (4-7)'] += 1
            else:
                urgency_distribution['High (8-10)'] += 1
        
        return {
            'total_emails': len(analyzed_emails),
            'by_category': category_counts,
            'by_urgency': urgency_distribution,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }

# Educational testing function
if __name__ == "__main__":
    print("🧪 Testing AI Analyzer independently...")
    
    # Import required modules
    import sys
    sys.path.append('.')
    from config_manager import ConfigManager
    from gmail_connector import GmailConnector
    
    # Initialize components
    config = ConfigManager()
    config.load_all_configs()
    
    gmail = GmailConnector(config)
    
    if gmail.authenticate() and gmail.test_connection():
        print("📧 Fetching recent emails for AI analysis...")
        
        # Get recent school emails
        emails = gmail.get_school_emails(days_back=1, max_results=5)
        
        if emails:
            # Analyze with AI
            analyzer = AIAnalyzer(config)
            analyzed_emails = analyzer.analyze_email_batch(emails)
            
            # Show results
            print(f"\n📊 Analysis Summary:")
            print("=" * 50)
            
            summary_stats = analyzer.generate_category_summary(analyzed_emails)
            print(f"Total emails analyzed: {summary_stats['total_emails']}")
            print(f"Categories found: {summary_stats['by_category']}")
            print(f"Urgency distribution: {summary_stats['by_urgency']}")
            
            # Show urgent emails
            urgent = analyzer.get_urgent_emails(analyzed_emails)
            if urgent:
                print(f"\n🚨 URGENT EMAILS REQUIRING ATTENTION:")
                for email in urgent:
                    print(f"   • {email['summary']}")
                    print(f"     Urgency: {email['urgency_score']:.1f}/10")
            
            print("\n🎉 AI Analysis complete!")
        else:
            print("📭 No recent school emails found for analysis")
    else:
        print("❌ Gmail connection failed")
