"""
Script d'intégration des pages de corrélation dans run_pipeline.py

Ce script modifie automatiquement run_pipeline.py pour ajouter
la génération des pages de corrélation individuelles.
"""

from pathlib import Path
import re

def integrate_correlation_pages():
    """Intègre la génération de pages dans step_correlation()."""
    
    pipeline_file = Path("run_pipeline.py")
    
    if not pipeline_file.exists():
        print(f"❌ Fichier introuvable: {pipeline_file}")
        return False
    
    print(f"📖 Lecture de {pipeline_file}...")
    content = pipeline_file.read_text(encoding='utf-8')
    
    # Vérifier si déjà intégré
    if 'CorrelationPagesGenerator' in content:
        print("✅ Les pages de corrélation sont déjà intégrées!")
        return True
    
    # Code à insérer
    pages_code = '''
        # Générer les pages individuelles de corrélation (NOUVEAU - V2.3.0)
        print("\\n📄 Génération des pages de corrélation individuelles...")
        try:
            from src.generators.correlation_pages import CorrelationPagesGenerator
            
            pages_output_dir = corr_output_dir / "pages"
            pages_generator = CorrelationPagesGenerator(analyzer)
            
            pages_stats = pages_generator.generate_all(
                output_dir=pages_output_dir,
                top_n=15,
                verbose=config.verbose
            )
            
            result['pages_generated'] = pages_stats['generated']
            result['pages_errors'] = pages_stats['errors']
            result['pages_path'] = str(pages_output_dir)
            
            print(f"✅ {pages_stats['generated']} pages de corrélation générées")
            
        except ImportError as e:
            print(f"⚠️  Module correlation_pages non trouvé: {e}")
            print("   Les pages individuelles ne seront pas générées")
        except Exception as e:
            print(f"⚠️  Erreur lors de la génération des pages: {e}")
            if config.verbose:
                import traceback
                traceback.print_exc()
        
'''
    
    # Trouver le point d'insertion (après export_dashboard dans step_correlation)
    # Chercher le pattern spécifique
    pattern = r"(# Générer le dashboard HTML si demandé.*?print\(f\"⚠️  Erreur lors de la génération du dashboard: \{e\}\"\))\s+(# Collecter les statistiques)"
    
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ Point d'insertion non trouvé dans step_correlation()")
        print("   Recherche d'un pattern alternatif...")
        
        # Pattern alternatif plus simple
        pattern2 = r"(exported_files\['dashboard'\] = dashboard_path.*?except Exception as e:.*?print\(f\"⚠️  Erreur lors de la génération du dashboard: \{e\}\"\))\s*\n\s*(# Collecter les statistiques)"
        
        match = re.search(pattern2, content, re.DOTALL)
        
        if not match:
            print("❌ Impossible de trouver le point d'insertion automatiquement")
            print("\n💡 Modification manuelle requise:")
            print("   1. Ouvrir run_pipeline.py")
            print("   2. Chercher 'def step_correlation'")
            print("   3. Trouver la ligne: # Collecter les statistiques")
            print("   4. Insérer le code ci-dessous JUSTE AVANT cette ligne:")
            print("\n" + pages_code)
            return False
    
    # Faire le remplacement
    new_content = re.sub(
        pattern if pattern else pattern2,
        r'\1' + pages_code + r'\2',
        content
    )
    
    # Sauvegarder une backup
    backup_file = pipeline_file.with_suffix('.py.backup')
    print(f"💾 Sauvegarde de l'original: {backup_file}")
    pipeline_file.rename(backup_file)
    backup_file.rename(pipeline_file)  # Restore
    import shutil
    shutil.copy2(pipeline_file, backup_file)
    
    # Écrire le nouveau contenu
    print(f"✏️  Modification de {pipeline_file}...")
    pipeline_file.write_text(new_content, encoding='utf-8')
    
    # Mettre à jour la version
    new_content = new_content.replace('Version: 2.2.0', 'Version: 2.3.0')
    pipeline_file.write_text(new_content, encoding='utf-8')
    
    print("✅ Intégration réussie!")
    print(f"\n📝 Modifications:")
    print(f"   • Ajout de CorrelationPagesGenerator dans step_correlation()")
    print(f"   • Version mise à jour: 2.2.0 → 2.3.0")
    print(f"   • Backup créé: {backup_file}")
    
    return True


def main():
    """Fonction principale."""
    print("=" * 70)
    print("🔧 INTÉGRATION DES PAGES DE CORRÉLATION AU PIPELINE")
    print("=" * 70)
    
    success = integrate_correlation_pages()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ INTÉGRATION TERMINÉE")
        print("=" * 70)
        print("\n🧪 Pour tester:")
        print("   python run_pipeline.py --step correlation")
        print("\n📊 Les pages seront générées dans:")
        print("   outputs/correlation/{timestamp}/pages/")
    else:
        print("\n" + "=" * 70)
        print("❌ ÉCHEC DE L'INTÉGRATION AUTOMATIQUE")
        print("=" * 70)
        print("\n💡 Intégration manuelle requise (voir instructions ci-dessus)")
    
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
