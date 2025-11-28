"""
Rollback Script - Restore HTML files from backup
=================================================
Restores HTML files from a previous backup in case of migration issues.

Author: Trading Analytics V2
Date: 2025-11-28
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime


# =============================================================================
# CONFIGURATION
# =============================================================================

BACKUP_DIR = Path(r"C:\TradeData\V2\backups")
HTML_REPORTS_DIR = Path(r"C:\TradeData\V2\outputs\html_reports")


# =============================================================================
# ROLLBACK FUNCTIONS
# =============================================================================

def list_available_backups() -> list:
    """List all available backups."""
    if not BACKUP_DIR.exists():
        return []
    
    backups = []
    for backup_path in sorted(BACKUP_DIR.iterdir(), reverse=True):
        if not backup_path.is_dir():
            continue
        
        manifest_path = backup_path / "manifest.json"
        if not manifest_path.exists():
            continue
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        backups.append({
            'path': backup_path,
            'timestamp': backup_path.name,
            'manifest': manifest
        })
    
    return backups


def restore_from_backup(backup_path: Path, dry_run: bool = False) -> dict:
    """Restore HTML files from a backup."""
    html_backup = backup_path / "html_reports"
    
    if not html_backup.exists():
        raise FileNotFoundError(f"Backup HTML directory not found: {html_backup}")
    
    stats = {
        'restored': 0,
        'errors': 0
    }
    
    # Clear current HTML files
    if not dry_run:
        print(f"Clearing current HTML files...")
        for html_file in HTML_REPORTS_DIR.glob("*.html"):
            html_file.unlink()
        
        # Also remove .bak files
        for bak_file in HTML_REPORTS_DIR.glob("*.bak"):
            bak_file.unlink()
    
    # Restore from backup
    print(f"Restoring files from backup...")
    for backup_file in html_backup.glob("*"):
        if not backup_file.is_file():
            continue
        
        dest_file = HTML_REPORTS_DIR / backup_file.name
        
        try:
            if not dry_run:
                shutil.copy2(backup_file, dest_file)
            print(f"{'[DRY RUN] ' if dry_run else ''}✓ Restored: {backup_file.name}")
            stats['restored'] += 1
        except Exception as e:
            print(f"❌ Error restoring {backup_file.name}: {e}")
            stats['errors'] += 1
    
    return stats


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main rollback workflow."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rollback HTML files from backup')
    parser.add_argument('--backup', type=str, help='Backup timestamp to restore (e.g., 20251128_140000)')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without executing')
    parser.add_argument('--list', action='store_true', help='List available backups')
    args = parser.parse_args()
    
    print("="*70)
    print("ROLLBACK HTML FILES FROM BACKUP")
    print("="*70)
    
    # List backups
    backups = list_available_backups()
    
    if args.list or not args.backup:
        print(f"\nAvailable backups ({len(backups)}):")
        if not backups:
            print("  No backups found")
            return
        
        for i, backup in enumerate(backups, 1):
            manifest = backup['manifest']
            print(f"\n{i}. Timestamp: {backup['timestamp']}")
            print(f"   Files backed up: {manifest.get('files_backed_up', 'N/A')}")
            print(f"   Backup type: {manifest.get('backup_type', 'N/A')}")
        
        if not args.backup:
            print("\nUse --backup <timestamp> to restore from a backup")
            return
    
    # Find requested backup
    backup_path = BACKUP_DIR / args.backup
    if not backup_path.exists():
        print(f"\n❌ Backup not found: {backup_path}")
        print(f"\nAvailable backups:")
        for backup in backups:
            print(f"  - {backup['timestamp']}")
        sys.exit(1)
    
    # Show backup info
    manifest_path = backup_path / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        print(f"\nBackup information:")
        print(f"  Timestamp: {args.backup}")
        print(f"  Files: {manifest.get('files_backed_up', 'N/A')}")
        print(f"  Type: {manifest.get('backup_type', 'N/A')}")
    
    # Confirm rollback
    if not args.dry_run:
        print(f"\n⚠️  WARNING: This will replace all current HTML files!")
        confirm = input(f"Proceed with rollback? [y/N]: ")
        if confirm.lower() != 'y':
            print("❌ Rollback cancelled")
            return
    
    # Execute rollback
    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Restoring from backup: {args.backup}\n")
    
    try:
        stats = restore_from_backup(backup_path, dry_run=args.dry_run)
        
        print("\n" + "="*70)
        print("ROLLBACK SUMMARY")
        print("="*70)
        print(f"Files restored: {stats['restored']}")
        print(f"Errors: {stats['errors']}")
        
        print(f"\n✓ Rollback {'simulation' if args.dry_run else 'completed'} successfully!")
        
        if args.dry_run:
            print("\nRun without --dry-run to execute the rollback.")
    
    except Exception as e:
        print(f"\n❌ Rollback failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
