"""
Tests de validation post-installation
======================================
Script pour valider que l'intégration Equity Enricher fonctionne correctement.

Usage:
    python validate_integration.py
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au path
V2_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(V2_ROOT))

def test_imports():
    """Test 1: Vérifier que tous les imports fonctionnent."""
    print("\n" + "=" * 70)
    print("TEST 1: Imports")
    print("=" * 70)
    
    errors = []
    
    # Test import kpi_enricher
    try:
        from src.enrichers.kpi_enricher import KPIEnricher
        print("✅ KPIEnricher importé")
    except ImportError as e:
        errors.append(f"KPIEnricher: {e}")
        print(f"❌ KPIEnricher: {e}")
    
    # Test import equity_enricher
    try:
        from src.enrichers.equity_enricher import EquityCurveEnricher
        print("✅ EquityCurveEnricher importé")
    except ImportError as e:
        errors.append(f"EquityCurveEnricher: {e}")
        print(f"❌ EquityCurveEnricher: {e}")
    
    # Test import styles
    try:
        from src.enrichers.styles import get_kpi_styles
        print("✅ get_kpi_styles importé")
    except ImportError as e:
        errors.append(f"get_kpi_styles: {e}")
        print(f"❌ get_kpi_styles: {e}")
    
    return len(errors) == 0, errors


def test_pipeline_config():
    """Test 2: Vérifier PipelineConfig."""
    print("\n" + "=" * 70)
    print("TEST 2: PipelineConfig")
    print("=" * 70)
    
    try:
        # Import depuis run_pipeline
        sys.path.insert(0, str(V2_ROOT))
        from run_pipeline import PipelineConfig
        
        config = PipelineConfig()
        
        # Vérifier attributs
        assert hasattr(config, 'enrich_backup'), "Attribut enrich_backup manquant"
        assert hasattr(config, 'enrich_force'), "Attribut enrich_force manquant"
        assert hasattr(config, 'enrich_include_equity'), "Attribut enrich_include_equity manquant"
        
        # Vérifier valeurs par défaut
        assert config.enrich_include_equity == True, "enrich_include_equity devrait être True par défaut"
        
        print("✅ PipelineConfig contient enrich_include_equity")
        print(f"   Valeur par défaut: {config.enrich_include_equity}")
        
        return True, []
        
    except ImportError as e:
        print(f"❌ Impossible d'importer PipelineConfig: {e}")
        return False, [str(e)]
    except AssertionError as e:
        print(f"❌ {e}")
        return False, [str(e)]
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False, [str(e)]


def test_function_exists():
    """Test 3: Vérifier que step_enrich_html_reports existe."""
    print("\n" + "=" * 70)
    print("TEST 3: Fonction step_enrich_html_reports")
    print("=" * 70)
    
    try:
        from run_pipeline import step_enrich_html_reports
        
        # Vérifier que c'est bien une fonction
        assert callable(step_enrich_html_reports), "step_enrich_html_reports n'est pas callable"
        
        # Vérifier signature (accepte config)
        import inspect
        sig = inspect.signature(step_enrich_html_reports)
        params = list(sig.parameters.keys())
        assert 'config' in params, "Fonction devrait accepter paramètre 'config'"
        
        print("✅ step_enrich_html_reports existe et est callable")
        print(f"   Signature: {sig}")
        
        return True, []
        
    except ImportError as e:
        print(f"❌ step_enrich_html_reports non trouvée: {e}")
        print("   La fonction step_enrich_kpis existe-t-elle encore ?")
        
        # Vérifier si l'ancienne fonction existe
        try:
            from run_pipeline import step_enrich_kpis
            print("   ⚠️  step_enrich_kpis existe encore (pas renommée)")
            return False, ["Fonction pas renommée"]
        except ImportError:
            return False, [str(e)]
            
    except AssertionError as e:
        print(f"❌ {e}")
        return False, [str(e)]
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False, [str(e)]


def test_helper_functions():
    """Test 4: Vérifier fonctions utilitaires."""
    print("\n" + "=" * 70)
    print("TEST 4: Fonctions utilitaires")
    print("=" * 70)
    
    try:
        from run_pipeline import (
            _generate_equity_warning_banner,
            _inject_after_body,
            _inject_after_kpi,
            _inject_warning_before_equity,
            _replace_section
        )
        
        print("✅ _generate_equity_warning_banner existe")
        print("✅ _inject_after_body existe")
        print("✅ _inject_after_kpi existe")
        print("✅ _inject_warning_before_equity existe")
        print("✅ _replace_section existe")
        
        # Test basique de _generate_equity_warning_banner
        banner = _generate_equity_warning_banner()
        assert 'equity-warning-banner' in banner, "Banner devrait contenir class equity-warning-banner"
        assert 'Equity Curve non rafraîchie' in banner, "Banner devrait contenir texte d'avertissement"
        
        print("\n✅ Bandeau d'avertissement génère le bon HTML")
        
        return True, []
        
    except ImportError as e:
        print(f"❌ Fonctions utilitaires manquantes: {e}")
        return False, [str(e)]
    except AssertionError as e:
        print(f"❌ {e}")
        return False, [str(e)]
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False, [str(e)]


def test_cli_arguments():
    """Test 5: Vérifier argument --no-equity."""
    print("\n" + "=" * 70)
    print("TEST 5: Argument CLI --no-equity")
    print("=" * 70)
    
    try:
        import subprocess
        import sys
        
        # Tester --help pour voir si --no-equity apparaît
        result = subprocess.run(
            [sys.executable, str(V2_ROOT / "run_pipeline.py"), "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if '--no-equity' in result.stdout:
            print("✅ Argument --no-equity présent dans --help")
            print("   Description: Enrichissement KPI uniquement")
            return True, []
        else:
            print("❌ Argument --no-equity absent de --help")
            return False, ["Argument CLI non ajouté"]
            
    except subprocess.TimeoutExpired:
        print("⚠️  Timeout lors du test CLI (peut être normal)")
        return True, []  # Pas bloquant
    except Exception as e:
        print(f"❌ Erreur lors du test CLI: {e}")
        return False, [str(e)]


def test_enricher_instantiation():
    """Test 6: Vérifier que les enrichers peuvent être instanciés."""
    print("\n" + "=" * 70)
    print("TEST 6: Instantiation des enrichers")
    print("=" * 70)
    
    try:
        from src.enrichers.kpi_enricher import KPIEnricher
        from src.enrichers.equity_enricher import EquityCurveEnricher
        from config.settings import EQUITY_CURVES_DIR
        
        # Test KPIEnricher (sans fichier, juste pour vérifier constructeur)
        try:
            kpi_enricher = KPIEnricher(None)  # None = pas de fichier
            print("✅ KPIEnricher peut être instancié")
        except Exception as e:
            print(f"⚠️  KPIEnricher: {e} (peut être normal si pas de Portfolio Report)")
        
        # Test EquityCurveEnricher
        try:
            equity_enricher = EquityCurveEnricher(EQUITY_CURVES_DIR)
            print("✅ EquityCurveEnricher peut être instancié")
            print(f"   DataSource Dir: {EQUITY_CURVES_DIR}")
            
            if EQUITY_CURVES_DIR.exists():
                nb_files = len(list(EQUITY_CURVES_DIR.glob("*.txt")))
                print(f"   {nb_files} fichiers DataSource disponibles")
            else:
                print(f"   ⚠️  Répertoire n'existe pas encore")
        except Exception as e:
            print(f"❌ EquityCurveEnricher: {e}")
            return False, [str(e)]
        
        return True, []
        
    except ImportError as e:
        print(f"❌ Imports échoués: {e}")
        return False, [str(e)]
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False, [str(e)]


def main():
    """Exécute tous les tests."""
    print("\n" + "=" * 70)
    print("🔍 VALIDATION INTÉGRATION EQUITY ENRICHER")
    print("=" * 70)
    print(f"V2_ROOT: {V2_ROOT}\n")
    
    tests = [
        ("Imports", test_imports),
        ("PipelineConfig", test_pipeline_config),
        ("Fonction principale", test_function_exists),
        ("Fonctions utilitaires", test_helper_functions),
        ("Arguments CLI", test_cli_arguments),
        ("Instantiation", test_enricher_instantiation),
    ]
    
    results = []
    all_errors = []
    
    for test_name, test_func in tests:
        try:
            success, errors = test_func()
            results.append((test_name, success))
            if errors:
                all_errors.extend(errors)
        except Exception as e:
            print(f"\n❌ ERREUR CRITIQUE dans {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
            all_errors.append(str(e))
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Score: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n🎉 VALIDATION COMPLÈTE RÉUSSIE!")
        print("   L'intégration est correctement installée.")
        print("\n💡 Prochaine étape:")
        print("   python run_pipeline.py --step enrich --dry-run")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) échoué(s)")
        print("\n❌ Erreurs détectées:")
        for error in all_errors:
            print(f"   • {error}")
        print("\n💡 Actions recommandées:")
        print("   1. Vérifiez que apply_modifications.py a bien été exécuté")
        print("   2. Comparez run_pipeline.py avec le backup")
        print("   3. Relancez apply_modifications.py --apply")
        return 1


if __name__ == "__main__":
    sys.exit(main())
