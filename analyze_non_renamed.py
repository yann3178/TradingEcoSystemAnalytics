"""
Analyze Non-Renamed Files
==========================
Analyzes the 346 files that were not renamed during migration
to help understand what they are and decide what to do with them.

Author: Trading Analytics V2
Date: 2025-11-28
"""

import json
from pathlib import Path
from collections import defaultdict
import re


# =============================================================================
# CONFIGURATION
# =============================================================================

HTML_REPORTS_DIR = Path(r"C:\TradeData\V2\outputs\html_reports")
MIGRATION_REPORT = Path(r"C:\TradeData\V2\outputs\consolidated\migration_report.json")
OUTPUT_REPORT = Path(r"C:\TradeData\V2\outputs\consolidated\non_renamed_analysis.json")
OUTPUT_TXT = Path(r"C:\TradeData\V2\outputs\consolidated\non_renamed_analysis.txt")


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def load_non_renamed_files():
    """Load the list of files that were not renamed from migration report."""
    with open(MIGRATION_REPORT, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    non_renamed = []
    for detail in report.get('migration_details', []):
        if detail['action'] == 'keep_original':
            non_renamed.append({
                'name': detail['old_name'],
                'strategy_name': detail['strategy_name'],
                'reason': detail['reason']
            })
    
    return non_renamed


def categorize_files(files):
    """Categorize non-renamed files by pattern."""
    categories = {
        'starts_with_dollar': [],      # $PS_, $CATA_, etc.
        'numeric_only': [],             # 237.html, 249.html
        'correlation_files': [],        # *_correlation.html
        'backup_files': [],             # *.bak
        'index_files': [],              # index*.html
        'special_chars': [],            # Contains special encoding (d20, c2d, etc.)
        'other': []
    }
    
    for f in files:
        name = f['name']
        
        if 'correlation' in name.lower():
            categories['correlation_files'].append(f)
        elif name.endswith('.bak'):
            categories['backup_files'].append(f)
        elif 'index' in name.lower():
            categories['index_files'].append(f)
        elif name.startswith('$'):
            categories['starts_with_dollar'].append(f)
        elif re.match(r'^\d+\.html$', name):
            categories['numeric_only'].append(f)
        elif any(code in name for code in ['d20', 'd21', 'c2d', 'c28', 'c29']):
            categories['special_chars'].append(f)
        else:
            categories['other'].append(f)
    
    return categories


def analyze_prefix_patterns(files):
    """Analyze common prefixes in non-renamed files."""
    prefixes = defaultdict(list)
    
    for f in files:
        name = f['name']
        
        # Extract prefix (before first underscore or number)
        if '_' in name:
            prefix = name.split('_')[0]
        elif re.match(r'^([A-Za-z$]+)', name):
            match = re.match(r'^([A-Za-z$]+)', name)
            prefix = match.group(1) if match else 'unknown'
        else:
            prefix = 'numeric_or_special'
        
        prefixes[prefix].append(name)
    
    return dict(prefixes)


def get_file_stats(categories):
    """Calculate statistics for each category."""
    stats = {}
    for cat, files in categories.items():
        stats[cat] = {
            'count': len(files),
            'examples': [f['name'] for f in files[:5]]
        }
    return stats


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_analysis_report():
    """Generate comprehensive analysis report."""
    print("="*70)
    print("NON-RENAMED FILES ANALYSIS")
    print("="*70)
    
    # Load non-renamed files
    print("\n[1/4] Loading non-renamed files from migration report...")
    non_renamed = load_non_renamed_files()
    print(f"✓ Found {len(non_renamed)} non-renamed files")
    
    # Categorize
    print("\n[2/4] Categorizing files...")
    categories = categorize_files(non_renamed)
    
    # Analyze prefixes
    print("\n[3/4] Analyzing prefix patterns...")
    prefixes = analyze_prefix_patterns(non_renamed)
    
    # Get stats
    print("\n[4/4] Generating statistics...")
    stats = get_file_stats(categories)
    
    # Display results
    print("\n" + "="*70)
    print("ANALYSIS RESULTS")
    print("="*70)
    
    print(f"\nTotal non-renamed files: {len(non_renamed)}")
    
    print("\n📊 BY CATEGORY:")
    print("-" * 70)
    for cat, data in stats.items():
        if data['count'] > 0:
            print(f"\n{cat.replace('_', ' ').title()}: {data['count']} files")
            if data['examples']:
                print("  Examples:")
                for ex in data['examples']:
                    print(f"    - {ex}")
    
    print("\n📝 BY PREFIX:")
    print("-" * 70)
    sorted_prefixes = sorted(prefixes.items(), key=lambda x: len(x[1]), reverse=True)
    for prefix, files in sorted_prefixes[:10]:  # Top 10
        print(f"\n{prefix}: {len(files)} files")
        for fname in files[:3]:
            print(f"  - {fname}")
        if len(files) > 3:
            print(f"  ... and {len(files) - 3} more")
    
    # Recommendations
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)
    
    print("\n✅ Files to KEEP as is:")
    if stats.get('correlation_files', {}).get('count', 0) > 0:
        print(f"  - {stats['correlation_files']['count']} correlation files (already have suffix)")
    if stats.get('backup_files', {}).get('count', 0) > 0:
        print(f"  - {stats['backup_files']['count']} backup files (.bak)")
    if stats.get('index_files', {}).get('count', 0) > 0:
        print(f"  - {stats['index_files']['count']} index files")
    
    print("\n💡 Files that might need attention:")
    if stats.get('starts_with_dollar', {}).get('count', 0) > 0:
        print(f"  - {stats['starts_with_dollar']['count']} files starting with '$'")
        print(f"    → These are strategies not in Portfolio Report")
        print(f"    → Decision: Keep if they're non-backtested strategies")
    
    if stats.get('numeric_only', {}).get('count', 0) > 0:
        print(f"  - {stats['numeric_only']['count']} numeric-only files (237.html, etc.)")
        print(f"    → These seem to be old or temporary files")
        print(f"    → Decision: Archive or delete if not needed")
    
    if stats.get('special_chars', {}).get('count', 0) > 0:
        print(f"  - {stats['special_chars']['count']} files with special encoding")
        print(f"    → Names contain encoded characters (d20, c2d, etc.)")
        print(f"    → Decision: Keep as is, fix at source later")
    
    # Save JSON report
    report_data = {
        'total_non_renamed': len(non_renamed),
        'categories': stats,
        'prefixes': {k: len(v) for k, v in prefixes.items()},
        'detailed_list': [f['name'] for f in non_renamed]
    }
    
    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ JSON report saved: {OUTPUT_REPORT}")
    
    # Save TXT report
    with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
        f.write("NON-RENAMED FILES - DETAILED LIST\n")
        f.write("="*70 + "\n\n")
        f.write(f"Total: {len(non_renamed)} files\n\n")
        
        for cat, files in categories.items():
            if files:
                f.write(f"\n{cat.upper()}\n")
                f.write("-"*70 + "\n")
                for file_info in files:
                    f.write(f"{file_info['name']}\n")
    
    print(f"✓ Text report saved: {OUTPUT_TXT}")
    
    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE")
    print("="*70)


if __name__ == "__main__":
    generate_analysis_report()
