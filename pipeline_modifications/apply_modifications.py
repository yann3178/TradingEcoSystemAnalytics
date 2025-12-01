"""
Script d'application automatique des modifications
===================================================
Ce script applique toutes les modifications nécessaires à run_pipeline.py
pour intégrer l'enrichissement Equity Curves.

Usage:
    python apply_modifications.py                 # Mode simulation (dry-run)
    python apply_modifications.py --apply         # Appliquer réellement
    python apply_pipeline.py --backup-only   # Créer backup seulement

Version: 1.0.0
Date: 2025-11-30
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

V2_ROOT = Path(r"C:\TradeData\V2")
PIPELINE_FILE = V2_ROOT / "run_pipeline.py"
BACKUP_DIR = V2_ROOT / "pipeline_modifications" / "backups"
NEW_FUNCTION_FILE = V2_ROOT / "pipeline_modifications" / "step_enrich_html_reports_NOUVEAU.py"


def create_backup():
    """Crée un backup timestampé du fichier pipeline."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"run_pipeline_backup_{timestamp}.py"
    
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PIPELINE_FILE, backup_path)
    
    print(f"✅ Backup créé: {backup_path}")
    return backup_path


def read_file(filepath):
    """Lit un fichier en gérant l'encoding."""
    for enc in ('utf-8', 'utf-8-sig', 'latin-1'):
        try:
            return filepath.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Impossible de lire {filepath}")


def apply_modifications(dry_run=True):
    """Applique toutes les modifications au fichier pipeline."""
    
    print("\n" + "=" * 70)
    print("🔧 APPLICATION DES MODIFICATIONS - run_pipeline.py")
    print("=" * 70)
    
    if dry_run:
        print("🔍 MODE DRY-RUN: Aucune modification ne sera effectuée\n")
    else:
        print("⚠️  MODE APPLICATION: Le fichier sera modifié!\n")
    
    # 1. Lire le fichier original
    print("📖 Lecture du fichier original...")
    content = read_file(PIPELINE_FILE)
    original_lines = len(content.splitlines())
    print(f"   {original_lines} lignes lues")
    
    # 2. Lire la nouvelle fonction
    print("\n📖 Lecture de la nouvelle fonction...")
    new_function = read_file(NEW_FUNCTION_FILE)
    print(f"   Fonction step_enrich_html_reports() chargée")
    
    # 3. MODIFICATION 1: Import EquityCurveEnricher
    print("\n🔧 Modification 1: Ajout import EquityCurveEnricher...")
    if 'from src.enrichers.equity_enricher import EquityCurveEnricher' in content:
        print("   ⏭️  Import déjà présent")
    else:
        old_import = "from src.enrichers.styles import get_kpi_styles"
        new_import = """from src.enrichers.kpi_enricher import KPIEnricher
from src.enrichers.equity_enricher import EquityCurveEnricher
from src.enrichers.styles import get_kpi_styles"""
        
        if old_import in content:
            # Remplacer aussi la ligne précédente pour avoir les 3 imports groupés
            old_block = """from src.enrichers.kpi_enricher import KPIEnricher
        from src.enrichers.styles import get_kpi_styles"""
            content = content.replace(old_block, new_import)
            print("   ✅ Import ajouté")
        else:
            print("   ⚠️  Pattern d'import non trouvé - manuel requis")
    
    # 4. MODIFICATION 2: Ajouter enrich_include_equity dans PipelineConfig
    print("\n🔧 Modification 2: Ajout config.enrich_include_equity...")
    if 'self.enrich_include_equity' in content:
        print("   ⏭️  Configuration déjà présente")
    else:
        old_config = "self.enrich_force = False  # Ré-enrichir même si déjà fait"
        new_config = """self.enrich_force = False  # Ré-enrichir même si déjà fait
        self.enrich_include_equity = True  # Enrichir avec equity curves"""
        
        if old_config in content:
            content = content.replace(old_config, new_config)
            print("   ✅ Configuration ajoutée")
        else:
            print("   ⚠️  Pattern de config non trouvé - manuel requis")
    
    # 5. MODIFICATION 3: Remplacer step_enrich_kpis par step_enrich_html_reports
    print("\n🔧 Modification 3: Remplacement fonction step_enrich_kpis...")
    
    # Trouver le début et la fin de la fonction
    start_marker = "def step_enrich_kpis(config: PipelineConfig)"
    end_marker = "def step_1b_harmonization(config: PipelineConfig)"
    
    if start_marker in content:
        start_idx = content.index(start_marker)
        end_idx = content.index(end_marker) if end_marker in content else len(content)
        
        # Extraire avant et après
        before = content[:start_idx]
        after = content[end_idx:]
        
        # Reconstruire avec nouvelle fonction
        content = before + new_function + "\n\n" + after
        print("   ✅ Fonction remplacée")
    else:
        print("   ⚠️  Fonction step_enrich_kpis non trouvée - manuel requis")
    
    # 6. MODIFICATION 4: Renommer appel dans run_pipeline()
    print("\n🔧 Modification 4: Mise à jour appel dans run_pipeline()...")
    old_call = "results['steps']['enrich'] = step_enrich_kpis(config)"
    new_call = "results['steps']['enrich'] = step_enrich_html_reports(config)"
    
    if old_call in content:
        content = content.replace(old_call, new_call)
        print("   ✅ Appel mis à jour")
    elif new_call in content:
        print("   ⏭️  Appel déjà à jour")
    else:
        print("   ⚠️  Appel non trouvé - manuel requis")
    
    # 7. MODIFICATION 5: Ajouter argument --no-equity
    print("\n🔧 Modification 5: Ajout argument CLI --no-equity...")
    if '--no-equity' in content:
        print("   ⏭️  Argument déjà présent")
    else:
        old_arg = """parser.add_argument(
        '--force',
        action='store_true',
        help="Forcer le ré-enrichissement même si déjà fait"
    )"""
        
        new_arg = """parser.add_argument(
        '--force',
        action='store_true',
        help="Forcer le ré-enrichissement même si déjà fait"
    )
    
    parser.add_argument(
        '--no-equity',
        action='store_true',
        help="Enrichissement KPI uniquement (sans equity curves)"
    )"""
        
        if old_arg in content:
            content = content.replace(old_arg, new_arg)
            print("   ✅ Argument CLI ajouté")
        else:
            print("   ⚠️  Pattern d'argument non trouvé - manuel requis")
    
    # 8. MODIFICATION 6: Ajouter config.enrich_include_equity dans main()
    print("\n🔧 Modification 6: Configuration dans main()...")
    if 'config.enrich_include_equity = not args.no_equity' in content:
        print("   ⏭️  Configuration déjà présente")
    else:
        old_main_config = "config.enrich_force = args.force"
        new_main_config = """config.enrich_force = args.force
    config.enrich_include_equity = not args.no_equity"""
        
        if old_main_config in content:
            content = content.replace(old_main_config, new_main_config)
            print("   ✅ Configuration main() ajoutée")
        else:
            print("   ⚠️  Pattern main() non trouvé - manuel requis")
    
    # 9. MODIFICATION 7: Mettre à jour docstring
    print("\n🔧 Modification 7: Mise à jour documentation...")
    old_doc = "1. Enrichissement HTML avec KPIs du Portfolio Report"
    new_doc = "1. Enrichissement HTML avec KPIs + Equity Curves"
    
    if old_doc in content:
        content = content.replace(old_doc, new_doc)
        print("   ✅ Documentation mise à jour")
    elif new_doc in content:
        print("   ⏭️  Documentation déjà à jour")
    
    # Statistiques finales
    modified_lines = len(content.splitlines())
    diff_lines = modified_lines - original_lines
    
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES MODIFICATIONS")
    print("=" * 70)
    print(f"Lignes originales : {original_lines}")
    print(f"Lignes modifiées  : {modified_lines}")
    print(f"Différence        : {diff_lines:+d} lignes")
    
    # Écrire le fichier si pas en dry-run
    if not dry_run:
        print("\n💾 Écriture du fichier modifié...")
        PIPELINE_FILE.write_text(content, encoding='utf-8')
        print(f"   ✅ Fichier sauvegardé: {PIPELINE_FILE}")
    else:
        # Sauvegarder preview
        preview_path = BACKUP_DIR / "run_pipeline_PREVIEW.py"
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        preview_path.write_text(content, encoding='utf-8')
        print(f"\n👁️  Preview sauvegardé: {preview_path}")
        print("   Comparez avec l'original avant d'appliquer")
    
    print("\n✅ Terminé!")
    
    if dry_run:
        print("\n💡 Pour appliquer réellement: python apply_modifications.py --apply")


def main():
    """Point d'entrée."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Applique les modifications à run_pipeline.py")
    parser.add_argument('--apply', action='store_true', help="Appliquer réellement (sinon dry-run)")
    parser.add_argument('--backup-only', action='store_true', help="Créer backup uniquement")
    
    args = parser.parse_args()
    
    # Vérifier que les fichiers existent
    if not PIPELINE_FILE.exists():
        print(f"❌ Fichier non trouvé: {PIPELINE_FILE}")
        sys.exit(1)
    
    if not NEW_FUNCTION_FILE.exists():
        print(f"❌ Fichier non trouvé: {NEW_FUNCTION_FILE}")
        print("   Assurez-vous d'avoir step_enrich_html_reports_NOUVEAU.py")
        sys.exit(1)
    
    # Créer backup
    print("📦 Création du backup...")
    backup_path = create_backup()
    
    if args.backup_only:
        print("\n✅ Backup créé uniquement")
        sys.exit(0)
    
    # Appliquer les modifications
    apply_modifications(dry_run=not args.apply)
    
    if args.apply:
        print(f"\n💾 Backup disponible: {backup_path}")
        print("   En cas de problème, restaurez avec:")
        print(f"   copy \"{backup_path}\" \"{PIPELINE_FILE}\"")


if __name__ == "__main__":
    main()
