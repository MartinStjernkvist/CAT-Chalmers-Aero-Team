from difflib import SequenceMatcher

def normalize_name(name):
    """Normalize name by converting to lowercase and removing extra spaces."""
    return ' '.join(name.lower().strip().split())

def parse_name(name):
    """
    Parse a name into components.
    Returns: dict with 'first', 'last', 'last_initial', 'full'
    """
    normalized = normalize_name(name)
    parts = normalized.split()
    
    if len(parts) == 0:
        return {}
    
    # Check if last part is an initial (single letter or letter with period)
    last_part = parts[-1].rstrip('.')
    
    result = {
        'first': parts[0],
        'full': normalized
    }
    
    if len(parts) > 1:
        if len(last_part) == 1:
            # Format like "Ted O" or "Ted O."
            result['last_initial'] = last_part
            result['last'] = ''
        else:
            # Full last name
            result['last'] = last_part
            result['last_initial'] = last_part[0]
    else:
        result['last'] = ''
        result['last_initial'] = ''
    
    return result

def names_match(attendee_name, team_name):
    """
    Check if an attendee name matches a team member name.
    Handles cases where team name is "First L." and attendee is "First Lastname"
    """
    attendee = parse_name(attendee_name)
    team = parse_name(team_name)
    
    # First names must match
    if attendee['first'] != team['first']:
        return False, 0.0
    
    # If team member has only initial, check if it matches
    if team['last_initial'] and not team['last']:
        if attendee['last']:
            # Attendee has full last name, team has initial
            if attendee['last'].startswith(team['last_initial']):
                return True, 1.0
        elif attendee['last_initial']:
            # Both have initials
            if attendee['last_initial'] == team['last_initial']:
                return True, 1.0
    
    # If both have full last names
    if team['last'] and attendee['last']:
        if team['last'] == attendee['last']:
            return True, 1.0
        # Fuzzy match on last name
        similarity = SequenceMatcher(None, team['last'], attendee['last']).ratio()
        if similarity > 0.8:
            return True, similarity
    
    # First name matches but can't confirm last name
    return False, 0.5

def find_best_match(attendance_name, team_members):
    """
    Find the best matching team member for an attendance entry.
    Uses multiple strategies including unique first name matching.
    """
    attendance_norm = normalize_name(attendance_name)
    attendee_parsed = parse_name(attendance_name)
    
    best_match = None
    best_score = 0
    all_matches = []
    
    # First pass: try exact matching with last name/initial
    for member in team_members:
        is_match, score = names_match(attendance_name, member)
        
        if is_match and score > best_score:
            best_match = member
            best_score = score
            all_matches.append((member, score))
        elif is_match:
            all_matches.append((member, score))
    
    # If we found good matches, return them
    if all_matches and best_score >= 0.8:
        # Check for ambiguous matches (multiple people with same first name and initial)
        if len(all_matches) > 1:
            scores = [s for _, s in all_matches]
            if len(set(scores)) == 1:
                # Ambiguous - can't distinguish
                return None, best_score, all_matches
        return best_match, best_score, all_matches
    
    # Second pass: check if first name is unique in team
    # Count how many team members have this first name
    first_name_matches = []
    for member in team_members:
        member_parsed = parse_name(member)
        if member_parsed['first'] == attendee_parsed['first']:
            first_name_matches.append(member)
    
    # If exactly one person has this first name, match them
    if len(first_name_matches) == 1:
        return first_name_matches[0], 0.9, [(first_name_matches[0], 0.9)]
    elif len(first_name_matches) > 1:
        # Multiple people with same first name - ambiguous
        return None, 0.5, [(m, 0.5) for m in first_name_matches]
    
    # No matches found
    return None, 0.0, []

def check_attendance(team_members_input, attendees_input):
    """
    Check attendance and return a detailed report.
    
    Args:
        team_members_input: String with team member names (one per line or comma-separated)
        attendees_input: String with attendee names (one per line)
    
    Returns:
        Dictionary with attendance results
    """
    # Parse inputs - handle both line-separated and comma-separated
    if '\n' in team_members_input:
        team_members = [line.strip() for line in team_members_input.strip().split('\n') if line.strip()]
    else:
        # Comma or period-separated (common in copy-paste from sheets)
        team_members = [name.strip().rstrip('.') for name in team_members_input.replace('.', '. ').split('.') if name.strip()]
        # Also try comma separation
        if len(team_members) == 1:
            team_members = [name.strip() for name in team_members_input.split(',') if name.strip()]
    
    attendees = [line.strip() for line in attendees_input.strip().split('\n') if line.strip()]
    
    # Track results
    present = []
    absent = []
    unmatched_attendees = []
    ambiguous = []
    
    # Mark attendance
    matched_members = set()
    
    for attendee in attendees:
        match, score, all_matches = find_best_match(attendee, team_members)
        
        if match and score >= 0.8:
            if match not in matched_members:
                present.append({
                    'team_name': match,
                    'attended_as': attendee,
                    'confidence': score
                })
                matched_members.add(match)
        elif all_matches and score > 0:
            # Ambiguous match
            ambiguous.append({
                'attended_as': attendee,
                'possible_matches': [m[0] for m in all_matches],
                'note': f'Could be: {", ".join([m[0] for m in all_matches])}'
            })
        else:
            unmatched_attendees.append(attendee)
    
    # Find absent members
    for member in team_members:
        if member not in matched_members:
            absent.append(member)
    
    return {
        'present': present,
        'absent': absent,
        'unmatched_attendees': unmatched_attendees,
        'ambiguous': ambiguous,
        'stats': {
            'total_members': len(team_members),
            'present_count': len(present),
            'absent_count': len(absent),
            'attendance_rate': f"{len(present)/len(team_members)*100:.1f}%" if team_members else "0%"
        }
    }

def print_report(results):
    """Print a formatted attendance report."""
    print("=" * 60)
    print("ATTENDANCE REPORT")
    print("=" * 60)
    
    print(f"\n📊 STATISTICS:")
    print(f"   Total Team Members: {results['stats']['total_members']}")
    print(f"   Present: {results['stats']['present_count']}")
    print(f"   Absent: {results['stats']['absent_count']}")
    print(f"   Attendance Rate: {results['stats']['attendance_rate']}")
    
    print(f"\n✅ PRESENT ({len(results['present'])}):")
    if results['present']:
        for p in sorted(results['present'], key=lambda x: x['team_name']):
            conf_indicator = "🟢" if p['confidence'] >= 0.95 else "🟡"
            print(f"   {conf_indicator} {p['team_name']}")
            if normalize_name(p['team_name']) != normalize_name(p['attended_as']):
                print(f"      (signed in as: {p['attended_as']})")
    else:
        print("   None")
    
    print(f"\n❌ ABSENT ({len(results['absent'])}):")
    if results['absent']:
        for member in sorted(results['absent']):
            print(f"   • {member}")
    else:
        print("   None")
    
    if results['ambiguous']:
        print(f"\n⚠️  AMBIGUOUS MATCHES ({len(results['ambiguous'])}):")
        for amb in results['ambiguous']:
            print(f"   • {amb['attended_as']}")
            print(f"     {amb['note']}")
    
    if results['unmatched_attendees']:
        print(f"\n❓ UNMATCHED ATTENDEES ({len(results['unmatched_attendees'])}):")
        print("   (These people attended but aren't on the team list)")
        for attendee in results['unmatched_attendees']:
            print(f"   • {attendee}")
    
    print("\n" + "=" * 60)

def generate_markdown_report(results, filename="attendance_report.md"):
    """Generate and save a markdown report."""
    from datetime import datetime
    import os
    
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    
    md_content = []
    
    # Header
    md_content.append("# Meeting Attendance Report")
    md_content.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Statistics
    md_content.append("## 📊 Statistics\n")
    md_content.append(f"- **Total Team Members:** {results['stats']['total_members']}")
    md_content.append(f"- **Present:** {results['stats']['present_count']}")
    md_content.append(f"- **Absent:** {results['stats']['absent_count']}")
    md_content.append(f"- **Attendance Rate:** {results['stats']['attendance_rate']}\n")
    
    # Present
    md_content.append(f"## ✅ Present ({len(results['present'])})\n")
    if results['present']:
        for p in sorted(results['present'], key=lambda x: x['team_name']):
            conf_indicator = "🟢" if p['confidence'] >= 0.95 else "🟡"
            md_content.append(f"- {conf_indicator} **{p['team_name']}**")
            if normalize_name(p['team_name']) != normalize_name(p['attended_as']):
                md_content.append(f"  - *Signed in as: {p['attended_as']}*")
    else:
        md_content.append("*None*")
    
    md_content.append("")
    
    # Absent
    md_content.append(f"## ❌ Absent ({len(results['absent'])})\n")
    if results['absent']:
        for member in sorted(results['absent']):
            md_content.append(f"- {member}")
    else:
        md_content.append("*None*")
    
    md_content.append("")
    
    # Ambiguous
    if results['ambiguous']:
        md_content.append(f"## ⚠️ Ambiguous Matches ({len(results['ambiguous'])})\n")
        for amb in results['ambiguous']:
            md_content.append(f"- **{amb['attended_as']}**")
            md_content.append(f"  - {amb['note']}")
        md_content.append("")
    
    # Unmatched
    if results['unmatched_attendees']:
        md_content.append(f"## ❓ Unmatched Attendees ({len(results['unmatched_attendees'])})\n")
        md_content.append("*These people attended but aren't on the team list*\n")
        for attendee in results['unmatched_attendees']:
            md_content.append(f"- {attendee}")
        md_content.append("")
    
    # Write to file
    report_text = '\n'.join(md_content)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    return filepath


# Example usage
if __name__ == "__main__":
    import os
    
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    TEAM_FILE = os.path.join(script_dir, "team_members.txt")
    
    print("MEETING ATTENDANCE CHECKER")
    print("=" * 60)
    
    # Check if team members file exists
    team_members_input = None
    if os.path.exists(TEAM_FILE):
        print(f"\n📁 Found existing team members file: team_members.txt")
        
        # Show preview of team members
        with open(TEAM_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            lines = content.split('\n') if '\n' in content else content.split(',')
            preview = lines[:5]
            print(f"   Preview: {', '.join([l.strip() for l in preview])}")
            if len(lines) > 5:
                print(f"   ... and {len(lines) - 5} more")
        
        use_existing = input("\n   Use this team list? (y/n): ").strip().lower()
        
        if use_existing == 'y':
            with open(TEAM_FILE, 'r', encoding='utf-8') as f:
                team_members_input = f.read()
            print("   ✓ Using existing team list")
        else:
            print("   Creating new team list...")
    
    # If no existing file or user wants to create new one
    if team_members_input is None:
        print("\n📋 Paste your TEAM MEMBERS list.")
        print("(Can be comma-separated or one per line)")
        print("Press Enter twice when done:\n")
        team_lines = []
        while True:
            line = input()
            if line == "":
                break
            team_lines.append(line)
        team_members_input = '\n'.join(team_lines)
        
        # Save to file
        with open(TEAM_FILE, 'w', encoding='utf-8') as f:
            f.write(team_members_input)
        print(f"\n💾 Team list saved to {TEAM_FILE}")
    
    # Get attendees list
    print("\n📝 Paste your ATTENDEES list (one name per line).")
    print("Press Enter twice when done:\n")
    attendee_lines = []
    while True:
        line = input()
        if line == "":
            break
        attendee_lines.append(line)
    attendees_input = '\n'.join(attendee_lines)
    
    # Process and display results
    print("\n🔄 Processing attendance...\n")
    results = check_attendance(team_members_input, attendees_input)
    print_report(results)
    
    # Save to markdown file
    filename = generate_markdown_report(results)
    print(f"\n💾 Report saved to: {filename}")
    print(f"   You can open this file in any markdown viewer or text editor.")