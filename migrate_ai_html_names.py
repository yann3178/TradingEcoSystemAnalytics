"""
Migration Script - Phase 2: Add Symbol Prefix to AI Analysis HTML Files
==========================================================================
Renames existing HTML files to include symbol prefix based on Portfolio Report mapping.

Author: Trading Analytics V2
Date: 2025-11-28
"""

import sys
import csv
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict


# =============================================================================
# CONFIGURATION
# =============================================================================

HTML_REPORTS_DIR = Path(r"C:\TradeData\V2\outputs\html_reports")
PORTFOLIO_REPORT = Path(r"C:\TradeData\V2\data\portfolio_reports\Portfolio_Report_V2_27112025.csv")
BACKUP_DIR = Path(r"C:\TradeData\V2\backups")
MAPPING_JSON = Path(r"C:\TradeData\V2\outputs\consolidated\strategy_mapping.json")


# =============================================================================
# STRATEGY MAPPER (Simple version for this script)
# =============================================================================

def load_strategy_to_symbols_mapping(portfolio_report: Path) -> Dict[str, List[str]]:
    """Load the mapping from Portfolio Report."""
    mapping = defaultdict(list)
    
    with open(portfolio_report, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            strategy_name = row.get('Strategie', '').strip()
            symbol = row.get('Symbol', '').strip()
            
            if strategy_name and symbol:
                if symbol not in mapping[strategy_name]:
                    mapping[strategy_name].append(symbol)
    
    # Sort symbols for consistency
    for strategy_name in mapping:
        mapping[strategy_name].sort()
    
    return dict(mapping)


# =============================================================================
# BACKUP FUNCTIONS
# =============================================================================

def create_backup(dry_run: bool = False) -> Path:
    """Create a full backup of the HTML reports directory."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = BACKUP_DIR / timestamp
    
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Creating backup: {backup_path}")
    
    if not dry_run:
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Copy all HTML files
        html_backup = backup_path / "html_reports"
        html_backup.mkdir(exist_ok=True)
        
        files_copied = 0
        for html_file in HTML_REPORTS_DIR.glob("*.html"):
            shutil.copy2(html_file, html_backup / html_file.name)
            files_copied += 1
        
        # Create manifest
        manifest = {
            'timestamp': timestamp,
            'source_dir': str(HTML_REPORTS_DIR),
            'files_backed_up': files_copied,
            'backup_type': 'pre_migration',
        }
        
        manifest_path = backup_path / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✓ Backed up {files_copied} files")
    
    return backup_path


# =============================================================================
# MIGRATION LOGIC
# =============================================================================

def find_html_files_to_migrate() -> List[Path]:
    """
    Find all HTML files that need migration (main strategy reports).
    Excludes correlation files, backups, and index files.
    """
    all_html = list(HTML_REPORTS_DIR.glob("*.html"))
    
    # Filter out files we don't want to migrate
    to_migrate = []
    for f in all_html:
        name = f.name
        
        # Skip correlation files
        if 'correlation' in name.lower():
            continue
        
        # Skip backup files
        if name.endswith('.bak'):
            continue
        
        # Skip index files
        if 'index' in name.lower():
            continue
        
        # Skip mobile enhancement
        if 'mobile-enhancement' in name.lower():
            continue
        
        to_migrate.append(f)
    
    return sorted(to_migrate)


def extract_strategy_name_from_filename(filename: str) -> str:
    """
    Extract strategy name from HTML filename.
    Removes the .html extension.
    """
    return filename.replace('.html', '')


def plan_migration(
    html_files: List[Path],
    strategy_mapping: Dict[str, List[str]]
) -> Tuple[List[Dict], List[str]]:
    """
    Plan the migration: determine which files need renaming and how.
    
    Returns:
        (migration_plan, warnings)
    """
    migration_plan = []
    warnings = []
    
    for html_file in html_files:
        strategy_name = extract_strategy_name_from_filename(html_file.name)
        
        # Look up symbols for this strategy
        symbols = strategy_mapping.get(strategy_name, [])
        
        if not symbols:
            warnings.append(f"No symbol found for: {strategy_name}")
            # Keep original name
            migration_plan.append({
                'old_path': html_file,
                'new_path': html_file,
                'strategy_name': strategy_name,
                'symbol': None,
                'action': 'keep_original',
                'reason': 'symbol_not_found'
            })
        elif len(symbols) == 1:
            # Single symbol - simple rename
            symbol = symbols[0]
            new_name = f"{symbol}_{strategy_name}.html"
            new_path = html_file.parent / new_name
            
            migration_plan.append({
                'old_path': html_file,
                'new_path': new_path,
                'strategy_name': strategy_name,
                'symbol': symbol,
                'action': 'rename',
                'reason': 'single_symbol'
            })
        else:
            # Multiple symbols - would need duplication (not happening based on our analysis)
            warnings.append(f"Multiple symbols found for {strategy_name}: {symbols}")
            # Take first symbol for now
            symbol = symbols[0]
            new_name = f"{symbol}_{strategy_name}.html"
            new_path = html_file.parent / new_name
            
            migration_plan.append({
                'old_path': html_file,
                'new_path': new_path,
                'strategy_name': strategy_name,
                'symbol': symbol,
                'action': 'rename',
                'reason': 'multiple_symbols_first_used'
            })
            warnings.append(f"  → Using first symbol: {symbol}")
    
    return migration_plan, warnings


def execute_migration(migration_plan: List[Dict], dry_run: bool = False):
    """Execute the migration plan."""
    stats = {
        'renamed': 0,
        'kept_original': 0,
        'errors': 0
    }
    
    for item in migration_plan:
        old_path = item['old_path']
        new_path = item['new_path']
        action = item['action']
        
        if action == 'keep_original':
            stats['kept_original'] += 1
            continue
        
        if action == 'rename':
            if old_path == new_path:
                # Already has correct name
                stats['kept_original'] += 1
                continue
            
            try:
                if not dry_run:
                    old_path.rename(new_path)
                print(f"{'[DRY RUN] ' if dry_run else ''}✓ Renamed: {old_path.name} → {new_path.name}")
                stats['renamed'] += 1
            except Exception as e:
                print(f"❌ Error renaming {old_path.name}: {e}")
                stats['errors'] += 1
    
    return stats


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_migration_report(
    migration_plan: List[Dict],
    warnings: List[str],
    stats: Dict,
    output_path: Path
):
    """Generate a detailed migration report."""
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_files': len(migration_plan),
        'statistics': stats,
        'warnings': warnings,
        'migration_details': [
            {
                'old_name': str(item['old_path'].name),
                'new_name': str(item['new_path'].name),
                'strategy_name': item['strategy_name'],
                'symbol': item['symbol'],
                'action': item['action'],
                'reason': item['reason']
            }
            for item in migration_plan
        ]
    }
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Migration report saved: {output_path}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main migration workflow."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate AI Analysis HTML files to include symbol prefix')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without executing')
    parser.add_argument('--no-backup', action='store_true', help='Skip backup creation')
    args = parser.parse_args()
    
    print("="*70)
    print("AI ANALYSIS HTML FILES MIGRATION")
    print("="*70)
    
    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made\n")
    
    # Step 1: Load strategy mapping
    print(f"\n[1/5] Loading strategy mapping from Portfolio Report...")
    if not PORTFOLIO_REPORT.exists():
        print(f"❌ Portfolio Report not found: {PORTFOLIO_REPORT}")
        sys.exit(1)
    
    strategy_mapping = load_strategy_to_symbols_mapping(PORTFOLIO_REPORT)
    print(f"✓ Loaded mapping for {len(strategy_mapping)} strategies")
    
    # Step 2: Find files to migrate
    print(f"\n[2/5] Finding HTML files to migrate...")
    html_files = find_html_files_to_migrate()
    print(f"✓ Found {len(html_files)} HTML files to process")
    
    if not html_files:
        print("\n⚠️  No files to migrate!")
        return
    
    # Step 3: Plan migration
    print(f"\n[3/5] Planning migration...")
    migration_plan, warnings = plan_migration(html_files, strategy_mapping)
    
    if warnings:
        print(f"\n⚠️  {len(warnings)} warnings:")
        for w in warnings[:10]:  # Show first 10
            print(f"  - {w}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more")
    
    # Show preview
    print(f"\nMigration preview (first 10):")
    for item in migration_plan[:10]:
        if item['action'] == 'rename':
            print(f"  {item['old_path'].name}")
            print(f"  → {item['new_path'].name}")
        else:
            print(f"  {item['old_path'].name} (keeping original)")
    
    if len(migration_plan) > 10:
        print(f"  ... and {len(migration_plan) - 10} more files")
    
    # Step 4: Create backup
    if not args.no_backup and not args.dry_run:
        print(f"\n[4/5] Creating backup...")
        backup_path = create_backup(dry_run=args.dry_run)
    else:
        print(f"\n[4/5] Skipping backup...")
        backup_path = None
    
    # Step 5: Execute migration
    print(f"\n[5/5] Executing migration...")
    
    if not args.dry_run:
        confirm = input(f"\n⚠️  Proceed with renaming {len(migration_plan)} files? [y/N]: ")
        if confirm.lower() != 'y':
            print("❌ Migration cancelled")
            return
    
    stats = execute_migration(migration_plan, dry_run=args.dry_run)
    
    # Generate report
    report_path = Path(r"C:\TradeData\V2\outputs\consolidated\migration_report.json")
    generate_migration_report(migration_plan, warnings, stats, report_path)
    
    # Summary
    print("\n" + "="*70)
    print("MIGRATION SUMMARY")
    print("="*70)
    print(f"Total files processed: {len(migration_plan)}")
    print(f"Files renamed: {stats['renamed']}")
    print(f"Files kept original: {stats['kept_original']}")
    print(f"Errors: {stats['errors']}")
    print(f"Warnings: {len(warnings)}")
    
    if backup_path and not args.dry_run:
        print(f"\n✓ Backup saved: {backup_path}")
    
    print(f"\n✓ Migration {'simulation' if args.dry_run else 'completed'} successfully!")
    
    if args.dry_run:
        print("\nRun without --dry-run to execute the migration.")


if __name__ == "__main__":
    main()
