"""
Add a new Academy Snapshot issue to the archive.

Usage:
    python add_issue.py

This script will:
1. Ask you for the issue details (or auto-detect from the file)
2. Extract text from PDF/PNG to help you fill in metadata
3. Update snapshot_data.json with the new entry
4. Rebuild the embed.html with updated inline data
5. Commit and push to GitHub (optional)

Requirements: pymupdf (pip install pymupdf)
"""
import json
import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'snapshot_data.json')
EMBED_FILE = os.path.join(BASE_DIR, 'embed.html')

ROLE_CATEGORIES = ['Test', 'Dev', 'BA', 'PM', 'DevOps', 'Security', 'Data', 'Service Desk', 'Internal']
SPECIALISMS = [
    'Manual / Functional', 'Automation', 'Performance', 'Accessibility',
    'Aviation Systems', 'Transport Systems', 'Data Migration', 'Data',
    'Data Visualisation', 'API Testing', 'RPA', 'Mobile', 'Retail Systems',
    'Front-End', 'Back-End', 'Software Development', 'Cloud / Architecture',
    'Cyber Security', 'VR / Digital', 'DevOps', 'Service Desk',
    'Business Analysis', 'Process Improvement', 'Project Delivery',
    'System Configuration', 'UAT', 'Digital Transformation',
    'Sustainability', 'Operations', 'Governance', 'Training',
    'Wellbeing', 'Recruitment'
]


def extract_text_pdf(filepath):
    """Extract text from a PDF using pymupdf."""
    try:
        import fitz
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except ImportError:
        print("  [!] pymupdf not installed. Run: pip install pymupdf")
        return None


def extract_text_image(filepath):
    """Extract text from an image using Windows OCR."""
    try:
        ps_script = f'''
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {{ $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' }})[0]
Function Await($WinRtTask, $ResultType) {{ $asTask = $asTaskGeneric.MakeGenericMethod($ResultType); $netTask = $asTask.Invoke($null, @($WinRtTask)); $netTask.Wait(-1) | Out-Null; $netTask.Result }}
[Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Foundation, ContentType = WindowsRuntime] | Out-Null
[Windows.Storage.StorageFile, Windows.Foundation, ContentType = WindowsRuntime] | Out-Null
$ocrEngine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
$storageFile = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync("{filepath}")) ([Windows.Storage.StorageFile])
$stream = Await ($storageFile.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
$decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
$bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
$ocrResult = Await ($ocrEngine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
Write-Output $ocrResult.Text
$stream.Dispose()
'''
        result = subprocess.run(['powershell', '-Command', ps_script],
                              capture_output=True, text=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        print(f"  [!] OCR failed: {e}")
        return None


def pick_from_list(prompt, options, allow_custom=True):
    """Let user pick from a list or enter custom value."""
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i:2}. {opt}")
    if allow_custom:
        print(f"  Or type a custom value")
    
    while True:
        choice = input("  > ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        elif allow_custom and choice:
            return choice
        print("  Invalid choice, try again.")


def ask(prompt, default=None):
    """Ask a question with optional default."""
    if default:
        val = input(f"  {prompt} [{default}]: ").strip()
        return val if val else default
    else:
        while True:
            val = input(f"  {prompt}: ").strip()
            if val:
                return val
            print("  Required field, please enter a value.")


def ask_yn(prompt, default='y'):
    """Ask yes/no."""
    val = input(f"  {prompt} [{'Y/n' if default == 'y' else 'y/N'}]: ").strip().lower()
    if not val:
        return default == 'y'
    return val in ('y', 'yes')


def rebuild_embed(data):
    """Rebuild embed.html with updated inline data."""
    mini = []
    for e in data['entries']:
        files = e.get('sourceFiles', [])
        mini.append({
            'i': e['issue'],
            'd': e['date'],
            'n': e['name'],
            'r': e['role'],
            'c': e['client'],
            'rc': e.get('roleCategory', ''),
            'sp': e.get('specialism', ''),
            'a': e.get('academy'),
            's': e.get('sector', ''),
            'rl': e.get('relocated', False),
            'f': files[0] if files else '',
        })
    
    mini_json = json.dumps(mini, separators=(',', ':'))
    
    # Read embed template (everything before and after the data line)
    with open(EMBED_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the data line
    import re
    content = re.sub(
        r'const D=\[.*?\];',
        f'const D={mini_json};',
        content,
        count=1,
        flags=re.DOTALL
    )
    
    with open(EMBED_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  [✓] embed.html updated with {len(mini)} entries")


def main():
    print("=" * 60)
    print("  ADD NEW ACADEMY SNAPSHOT ISSUE")
    print("=" * 60)
    
    # Load existing data
    data = json.load(open(DATA_FILE, encoding='utf-8'))
    existing_issues = sorted(set(e['issue'] for e in data['entries']))
    print(f"\n  Existing issues: {existing_issues[-5:]}... (latest: Issue {max(existing_issues)})")
    
    # Get issue number
    issue_num = int(ask("Issue number"))
    
    # Check for issue folder
    issue_folders = [f for f in os.listdir(BASE_DIR) 
                     if os.path.isdir(os.path.join(BASE_DIR, f)) 
                     and f.startswith('Issue') 
                     and str(issue_num) in f.split(' ')[1] if len(f.split(' ')) > 1]
    
    # Find the folder
    folder = None
    for f in os.listdir(BASE_DIR):
        if os.path.isdir(os.path.join(BASE_DIR, f)) and f.startswith('Issue'):
            parts = f.replace('Issue ', '').split(' - ')
            try:
                if int(parts[0].strip()) == issue_num:
                    folder = f
                    break
            except ValueError:
                continue
    
    if folder:
        print(f"\n  Found folder: {folder}")
        files = sorted([f for f in os.listdir(os.path.join(BASE_DIR, folder))
                       if f.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf'))])
        print(f"  Files: {files}")
    else:
        print(f"\n  [!] No folder found for Issue {issue_num}.")
        print(f"  Please create a folder like 'Issue {issue_num}' and add the files first.")
        return
    
    # Get issue date
    date = ask("Date (e.g. 'July 2026')")
    
    # Edition type
    edition = ask("Edition type", "Standard")
    
    # Process each file as a person
    print(f"\n  Processing {len(files)} file(s)...")
    
    for file in files:
        filepath = os.path.join(BASE_DIR, folder, file)
        ext = file.split('.')[-1].lower()
        
        print(f"\n{'─' * 60}")
        print(f"  FILE: {file}")
        print(f"{'─' * 60}")
        
        # Extract text
        text = None
        if ext == 'pdf':
            text = extract_text_pdf(filepath)
        elif ext in ('png', 'jpg', 'jpeg'):
            text = extract_text_image(filepath)
        
        if text:
            print(f"\n  EXTRACTED TEXT (first 500 chars):")
            print(f"  {'─' * 40}")
            print(f"  {text[:500]}...")
            print(f"  {'─' * 40}")
        
        # Gather metadata
        print(f"\n  Enter details for this person:")
        name = ask("Full name")
        academy_str = ask("Academy number (or 'none' for internal)")
        academy = int(academy_str) if academy_str.lower() != 'none' else None
        client = ask("Client name")
        role = ask("Job title/role")
        role_cat = pick_from_list("Role category:", ROLE_CATEGORIES)
        specialism = pick_from_list("Specialism:", sorted(SPECIALISMS))
        sector = ask("Sector (e.g. 'Aviation/Air Traffic Control', 'Retail')")
        methodology = ask("Methodology", "Agile")
        location = ask("Location (e.g. 'Remote', 'Hybrid (2 days office)', 'Office')")
        relocated = ask_yn("Did they relocate?", 'n')
        reloc_details = ask("Relocation details") if relocated else None
        
        tools_str = ask("Tools (comma-separated, or 'none')", "none")
        tools = [t.strip() for t in tools_str.split(',')] if tools_str.lower() != 'none' else []
        
        # Build entry
        entry = {
            "issue": issue_num,
            "date": date,
            "name": name,
            "academy": academy,
            "client": client,
            "role": role,
            "roleCategory": role_cat,
            "specialism": specialism,
            "tools": tools,
            "methodology": methodology,
            "location": location,
            "relocated": relocated,
            "sector": sector,
            "editionType": edition,
            "fileFormat": ext,
            "sourceFiles": [f"{folder}/{file}"]
        }
        if reloc_details:
            entry["relocationDetails"] = reloc_details
        
        data['entries'].append(entry)
        print(f"\n  [✓] Added: {name} (Issue {issue_num})")
    
    # Save JSON
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n  [✓] snapshot_data.json saved ({len(data['entries'])} total entries)")
    
    # Rebuild embed
    rebuild_embed(data)
    
    # Git commit & push
    if ask_yn("\n  Commit and push to GitHub?", 'y'):
        subprocess.run(['git', 'add', '.'], cwd=BASE_DIR)
        subprocess.run(['git', 'commit', '-m', f'Add Issue {issue_num} - {date}'], cwd=BASE_DIR)
        subprocess.run(['git', 'push'], cwd=BASE_DIR)
        print(f"\n  [✓] Pushed to GitHub. Pages will update in ~1 minute.")
    
    print(f"\n{'=' * 60}")
    print(f"  DONE! Issue {issue_num} added successfully.")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
