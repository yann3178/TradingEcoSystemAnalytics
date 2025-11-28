"""
Post-Migration Verification Script
===================================
Validates that the migration was successful by checking file counts,
naming patterns, and data integrity.

Author: Trading Analytics V2
Date: 2025-11-28
"""

import json
from pathlib import Path
from collections import defaultdict


# =============================================================================
# CONFIGURATION
# =============================================================================

HTML_REPORTS_DIR = Path(r"C:\TradeData\V2\outputs\html_reports")
MIGRATION_REPORT = Path(r"C:\TradeData\V2\outputs\consolidated\migration_report.json")
BACKUP_DIR = Path(r"C:\TradeData\V2\backups")


# =============================================================================
# VERIFICATION FUNCTIONS
# =============================================================================

def check_migration_report() -> dict:
    """Check if migration report exists and load it."""
    if not MIGRATION_REPORT.exists():
        return {
            'exists': False,
            'error': 'Migration report not found'
        }
    
    with open(MIGRATION_REPORT, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    return {
        'exists': True,
        'report': report
    }


def check_file_counts(expected_total: int = None) -> dict:
    """Check file counts and categorize files."""
    files = {
        'main': [],
        'correlation': [],
        'backup': [],
        'index': [],
        'other': []
    }
    
    for html_file in HTML_REPORTS_DIR.glob("*.html"):
        name = html_file.name.lower()
        
        if 'correlation' in name:
            files['correlation'].append(html_file)
        elif name.endswith('.bak'):
            files['backup'].append(html_file)
        elif 'index' in name:
            files['index'].append(html_file)
        elif 'mobile-enhancement' in name:
            files['other'].append(html_file)
        else:
            files['main'].append(html_file)
    
    total = sum(len(v) for v in files.values())
    
    return {
        'total': total,
        'main_files': len(files['main']),
        'correlation_files': len(files['correlation']),
        'backup_files': len(files['backup']),
        'index_files': len(files['index']),
        'other_files': len(files['other']),
        'expected_total': expected_total,
        'count_matches': total == expected_total if expected_total else None,
        'files': files
    }


def check_naming_pattern() -> dict:
    """Check if main files follow the new naming pattern (Symbol_StrategyName)."""
    main_files = [
        f for f in HTML_REPORTS_DIR.glob("*.html")
        if not any(x in f.name.lower() for x in ['correlation', 'index', 'mobile'])
        and not f.name.endswith('.bak')
    ]
    
    # Pattern: Should start with uppercase letters (symbol) followed by underscore
    # Examples: NQ_SOM_UA_2301_G_1.html, FDAX_ATS_Strategy_v0.8.html
    
    with_prefix = []
    without_prefix = []
    
    for f in main_files:
        name = f.name
        
        # Check if starts with likely symbol pattern
        # Symbols are typically 2-6 uppercase letters followed by underscore
        if '_' in name:
            prefix = name.split('_')[0]
            if prefix.isupper() and 2 <= len(prefix) <= 6:
                with_prefix.append(f)
            else:
                without_prefix.append(f)
        else:
            without_prefix.append(f)
    
    return {
        'total_main_files': len(main_files),
        'with_symbol_prefix': len(with_prefix),
        'without_symbol_prefix': len(without_prefix),
        'percentage_migrated': (len(with_prefix) / len(main_files) * 100) if main_files else 0,
        'files_without_prefix': [f.name for f in without_prefix[:10]]  # Show first 10
    }


def check_backup_exists() -> dict:
    """Check if a recent backup exists."""
    if not BACKUP_DIR.exists():
        return {
            'exists': False,
            'backups_found': 0
        }
    
    backups = []
    for backup_path in BACKUP_DIR.iterdir():
        if not backup_path.is_dir():
            continue
        
        manifest_path = backup_path / "manifest.json"
        if manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            backups.append({
                'timestamp': backup_path.name,
                'files_backed_up': manifest.get('files_backed_up', 0)
            })
    
    backups.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return {
        'exists': len(backups) > 0,
        'backups_found': len(backups),
        'latest_backup': backups[0] if backups else None,
        'all_backups': backups
    }


def check_symbol_distribution() -> dict:
    """Analyze symbol distribution in file names."""
    main_files = [
        f for f in HTML_REPORTS_DIR.glob("*.html")
        if not any(x in f.name.lower() for x in ['correlation', 'index', 'mobile'])
        and not f.name.endswith('.bak')
    ]
    
    symbol_counts = defaultdict(int)
    
    for f in main_files:
        name = f.name
        if '_' in name:
            symbol = name.split('_')[0]
            if symbol.isupper() and 2 <= len(symbol) <= 6:
                symbol_counts[symbol] += 1
    
    return {
        'symbols_found': len(symbol_counts),
        'distribution': dict(sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:10])  # Top 10
    }


# =============================================================================
# MAIN VERIFICATION
# =============================================================================

def run_verification():
    """Run all verification checks."""
    print("="*70)
    print("POST-MIGRATION VERIFICATION")
    print("="*70)
    
    results = {
        'passed': [],
        'warnings': [],
        'errors': []
    }
    
    # Check 1: Migration report
    print("\n[1/5] Checking migration report...")
    report_check = check_migration_report()
    
    if report_check['exists']:
        report = report_check['report']
        print(f"✓ Migration report found")
        print(f"  - Total files: {report.get('total_files', 'N/A')}")
        print(f"  - Renamed: {report.get('statistics', {}).get('renamed', 'N/A')}")
        print(f"  - Kept original: {report.get('statistics', {}).get('kept_original', 'N/A')}")
        print(f"  - Errors: {report.get('statistics', {}).get('errors', 'N/A')}")
        print(f"  - Warnings: {len(report.get('warnings', []))}")
        
        results['passed'].append('Migration report exists and is readable')
        
        if report.get('statistics', {}).get('errors', 0) > 0:
            results['errors'].append(f"{report['statistics']['errors']} errors in migration")
    else:
        print(f"✗ Migration report not found")
        results['errors'].append('Migration report missing')
        report = None
    
    # Check 2: File counts
    print("\n[2/5] Checking file counts...")
    expected_total = report.get('total_files') if report else None
    counts = check_file_counts(expected_total)
    
    print(f"✓ Total HTML files: {counts['total']}")
    print(f"  - Main files: {counts['main_files']}")
    print(f"  - Correlation files: {counts['correlation_files']}")
    print(f"  - Index files: {counts['index_files']}")
    print(f"  - Other files: {counts['other_files']}")
    
    if counts['count_matches'] is not None:
        if counts['count_matches']:
            print(f"✓ File count matches expected ({expected_total})")
            results['passed'].append('File count matches expected')
        else:
            print(f"✗ File count mismatch (expected {expected_total}, got {counts['total']})")
            results['warnings'].append(f"File count mismatch: expected {expected_total}, got {counts['total']}")
    
    # Check 3: Naming pattern
    print("\n[3/5] Checking naming patterns...")
    naming = check_naming_pattern()
    
    print(f"✓ Main files analyzed: {naming['total_main_files']}")
    print(f"  - With symbol prefix: {naming['with_symbol_prefix']} ({naming['percentage_migrated']:.1f}%)")
    print(f"  - Without symbol prefix: {naming['without_symbol_prefix']}")
    
    if naming['percentage_migrated'] >= 95:
        print(f"✓ Most files have symbol prefix (>95%)")
        results['passed'].append('Naming pattern correct (>95% files with symbol prefix)')
    elif naming['percentage_migrated'] >= 80:
        print(f"⚠ Some files missing symbol prefix ({100-naming['percentage_migrated']:.1f}%)")
        results['warnings'].append(f"{100-naming['percentage_migrated']:.1f}% files missing symbol prefix")
    else:
        print(f"✗ Many files missing symbol prefix ({100-naming['percentage_migrated']:.1f}%)")
        results['errors'].append(f"Too many files missing symbol prefix ({100-naming['percentage_migrated']:.1f}%)")
    
    if naming['files_without_prefix']:
        print(f"\n  Files without prefix (sample):")
        for fname in naming['files_without_prefix'][:5]:
            print(f"    - {fname}")
        if len(naming['files_without_prefix']) > 5:
            print(f"    ... and {len(naming['files_without_prefix']) - 5} more")
    
    # Check 4: Backup
    print("\n[4/5] Checking backup...")
    backup_check = check_backup_exists()
    
    if backup_check['exists']:
        latest = backup_check['latest_backup']
        print(f"✓ Backup found: {backup_check['backups_found']} backup(s)")
        print(f"  - Latest: {latest['timestamp']}")
        print(f"  - Files backed up: {latest['files_backed_up']}")
        results['passed'].append('Backup exists and is accessible')
    else:
        print(f"✗ No backup found")
        results['warnings'].append('No backup found - migration may have run with --no-backup')
    
    # Check 5: Symbol distribution
    print("\n[5/5] Analyzing symbol distribution...")
    symbols = check_symbol_distribution()
    
    print(f"✓ Symbols found: {symbols['symbols_found']}")
    if symbols['distribution']:
        print(f"\n  Top symbols:")
        for symbol, count in list(symbols['distribution'].items())[:5]:
            print(f"    {symbol}: {count} files")
    
    # Final summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    print(f"\n✓ Passed checks: {len(results['passed'])}")
    for check in results['passed']:
        print(f"  - {check}")
    
    if results['warnings']:
        print(f"\n⚠ Warnings: {len(results['warnings'])}")
        for warning in results['warnings']:
            print(f"  - {warning}")
    
    if results['errors']:
        print(f"\n✗ Errors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"  - {error}")
    
    # Overall status
    print("\n" + "="*70)
    if not results['errors'] and len(results['warnings']) <= 1:
        print("✅ MIGRATION SUCCESSFUL - All checks passed!")
    elif not results['errors']:
        print("⚠️  MIGRATION COMPLETED WITH WARNINGS - Review above")
    else:
        print("❌ MIGRATION ISSUES DETECTED - Review errors above")
        print("   Consider using rollback_migration.py to restore")
    print("="*70)


if __name__ == "__main__":
    run_verification()
