#!/usr/bin/env python3
"""
Sally 3.0 - Production Main Orchestrator
Coordinates email processing, AI analysis, and family communication
"""

import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# Add utils folder to Python path
sys.path.append('utils')

from config_manager import ConfigManager
from gmail_connector import GmailConnector
from ai_analyzer import AIAnalyzer
from summary_generator import SummaryGenerator

def setup_logging():
    """Configure logging for production monitoring"""
    log_path = Path("output/logs")
    log_path.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path / f"sally_{datetime.now().strftime('%Y%m%d')}.log"),
            logging.StreamHandler()
        ]
    )

def main():
    """Sally 3.0 Main Production Controller"""
    
    if len(sys.argv) < 2:
        show_help()
        return 0
    
    setup_logging()
    logger = logging.getLogger("Sally.Main")
    
    try:
        # Initialize core components
        config = ConfigManager()
        if not config.load_all_configs():
            logger.error("Configuration loading failed")
            return 1

        # Add to main.py after config.load_all_configs():
        print("DEBUG - Recipients loaded:", config.recipients)
        
        gmail = GmailConnector(config)
        if not gmail.authenticate():
            logger.error("Gmail authentication failed")
            return 1
        
        command = sys.argv[1].lower()
        
        if command == "process":
            return process_emails(config, gmail, logger)
        elif command == "summary":
            return generate_weekly_summary(config, gmail, logger)
        elif command == "urgent":
            return check_urgent_emails(config, gmail, logger)
        elif command == "index":
            return build_data_index(config, gmail, logger)
        elif command == "test-summary":
            return send_test_summary(config, gmail, logger)
        else:
            show_help()
            return 1
            
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return 1

def build_data_index(config, gmail, logger):
    """Build searchable index of all academic year emails (run once)"""
    logger.info("Building comprehensive data index...")
    
    from data_manager import DataManager
    
    data_manager = DataManager(config)
    analyzer = AIAnalyzer(config)
    
    # This does the expensive AI processing once
    stored_count = data_manager.bulk_process_and_store(gmail, analyzer)
    logger.info(f"Data index complete: {stored_count} emails processed and stored")
    
    return 0

def process_emails(config, gmail, logger):
    """Process and analyze new emails"""
    logger.info("Starting email processing...")
    
    # Get emails since academic year start
    analyzer = AIAnalyzer(config)
    
    # Calculate academic year start
    now = datetime.now()
    if now.month < 7:
        academic_start = datetime(now.year - 1, 7, 1)
    else:
        academic_start = datetime(now.year, 7, 1)
    
    days_since_start = (now - academic_start).days
    
    # Fetch and analyze emails
    emails = gmail.get_school_emails(days_back=days_since_start, max_results=100)
    if not emails:
        logger.info("No emails to process")
        return 0
    
    analyzed_emails = analyzer.analyze_email_batch(emails)
    
    # Check for urgent items
    urgent_emails = analyzer.get_urgent_emails(analyzed_emails)
    if urgent_emails:
        logger.warning(f"Found {len(urgent_emails)} urgent emails")
        # Send urgent alerts here if configured
    
    return 0

def generate_weekly_summary(config, gmail, logger):
    """Generate and send weekly family summary"""
    logger.info("Generating weekly summary...")
    
    summary_gen = SummaryGenerator(config, gmail)
    summary_data = summary_gen.generate_weekly_summary()
    
    # Send summary email if recipients configured
    if config.recipients.get('summary'):
        success = summary_gen.send_weekly_summary_email(summary_data)
        if success:
            logger.info("Weekly summary sent successfully")
        else:
            logger.error("Failed to send weekly summary")
    
    return 0

def check_urgent_emails(config, gmail, logger):
    """Quick check for urgent communications"""
    logger.info("Checking for urgent emails...")
    
    analyzer = AIAnalyzer(config)
    emails = gmail.get_school_emails(days_back=3, max_results=20)  # Last 3 days only
    
    if emails:
        analyzed_emails = analyzer.analyze_email_batch(emails)
        urgent_emails = analyzer.get_urgent_emails(analyzed_emails)
        
        if urgent_emails:
            print(f"Found {len(urgent_emails)} urgent communications:")
            for email in urgent_emails:
                print(f"  • {email['subject']} (Urgency: {email['urgency_score']:.1f}/10)")
        else:
            print("No urgent communications found")
    else:
        print("No recent emails found")
    
    return 0

def send_test_summary(config, gmail, logger):
    """Generate and send test summary immediately"""
    logger.info("Generating test summary...")
    
    summary_gen = SummaryGenerator(config, gmail)
    summary_data = summary_gen.generate_weekly_summary(days_back=7)  # Last week
    
    # Always try to send regardless of configuration
    success = summary_gen.send_weekly_summary_email(summary_data)
    
    if success:
        logger.info("Test summary sent successfully")
        print("Test summary email sent - check your inbox!")
    else:
        logger.error("Failed to send test summary")
        print("Failed to send test summary - check your email configuration")
    
    return 0

def show_help():
    """Display available commands"""
    help_text = """
Sally 3.0 - AI School Communication Assistant


COMMANDS:
  process    - Analyze all school emails from academic year start
  summary    - Generate and send weekly family summary  
  urgent     - Quick check for urgent communications
  index      - Build searchable database (run once)

EXAMPLES:
  py main.py process     # Analyze recent emails
  py main.py summary     # Send weekly report
  py main.py urgent      # Check urgent items only
  py main.py index       # Build email database

For automated scheduling, use 'process' and 'summary' commands.
    """
    print(help_text)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

   

