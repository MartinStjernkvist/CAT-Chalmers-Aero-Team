import re
from pathlib import Path
from tkinter import Tk, filedialog
from typing import Dict, List, Optional, Tuple

from parser_v2 import ReportParser


class IndividualReports:
    """Manages Individual Progress Reports (IPR) for a specific week"""

    def __init__(self, week_number: int):
        self.week_number = week_number
        self.folder_path: Optional[Path] = None
        self.reports: Dict[str, Tuple[str, Dict]] = {}  # {name: (content, metadata)}
        self.members_list: List[str] = []

    def select_folder(self) -> Optional[Path]:
        """Open file dialog to select folder containing IPR files"""
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        folder_selected = filedialog.askdirectory(
            title="Select folder containing Individual Progress Reports (.docx)"
        )
        root.destroy()

        if not folder_selected:
            print("✗ No folder selected")
            return None

        self.folder_path = Path(folder_selected)
        self._load_all_reports()
        
        print(f"✓ Folder: {self.folder_path}")
        print(f"✓ Found {len(self.reports)} reports for week {self.week_number}")
        
        return self.folder_path

    def _load_all_reports(self):
        """Load all IPR .docx files from the folder"""
        if not self.folder_path:
            return

        self.reports.clear()
        
        # Pattern to extract name from filename: "IPR Name.docx" or "IPR - Name.docx"
        name_pattern = re.compile(r'IPR\s*[-–—]?\s*(.+)', re.IGNORECASE)

        for file in self.folder_path.glob('*.docx'):
            # Skip temporary files
            if file.name.startswith('~$'):
                continue

            # Extract person's name from filename
            match = name_pattern.search(file.stem)
            if not match:
                print(f"⚠ Skipping file with unexpected name: {file.name}")
                continue

            name = match.group(1).strip()

            try:
                # Read the document
                text = ReportParser.read_docx(file)
                
                # Split into weeks
                weeks = ReportParser.split_by_weeks(text)
                
                # Get the requested week
                if self.week_number not in weeks:
                    print(f"⚠ Week {self.week_number} not found in {file.name}")
                    print(f"   Available weeks: {sorted(weeks.keys())}")
                    continue
                
                week_content = weeks[self.week_number]
                metadata = ReportParser.extract_metadata(week_content)
                
                self.reports[name] = (week_content, metadata)
                
            except Exception as e:
                print(f"✗ Error loading {file.name}: {e}")

        # Create sorted member list
        self.members_list = sorted(self.reports.keys())

    def list_members(self) -> List[str]:
        """Display all members and their info"""
        if not self.reports:
            print("✗ No reports loaded")
            return []

        print(f"\n{'=' * 80}")
        print(f"TEAM MEMBERS - WEEK {self.week_number} ({len(self.members_list)} members)")
        print(f"{'=' * 80}\n")

        for idx, name in enumerate(self.members_list):
            _, metadata = self.reports[name]
            sub_team = metadata.get('sub_team', 'N/A')
            main_task = metadata.get('main_task', 'N/A')
            print(f"[{idx:2d}] {name:30s} | {sub_team:20s} | {main_task}")

        print()
        return self.members_list

    def get_individual_report(self, index: int) -> Optional[str]:
        """Get and display a specific person's report by index"""
        if not self.reports:
            print("✗ No reports loaded")
            return None

        if not (0 <= index < len(self.members_list)):
            print(f"✗ Invalid index. Valid range: 0-{len(self.members_list) - 1}")
            return None

        name = self.members_list[index]
        content, metadata = self.reports[name]

        print(f"\n{'=' * 80}")
        print(f"[{index:02d}] {name}")
        print(f"{'=' * 80}")
        
        if metadata.get('sub_team'):
            print(f"Sub-team: {metadata['sub_team']}")
        if metadata.get('main_task'):
            print(f"Main Task: {metadata['main_task']}")
        
        print(f"\n{content}\n")
        return content

    def compile_all(self) -> Optional[Path]:
        """Compile all reports into a single markdown file"""
        if not self.folder_path or not self.reports:
            print("✗ No reports to compile")
            return None

        output_dir = self.folder_path / str(self.week_number)
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"Compiled_IPR_W{self.week_number:02d}.md"

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Compiled Individual Progress Reports - Week {self.week_number}\n\n")
                f.write(f"**Total members:** {len(self.reports)}\n\n")
                f.write("---\n\n")

                for idx, name in enumerate(self.members_list):
                    content, metadata = self.reports[name]

                    f.write(f"## [{idx:02d}] {name}\n\n")

                    if metadata.get('sub_team'):
                        f.write(f"**Sub-team:** {metadata['sub_team']}  \n")
                    if metadata.get('main_task'):
                        f.write(f"**Main Task:** {metadata['main_task']}  \n")

                    f.write(f"\n{content}\n\n")
                    f.write("---\n\n")

            print(f"✓ Saved: {output_file}")
            return output_file

        except Exception as e:
            print(f"✗ Error: {e}")
            return None

    def compile_section(self, section_name: str) -> Optional[Path]:
        """Compile a specific section (progress, problems, plans) from all reports"""
        if not self.folder_path or not self.reports:
            print("✗ No reports to compile")
            return None

        output_dir = self.folder_path / str(self.week_number)
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"IPR_{section_name.title()}_W{self.week_number:02d}.md"

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Individual {section_name.title()} - Week {self.week_number}\n\n")

                for idx, name in enumerate(self.members_list):
                    content, metadata = self.reports[name]
                    section_text = ReportParser.extract_section(content, section_name)

                    if section_text:
                        f.write(f"## [{idx:02d}] {name}")
                        if metadata.get('sub_team'):
                            f.write(f" | {metadata['sub_team']}")
                        f.write(f"\n\n{section_text}\n\n")
                        f.write("---\n\n")

            print(f"✓ Saved: {output_file}")
            return output_file

        except Exception as e:
            print(f"✗ Error: {e}")
            return None

    def compile_progress(self) -> Optional[Path]:
        return self.compile_section('progress')

    def compile_problems(self) -> Optional[Path]:
        return self.compile_section('problems')

    def compile_plans(self) -> Optional[Path]:
        return self.compile_section('plans')