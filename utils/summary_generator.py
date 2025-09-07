"""
Sally 3.0 - Weekly Summary Generator
Creates beautiful, actionable weekly summaries for busy families

EDUCATIONAL CONCEPTS:
- Data Aggregation: Combining multiple data sources into insights
- Template Generation: Creating consistent, professional reports
- Family Communication: Presenting technical analysis in family-friendly format
- HTML Email: Professional formatting for email delivery
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict, Counter

class SummaryGenerator:
    """
    Generates weekly family communication summaries
    Transforms technical email analysis into actionable family insights
    """
    
    def __init__(self, config_manager, gmail_connector):
        self.config = config_manager
        self.gmail = gmail_connector
        
        print("📊 SummaryGenerator initialized")
    
    def generate_weekly_summary(self, days_back=7) -> Dict:
        """
        Generate comprehensive weekly summary of school communications
        Returns structured data that can be formatted as email or report
        """
        
        print(f"📈 Generating weekly summary for last {days_back} days...")
        
        # Get week's emails from Gmail
        from ai_analyzer import AIAnalyzer
        analyzer = AIAnalyzer(self.config)
        
        # Fetch and analyze week's emails
        print("   📧 Fetching school emails...")
        weekly_emails = self.gmail.get_school_emails(days_back=days_back, max_results=50)
        
        if not weekly_emails:
            print("   📭 No emails found for this period")
            return self._create_empty_summary()
        
        print(f"   🧠 Analyzing {len(weekly_emails)} emails...")
        analyzed_emails = analyzer.analyze_email_batch(weekly_emails)
        
        # Generate summary statistics
        summary_data = self._create_summary_structure(analyzed_emails, days_back)
        
        print("   📊 Generating insights and recommendations...")
        summary_data['insights'] = self._generate_insights(analyzed_emails)
        summary_data['action_items'] = self._extract_action_items(analyzed_emails)
        summary_data['upcoming_events'] = self._identify_upcoming_events(analyzed_emails)
        
        print("✅ Weekly summary generation complete!")
        return summary_data
    
    def _create_summary_structure(self, emails: List[Dict], days_back: int) -> Dict:
        """
        Create the basic summary data structure
        """
        
        # Group emails by student
        student_emails = defaultdict(list)
        general_emails = []
        
        for email in emails:
            student = email.get('student_association', 'All Students')
            if student == 'All Students':
                general_emails.append(email)
            else:
                # Handle multiple students (comma-separated)
                students = [s.strip() for s in student.split(',')]
                for s in students:
                    student_emails[s].append(email)
        
        # Count by categories and urgency
        category_counts = Counter(email.get('category', 'Unknown') for email in emails)
        urgency_counts = self._categorize_urgency_counts(emails)
        
        # Create summary structure
        summary = {
            'period': {
                'start_date': (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d'),
                'end_date': datetime.now().strftime('%Y-%m-%d'),
                'days': days_back
            },
            'overview': {
                'total_emails': len(emails),
                'by_category': dict(category_counts),
                'by_urgency': urgency_counts,
                'schools_contacted': len(set(email.get('sender', '').split('@')[-1] for email in emails))
            },
            'by_student': {},
            'general_communications': len(general_emails),
            'urgent_items': [email for email in emails if email.get('urgency_score', 0) >= 7.0],
            'generation_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Create per-student summaries
        for student_code, student_emails_list in student_emails.items():
            real_name = self.config.get_real_name(student_code)
            
            summary['by_student'][student_code] = {
                'student_name': real_name,
                'total_emails': len(student_emails_list),
                'by_category': dict(Counter(email.get('category', 'Unknown') for email in student_emails_list)),
                'urgent_count': sum(1 for email in student_emails_list if email.get('urgency_score', 0) >= 7.0),
                'recent_emails': [
                    {
                        'subject': email.get('subject', 'No Subject')[:60] + '...' if len(email.get('subject', '')) > 60 else email.get('subject', 'No Subject'),
                        'category': email.get('category', 'Unknown'),
                        'urgency': email.get('urgency_score', 0),
                        'date': email.get('timestamp', datetime.now()).strftime('%m/%d') if email.get('timestamp') else 'Unknown',
                        'summary': email.get('summary', '')[:100] + '...' if len(email.get('summary', '')) > 100 else email.get('summary', '')
                    }
                    for email in sorted(student_emails_list, key=lambda x: x.get('urgency_score', 0), reverse=True)[:5]
                ]
            }
        
        return summary
    
    def _categorize_urgency_counts(self, emails: List[Dict]) -> Dict[str, int]:
        """
        Categorize emails by urgency levels for summary
        """
        counts = {'Low (0-3)': 0, 'Medium (4-7)': 0, 'High (8-10)': 0}
        
        for email in emails:
            urgency = email.get('urgency_score', 0)
            if urgency <= 3:
                counts['Low (0-3)'] += 1
            elif urgency <= 7:
                counts['Medium (4-7)'] += 1
            else:
                counts['High (8-10)'] += 1
        
        return counts
    
    def _generate_insights(self, emails: List[Dict]) -> List[str]:
        """
        Generate AI-powered insights from the week's communications
        """
        insights = []
        
        # Communication volume insight
        if len(emails) > 20:
            insights.append(f"📈 High communication week with {len(emails)} emails - consider prioritizing urgent items")
        elif len(emails) < 5:
            insights.append("📉 Quiet communication week - good time to catch up on any pending items")
        
        # Category distribution insights
        categories = Counter(email.get('category', 'Unknown') for email in emails)
        most_common = categories.most_common(1)
        if most_common:
            category, count = most_common[0]
            if count > len(emails) * 0.5:
                insights.append(f"🎯 {category} communications dominated this week ({count}/{len(emails)} emails)")
        
        # Urgency pattern insights
        urgent_count = sum(1 for email in emails if email.get('urgency_score', 0) >= 7.0)
        if urgent_count > 3:
            insights.append(f"🚨 Multiple urgent items this week ({urgent_count}) - may need immediate family discussion")
        elif urgent_count == 0:
            insights.append("✅ No urgent communications this week - good opportunity for planning ahead")
        
        # Financial communications insight
        financial_count = sum(1 for email in emails if email.get('category') == 'Financial')
        if financial_count > 2:
            insights.append(f"💰 Multiple financial communications ({financial_count}) - review payment deadlines")
        
        return insights
    
    def _extract_action_items(self, emails: List[Dict]) -> List[Dict]:
        """
        Extract actionable items that require parent response
        """
        action_items = []
        
        # High urgency emails are automatic action items
        for email in emails:
            if email.get('urgency_score', 0) >= 7.0:
                action_items.append({
                    'priority': 'High',
                    'subject': email.get('subject', 'No Subject'),
                    'category': email.get('category', 'Unknown'),
                    'student': self.config.get_real_name(email.get('student_association', 'All Students')),
                    'summary': email.get('summary', '')[:100] + '...' if len(email.get('summary', '')) > 100 else email.get('summary', ''),
                    'urgency_score': email.get('urgency_score', 0)
                })
        
        # Medium urgency items that mention specific actions
        action_keywords = ['respond', 'reply', 'sign', 'return', 'submit', 'pay', 'attend', 'confirm']
        for email in emails:
            if 4 <= email.get('urgency_score', 0) < 7:
                subject_lower = email.get('subject', '').lower()
                summary_lower = email.get('summary', '').lower()
                
                if any(keyword in subject_lower or keyword in summary_lower for keyword in action_keywords):
                    action_items.append({
                        'priority': 'Medium',
                        'subject': email.get('subject', 'No Subject'),
                        'category': email.get('category', 'Unknown'),
                        'student': self.config.get_real_name(email.get('student_association', 'All Students')),
                        'summary': email.get('summary', '')[:100] + '...' if len(email.get('summary', '')) > 100 else email.get('summary', ''),
                        'urgency_score': email.get('urgency_score', 0)
                    })
        
        # Sort by urgency score (highest first)
        action_items.sort(key=lambda x: x['urgency_score'], reverse=True)
        
        return action_items[:10]  # Limit to top 10 action items
    
    def _identify_upcoming_events(self, emails: List[Dict]) -> List[Dict]:
        """
        Identify upcoming events and important dates from email content
        """
        events = []
        
        # Look for calendar-related emails
        calendar_emails = [email for email in emails if email.get('category') == 'Calendar']
        
        for email in calendar_emails:
            # Extract dates from key_information if available
            key_info = email.get('key_information', {})
            dates = key_info.get('dates', []) if isinstance(key_info, dict) else []
            
            if dates:
                events.append({
                    'subject': email.get('subject', 'No Subject'),
                    'student': self.config.get_real_name(email.get('student_association', 'All Students')),
                    'dates': dates[:3],  # Limit to first 3 dates
                    'category': email.get('category', 'Calendar'),
                    'summary': email.get('summary', '')[:80] + '...' if len(email.get('summary', '')) > 80 else email.get('summary', '')
                })
        
        return events[:8]  # Limit to 8 upcoming events
    
    def _create_empty_summary(self) -> Dict:
        """
        Create summary structure when no emails found
        """
        return {
            'period': {
                'start_date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'end_date': datetime.now().strftime('%Y-%m-%d'),
                'days': 7
            },
            'overview': {
                'total_emails': 0,
                'by_category': {},
                'by_urgency': {'Low (0-3)': 0, 'Medium (4-7)': 0, 'High (8-10)': 0},
                'schools_contacted': 0
            },
            'by_student': {},
            'general_communications': 0,
            'urgent_items': [],
            'insights': ['📭 No school communications this week - enjoy the quiet time!'],
            'action_items': [],
            'upcoming_events': [],
            'generation_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    
    def format_as_html_email(self, summary_data: Dict) -> str:
        """
        Convert summary data to beautiful HTML email format
        Family-friendly, mobile-responsive design
        """
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sally 3.0 - Weekly Family Summary</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .content {{ padding: 30px; }}
        .overview {{ background: #f8f9fa; padding: 20px; border-radius: 6px; margin-bottom: 30px; }}
        .stats {{ display: flex; justify-content: space-around; text-align: center; }}
        .stat {{ flex: 1; }}
        .stat-number {{ font-size: 24px; font-weight: bold; color: #667eea; }}
        .stat-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        .student-card {{ background: #fff; border: 1px solid #e0e0e0; border-radius: 6px; padding: 20px; margin-bottom: 20px; }}
        .student-name {{ font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px; }}
        .email-item {{ background: #f8f9fa; padding: 12px; border-left: 4px solid #667eea; margin-bottom: 10px; }}
        .urgent {{ border-left-color: #dc3545 !important; }}
        .medium {{ border-left-color: #ffc107 !important; }}
        .action-item {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 6px; margin-bottom: 15px; }}
        .action-priority-high {{ background: #f8d7da; border-color: #f5c6cb; }}
        .insight {{ background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin-bottom: 15px; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; background: #f8f9fa; }}
        @media (max-width: 480px) {{ .stats {{ flex-direction: column; }} .stat {{ margin-bottom: 15px; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Sally 3.0 Weekly Report</h1>
            <p>Your AI School Communication Summary</p>
            <p>{summary_data['period']['start_date']} to {summary_data['period']['end_date']}</p>
        </div>
        
        <div class="content">
            <!-- Overview Section -->
            <div class="overview">
                <div class="stats">
                    <div class="stat">
                        <div class="stat-number">{summary_data['overview']['total_emails']}</div>
                        <div class="stat-label">Total Emails</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{len(summary_data['urgent_items'])}</div>
                        <div class="stat-label">Urgent Items</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{len(summary_data['action_items'])}</div>
                        <div class="stat-label">Action Items</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{summary_data['overview']['schools_contacted']}</div>
                        <div class="stat-label">Schools</div>
                    </div>
                </div>
            </div>
"""
        
        # Add insights section
        if summary_data.get('insights'):
            html += """
            <div class="section">
                <h2>💡 This Week's Insights</h2>
"""
            for insight in summary_data['insights']:
                html += f'<div class="insight">{insight}</div>'
            html += "</div>"
        
        # Add urgent items section
        if summary_data['urgent_items']:
            html += """
            <div class="section">
                <h2>🚨 Urgent Items Requiring Attention</h2>
"""
            for item in summary_data['urgent_items']:
                html += f"""
                <div class="email-item urgent">
                    <strong>{item.get('subject', 'No Subject')}</strong><br>
                    <small>Category: {item.get('category', 'Unknown')} | Urgency: {item.get('urgency_score', 0):.1f}/10</small><br>
                    {item.get('summary', '')[:150] + '...' if len(item.get('summary', '')) > 150 else item.get('summary', '')}
                </div>
"""
            html += "</div>"
        
        # Add action items section
        if summary_data.get('action_items'):
            html += """
            <div class="section">
                <h2>📋 Action Items This Week</h2>
"""
            for item in summary_data['action_items']:
                priority_class = 'action-priority-high' if item.get('priority') == 'High' else 'action-item'
                html += f"""
                <div class="{priority_class}">
                    <strong>{item.get('priority', 'Medium')} Priority:</strong> {item.get('subject', 'No Subject')}<br>
                    <small>Student: {item.get('student', 'All')} | Category: {item.get('category', 'Unknown')}</small><br>
                    {item.get('summary', '')[:120] + '...' if len(item.get('summary', '')) > 120 else item.get('summary', '')}
                </div>
"""
            html += "</div>"
        
        # Add per-student sections
        if summary_data.get('by_student'):
            html += '<div class="section"><h2>👨‍👩‍👧‍👦 By Student</h2>'
            
            for student_code, student_data in summary_data['by_student'].items():
                html += f"""
                <div class="student-card">
                    <div class="student-name">{student_data['student_name']}</div>
                    <p><strong>{student_data['total_emails']} emails</strong> | Categories: {', '.join(f"{k}: {v}" for k, v in student_data['by_category'].items())}</p>
"""
                
                # Add recent emails for this student
                for email in student_data.get('recent_emails', [])[:3]:  # Show top 3
                    urgency_class = 'urgent' if email.get('urgency', 0) >= 7 else 'medium' if email.get('urgency', 0) >= 4 else ''
                    html += f"""
                    <div class="email-item {urgency_class}">
                        <strong>{email.get('subject', 'No Subject')}</strong> <small>({email.get('date', 'Unknown')})</small><br>
                        <small>Category: {email.get('category', 'Unknown')} | Urgency: {email.get('urgency', 0):.1f}/10</small>
                    </div>
"""
                html += "</div>"
            html += "</div>"
        
        # Add upcoming events
        if summary_data.get('upcoming_events'):
            html += """
            <div class="section">
                <h2>📅 Upcoming Events & Important Dates</h2>
"""
            for event in summary_data['upcoming_events']:
                html += f"""
                <div class="email-item">
                    <strong>{event.get('subject', 'No Subject')}</strong><br>
                    <small>Student: {event.get('student', 'All')} | Dates: {', '.join(event.get('dates', []))}</small><br>
                    {event.get('summary', '')}
                </div>
"""
            html += "</div>"
        
        # Footer
        html += f"""
        </div>
        <div class="footer">
            <p>📊 Generated by Sally 3.0 on {summary_data['generation_timestamp']}</p>
            <p>🤖 Your AI School Communication Assistant</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html

    
    def send_weekly_summary_email(self, summary_data: Dict) -> bool:
        """
        Send formatted weekly summary to configured recipients
        """
        
        print("📤 Preparing to send weekly summary email...")
        
        # Get recipients for summary emails
        summary_recipients = [
            recipient for recipient in self.config.recipients.get('summary', [])
        ]
        
        if not summary_recipients:
            print("⚠️ No summary email recipients configured")
            return False
        
        # Generate HTML email
        html_content = self.format_as_html_email(summary_data)
        
        # Create subject line
        total_emails = summary_data['overview']['total_emails']
        urgent_count = len(summary_data['urgent_items'])
        
        if urgent_count > 0:
            subject = f"🚨 Sally 3.0 Weekly Summary: {total_emails} emails, {urgent_count} urgent"
        else:
            subject = f"📊 Sally 3.0 Weekly Summary: {total_emails} school emails"
        
        # Send to all recipients
        success_count = 0
        for recipient in summary_recipients:
            recipient_email = recipient.get('email') if isinstance(recipient, dict) else recipient
            
            try:
                if self.gmail.send_email(recipient_email, subject, html_content):
                    success_count += 1
                    print(f"   ✅ Sent to {recipient_email}")
                else:
                    print(f"   ❌ Failed to send to {recipient_email}")
            except Exception as e:
                print(f"   ❌ Error sending to {recipient_email}: {str(e)}")
        
        print(f"📧 Summary email sent to {success_count}/{len(summary_recipients)} recipients")
        return success_count > 0

    # Educational testing function
    if __name__ == "__main__":
        print("🧪 Testing SummaryGenerator independently...")
        
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
            print("📊 Testing weekly summary generation...")
            
            # Create summary generator
            summary_gen = SummaryGenerator(config, gmail)
            
            # Generate summary for last 7 days
            summary_data = summary_gen.generate_weekly_summary(days_back=7)
            
            # Display results
            print(f"\n📈 Weekly Summary Results:")
            print("=" * 50)
            print(f"Total emails: {summary_data['overview']['total_emails']}")
            print(f"Categories: {summary_data['overview']['by_category']}")
            print(f"Urgency distribution: {summary_data['overview']['by_urgency']}")
            print(f"Urgent items: {len(summary_data['urgent_items'])}")
            print(f"Action items: {len(summary_data['action_items'])}")
            print(f"Insights generated: {len(summary_data['insights'])}")
            
            # Show insights
            if summary_data['insights']:
                print(f"\n💡 This Week's Insights:")
                for insight in summary_data['insights']:
                    print(f"   • {insight}")
            
            # Test HTML generation
            print(f"\n📧 Testing HTML email generation...")
            html_email = summary_gen.format_as_html_email(summary_data)
            print(f"   ✅ HTML email generated ({len(html_email)} characters)")
            
            # Save HTML for preview
            with open('output/sample_weekly_summary.html', 'w', encoding='utf-8') as f:
                f.write(html_email)
            print(f"   💾 Sample HTML saved to output/sample_weekly_summary.html")
            
            print("\n🎉 Weekly Summary Generator test complete!")
            
        else:
            print("❌ Gmail connection failed - cannot test summary generation")

