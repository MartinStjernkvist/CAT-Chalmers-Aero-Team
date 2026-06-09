import re
from pathlib import Path
from tkinter import Tk, filedialog
from typing import Dict, List, Optional, Tuple

from parser_v2 import ReportParser

script_dir = Path(__file__).parent

class SubTeamReports:
    """Manages Sub-team Progress Reports (SPR) for a specific week"""

    def __init__(self, week_number: int, sub_team_name: str = ""):
        self.week_number = week_number
        self.sub_team_name = sub_team_name
        self.folder_path: Optional[Path] = None
        self.reports: Dict[str, Tuple[str, Dict]] = {}  # {team_name: (content, metadata)}
        self.teams_list: List[str] = []

    def select_folder(self) -> Optional[Path]:
        """Open file dialog to select folder containing SPR files"""
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        folder_selected = filedialog.askdirectory(
            title="Select folder containing Sub-team Progress Reports (.docx)"
        )
        root.destroy()

        if not folder_selected:
            print("✗ No folder selected")
            return None

        self.folder_path = Path(folder_selected)
        self._load_all_reports()
        
        print(f"✓ Folder: {self.folder_path}")
        print(f"✓ Found {len(self.reports)} reports for week {self.week_number}")
        if self.reports:
            print(f"  Sub-teams: {', '.join(sorted(self.reports.keys()))}")
        
        return self.folder_path

    def _load_all_reports(self):
        """Load all SPR .docx files from the folder"""
        if not self.folder_path:
            return

        self.reports.clear()
        
        # Pattern to extract team name from filename: "SPR Team.docx" or "SPR - Team.docx"
        name_pattern = re.compile(r'SPR\s*[-–—]?\s*(.+)', re.IGNORECASE)

        for file in self.folder_path.glob('*.docx'):
            # Skip temporary files
            if file.name.startswith('~$'):
                continue

            match = name_pattern.search(file.stem)
            if not match:
                print(f"⚠ Skipping file with unexpected name: {file.name}")
                continue

            team_name = match.group(1).strip()

            try:
                text = ReportParser.read_docx(file)
                
                weeks = ReportParser.split_by_weeks(text)
                
                if self.week_number not in weeks:
                    print(f"⚠ Week {self.week_number} not found in {file.name}")
                    print(f"   Available weeks: {sorted(weeks.keys())}")
                    continue
                
                week_content = weeks[self.week_number]
                
                metadata = {}
                names_match = re.search(
                    r'Name\(s\)\s*:\s*(.+?)(?:\n|$)',
                    week_content,
                    re.IGNORECASE
                )
                if names_match:
                    metadata['names'] = names_match.group(1).strip()
                
                self.reports[team_name] = (week_content, metadata)
                
            except Exception as e:
                print(f"✗ Error loading {file.name}: {e}")

        # Create sorted teams list
        self.teams_list = sorted(self.reports.keys())

    def list_teams(self) -> List[str]:
        """Display all sub-teams and their info"""
        if not self.reports:
            print("✗ No reports loaded")
            return []

        print(f"\n{'=' * 80}")
        print(f"SUB-TEAMS - WEEK {self.week_number} ({len(self.teams_list)} teams)")
        print(f"{'=' * 80}\n")

        for idx, team_name in enumerate(self.teams_list):
            _, metadata = self.reports[team_name]
            members = metadata.get('names', 'N/A')
            print(f"[{idx:2d}] {team_name:30s} | Members: {members}")

        print()
        return self.teams_list

    def get_team_report(self, team_name: str = None) -> Optional[str]:
        """Get and display a specific sub-team's report"""
        if not self.reports:
            print("✗ No reports loaded")
            return None

        # Use provided team_name or fall back to instance attribute
        search_name = team_name if team_name else self.sub_team_name
        
        if not search_name:
            print("✗ No sub-team name specified.")
            print(f"Available sub-teams: {', '.join(sorted(self.reports.keys()))}")
            return None

        # Find matching teams (case-insensitive partial match)
        matching_teams = [
            team for team in self.reports.keys()
            if search_name.lower() in team.lower()
        ]

        if not matching_teams:
            print(f"✗ Sub-team '{search_name}' not found.")
            print(f"Available sub-teams: {', '.join(sorted(self.reports.keys()))}")
            return None

        if len(matching_teams) > 1:
            print(f"⚠ Multiple matches found: {', '.join(matching_teams)}")
            print(f"Using: {matching_teams[0]}")

        team_name = matching_teams[0]
        content, metadata = self.reports[team_name]

        print(f"\n{'=' * 80}")
        print(f"SUB-TEAM: {team_name}")
        print(f"{'=' * 80}")
        if metadata.get('names'):
            print(f"Team Members: {metadata['names']}")
        print(f"\n{content}\n")

        return content

    def compile_all(self) -> Optional[Path]:
        """Compile all reports into a single markdown file"""
        if not self.folder_path or not self.reports:
            print("✗ No reports to compile")
            return None

        output_dir = script_dir / str(self.week_number)
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"Compiled_SPR_W{self.week_number:02d}.md"

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Compiled Sub-team Progress Reports - Week {self.week_number}\n\n")
                f.write(f"**Total sub-teams:** {len(self.reports)}\n\n")
                f.write("---\n\n")

                for team_name in sorted(self.reports.keys()):
                    content, metadata = self.reports[team_name]

                    f.write(f"## {team_name}\n\n")

                    if metadata.get('names'):
                        f.write(f"**Team Members:** {metadata['names']}\n\n")

                    f.write(f"{content}\n\n")
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

        output_dir = script_dir / str(self.week_number)
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"SPR_{section_name.title()}_W{self.week_number:02d}.md"

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Sub-team {section_name.title()} - Week {self.week_number}\n\n")

                for team_name in sorted(self.reports.keys()):
                    content, _ = self.reports[team_name]
                    section_text = ReportParser.extract_section(content, section_name)

                    if section_text:
                        f.write(f"## {team_name}\n\n")
                        f.write(f"{section_text}\n\n")
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