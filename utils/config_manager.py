"""
Sally 3.0 - Configuration Manager
Reads settings from text files (keeping code separate from configuration)

EDUCATIONAL CONCEPTS:
- Configuration Management: Settings live in text files, not code
- File I/O: Reading and parsing text files in Python
- Error Handling: What to do when files are missing or malformed
- Privacy Protection: Managing student name encoding
"""

import os
from pathlib import Path

class ConfigManager:
    """
    Manages all Sally's configuration files
    This is like Sally's memory of your preferences and settings
    """
    
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        
        # Configuration storage - these will hold your settings
        self.schools = []           # List of school domains to monitor
        self.students = {}          # Student name → coded name mapping
        self.recipients = {}        # Email addresses for alerts/summaries
        self.urgent_keywords = []   # Words that indicate urgent emails
        
        print(f"🔧 ConfigManager initialized, reading from: {self.config_dir}")
    
    def load_schools(self):
        """
        Load school domains from schools.txt
        These are the email domains Sally will monitor
        """
        schools_file = self.config_dir / "schools.txt"
        
        if not schools_file.exists():
            print("❌ schools.txt not found! Please create it in the config folder.")
            return False
        
        self.schools = []
        print(f"📚 Reading school domains from {schools_file}")
        
        try:
            with open(schools_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments (lines starting with #)
                    if line and not line.startswith('#'):
                        self.schools.append(line.lower())
                        print(f"   ✅ Added school domain: {line}")
            
            if self.schools:
                print(f"🎯 Successfully loaded {len(self.schools)} school domains")
                return True
            else:
                print("⚠️ No school domains found in schools.txt")
                return False
                
        except Exception as e:
            print(f"❌ Error reading schools.txt: {str(e)}")
            return False
    
    def load_students(self):
        """
        Load student information and create privacy mapping
        Format: RealName|CodedName|Grade
        """
        students_file = self.config_dir / "students.txt"
        
        if not students_file.exists():
            print("❌ students.txt not found! Please create it in the config folder.")
            return False
        
        self.students = {}
        print(f"👨‍👩‍👧‍👦 Reading student information from {students_file}")
        
        try:
            with open(students_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        # Parse format: RealName|CodedName|Grade
                        parts = line.split('|')
                        
                        if len(parts) >= 2:
                            real_name = parts[0].strip()
                            coded_name = parts[1].strip()
                            grade = parts[2].strip() if len(parts) > 2 else "Unknown Grade"
                            
                            self.students[real_name] = {
                                'coded_name': coded_name,
                                'grade': grade
                            }
                            
                            print(f"   ✅ {real_name} → {coded_name} ({grade})")
                        else:
                            print(f"   ⚠️ Line {line_num} malformed: {line}")
            
            if self.students:
                print(f"🎯 Successfully loaded {len(self.students)} students")
                return True
            else:
                print("⚠️ No students found in students.txt")
                return False
                
        except Exception as e:
            print(f"❌ Error reading students.txt: {str(e)}")
            return False

    def load_all_configs(self):
        """
        Load all configuration files - main method for initialization
        """
        print("Loading all Sally configuration files...")
        
        school_success = self.load_schools()
        student_success = self.load_students()
        recipients_success = self.load_recipients()  # Add this line
        
        if school_success and student_success and recipients_success:
            print("All configuration loaded successfully!")
            return True
        else:
            print("Configuration loading failed")
            return False

    def get_coded_name(self, real_name):
        """
        Convert real student name to privacy-safe coded name
        This protects your children's privacy when using AI services
        """
        if real_name in self.students:
            return self.students[real_name]['coded_name']
        else:
            # Create a generic coded name if not found
            return f"Student_Unknown_{abs(hash(real_name)) % 1000}"
    
    def get_real_name(self, coded_name):
        """
        Convert coded name back to real name for family display
        """
        for real_name, info in self.students.items():
            if info['coded_name'] == coded_name:
                return real_name
        return coded_name  # Return as-is if not found

    def load_recipients(self):
        """Load email recipient configuration"""  
        recipients_file = self.config_dir / "recipients.txt"
        
        if not recipients_file.exists():
            print("recipients.txt not found. Please configure email recipients.")
            return False
        
        self.recipients = {'summary': [], 'urgent': []}
        with open(recipients_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Format: EmailType|EmailAddress|Name
                    parts = line.split('|')
                    if len(parts) >= 2:
                        email_type = parts[0].strip().lower()
                        email_address = parts[1].strip()
                        name = parts[2].strip() if len(parts) > 2 else "User"
                        
                        if email_type in self.recipients:
                            self.recipients[email_type].append({
                                'email': email_address,
                                'name': name
                            })
        
        print(f"Loaded email recipients: {len(self.recipients['summary'])} summary, {len(self.recipients['urgent'])} urgent")
        return True
    
    def test_configuration(self):
        """
        Test all configuration loading - useful for debugging
        """
        print("🧪 Testing Sally's configuration...")
        print("=" * 50)
        
        # Test school loading
        school_success = self.load_schools()
        
        # Test student loading  
        student_success = self.load_students()
        
        # Show privacy mapping test
        if student_success and self.students:
            print("\n🔒 Privacy Protection Test:")
            for real_name in self.students.keys():
                coded = self.get_coded_name(real_name)
                back_to_real = self.get_real_name(coded)
                print(f"   {real_name} → {coded} → {back_to_real}")
        
        print("=" * 50)
        if school_success and student_success:
            print("✅ All configuration loaded successfully!")
            return True
        else:
            print("❌ Configuration has issues - please check your files")
            return False

# Educational Tip: This pattern (if __name__ == "__main__") lets you test 
# this module independently by running: py config_manager.py
if __name__ == "__main__":
    print("🧪 Testing ConfigManager independently...")
    
    # Create and test the configuration manager
    config = ConfigManager()
    success = config.test_configuration()
    
    if success:
        print("🎉 Configuration system is working perfectly!")
    else:
        print("🔧 Please fix configuration files and try again.")
