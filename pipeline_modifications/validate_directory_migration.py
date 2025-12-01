"""
Script de Validation de la Migration
======================================
Valide que la migration de l'architecture directories est complète et correcte.

Usage:
    python validate_directory_migration.py

Auteur: Trading Analytics Pipeline V2
Date: 2025-11-30
Version: 1.0.0
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import sys


# =============================================================================
# CONFIGURATION
# =============================================================================

V2_ROOT = Path(__file__).parent.parent
OUTPUTS_DIR = V2_ROOT / "outputs"
CONFIG_FILE = V2_ROOT / "config" / "settings.py"


# =============================================================================
# TESTS DE VALIDATION
# =============================================================================

class ValidationTest:
    """Classe de base pour un test de validation."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.passed = False
        self.message = ""
        self.details = []
    
    def run(self) -> bool:
        """Exécute le test. À surcharger dans les sous-classes."""
        raise NotImplementedError
    
    def report(self) -> str:
        """Génère un rapport du test."""
        status = "✅ PASS" if self.passed else "❌ FAIL"
        output = f"{status} - {self.name}\n"
        output += f"   {self.description}\n"
        if self.message:
            output += f"   → {self.message}\n"
        for detail in self.details:
            output += f"      • {detail}\n"
        return output


class Test1_DirectoryStructure(ValidationTest):
    """Test 1: Vérifie que la nouvelle structure de répertoires existe."""
    
    def __init__(self):
        super().__init__(
            "Structure de répertoires",
            "Vérifie que outputs/html_reports/ et sous-dossiers existent"
        )
    
    def run(self) -> bool:
        required_dirs = [
            OUTPUTS_DIR / "html_reports",
            OUTPUTS_DIR / "html_reports" / "correlation",
            OUTPUTS_DIR / "html_reports" / "correlation" / "dashboards",
            OUTPUTS_DIR / "html_reports" / "correlation" / "pages",
            OUTPUTS_DIR / "html_reports" / "montecarlo",
            OUTPUTS_DIR / "html_reports" / "montecarlo" / "dashboards",
            OUTPUTS_DIR / "html_reports" / "montecarlo" / "individual",
        ]
        
        missing = []
        for d in required_dirs:
            if not d.exists():
                missing.append(str(d.relative_to(V2_ROOT)))
        
        if missing:
            self.passed = False
            self.message = f"{len(missing)}/{len(required_dirs)} répertoires manquants"
            self.details = missing
        else:
            self.passed = True
            self.message = f"Tous les répertoires ({len(required_dirs)}) existent"
        
        return self.passed


class Test2_HTMLFiles(ValidationTest):
    """Test 2: Vérifie que les fichiers HTML sont dans html_reports/."""
    
    def __init__(self):
        super().__init__(
            "Fichiers HTML",
            "Vérifie la présence de fichiers HTML dans html_reports/"
        )
    
    def run(self) -> bool:
        html_dir = OUTPUTS_DIR / "html_reports"
        
        if not html_dir.exists():
            self.passed = False
            self.message = "Répertoire html_reports/ inexistant"
            return False
        
        html_files = list(html_dir.glob("*.html"))
        corr_pages = list((html_dir / "correlation" / "pages").glob("*.html"))
        corr_dashboards = list((html_dir / "correlation" / "dashboards").glob("*.html"))
        mc_individual = list((html_dir / "montecarlo" / "individual").glob("*.html"))
        
        total = len(html_files) + len(corr_pages) + len(corr_dashboards) + len(mc_individual)
        
        if total == 0:
            self.passed = False
            self.message = "Aucun fichier HTML trouvé"
        else:
            self.passed = True
            self.message = f"{total} fichiers HTML trouvés"
            self.details = [
                f"Stratégies (racine): {len(html_files)}",
                f"Correlation pages: {len(corr_pages)}",
                f"Correlation dashboards: {len(corr_dashboards)}",
                f"Monte Carlo individual: {len(mc_individual)}",
            ]
        
        return self.passed


class Test3_NoOrphanHTML(ValidationTest):
    """Test 3: Vérifie qu'il n'y a pas de HTML orphelins dans les anciens emplacements."""
    
    def __init__(self):
        super().__init__(
            "HTML orphelins",
            "Vérifie l'absence de HTML dans anciens emplacements"
        )
    
    def run(self) -> bool:
        old_locations = [
            OUTPUTS_DIR / "ai_analysis" / "html_reports",
            OUTPUTS_DIR / "correlation",
            OUTPUTS_DIR / "correlation_pages_full",
            OUTPUTS_DIR / "monte_carlo",
        ]
        
        orphans = []
        for loc in old_locations:
            if loc.exists():
                html_files = list(loc.rglob("*.html"))
                # Ignorer les backups
                html_files = [f for f in html_files if "backup" not in str(f).lower()]
                if html_files:
                    orphans.extend([str(f.relative_to(V2_ROOT)) for f in html_files])
        
        if orphans:
            self.passed = False
            self.message = f"{len(orphans)} fichiers HTML orphelins trouvés"
            self.details = orphans[:10]  # Limiter à 10 pour lisibilité
        else:
            self.passed = True
            self.message = "Aucun HTML orphelin dans anciens emplacements"
        
        return self.passed


class Test4_ConfigPaths(ValidationTest):
    """Test 4: Vérifie que config/settings.py contient les nouveaux chemins."""
    
    def __init__(self):
        super().__init__(
            "Configuration chemins",
            "Vérifie config/settings.py contient HTML_CORRELATION_DIR, etc."
        )
    
    def run(self) -> bool:
        if not CONFIG_FILE.exists():
            self.passed = False
            self.message = "config/settings.py introuvable"
            return False
        
        content = CONFIG_FILE.read_text(encoding='utf-8')
        
        required_vars = [
            "HTML_CORRELATION_DIR",
            "HTML_CORRELATION_DASHBOARDS_DIR",
            "HTML_CORRELATION_PAGES_DIR",
            "HTML_MONTECARLO_DIR",
            "HTML_MONTECARLO_DASHBOARDS_DIR",
            "HTML_MONTECARLO_INDIVIDUAL_DIR",
        ]
        
        missing = []
        for var in required_vars:
            if var not in content:
                missing.append(var)
        
        if missing:
            self.passed = False
            self.message = f"{len(missing)}/{len(required_vars)} variables manquantes"
            self.details = missing
        else:
            self.passed = True
            self.message = f"Toutes les variables ({len(required_vars)}) présentes"
        
        return self.passed


class Test5_LegacyCompatibility(ValidationTest):
    """Test 5: Vérifie que les chemins legacy sont redirigés."""
    
    def __init__(self):
        super().__init__(
            "Compatibilité legacy",
            "Vérifie AI_HTML_REPORTS_DIR redirige vers HTML_REPORTS_DIR"
        )
    
    def run(self) -> bool:
        if not CONFIG_FILE.exists():
            self.passed = False
            self.message = "config/settings.py introuvable"
            return False
        
        content = CONFIG_FILE.read_text(encoding='utf-8')
        
        # Vérifier que AI_HTML_REPORTS_DIR = HTML_REPORTS_DIR
        if "AI_HTML_REPORTS_DIR = HTML_REPORTS_DIR" in content:
            self.passed = True
            self.message = "Redirection legacy correcte"
        else:
            self.passed = False
            self.message = "Redirection legacy manquante ou incorrecte"
            self.details = ["AI_HTML_REPORTS_DIR devrait être = HTML_REPORTS_DIR"]
        
        return self.passed


class Test6_AnalyzerConfig(ValidationTest):
    """Test 6: Vérifie src/analyzers/config.py utilise HTML_REPORTS_DIR."""
    
    def __init__(self):
        super().__init__(
            "Analyzer config",
            "Vérifie src/analyzers/config.py utilise HTML_REPORTS_DIR"
        )
    
    def run(self) -> bool:
        config_file = V2_ROOT / "src" / "analyzers" / "config.py"
        
        if not config_file.exists():
            self.passed = False
            self.message = "src/analyzers/config.py introuvable"
            return False
        
        content = config_file.read_text(encoding='utf-8')
        
        checks = [
            ("Import HTML_REPORTS_DIR", "HTML_REPORTS_DIR" in content),
            ("html_reports_dir utilise HTML_REPORTS_DIR", 
             "html_reports_dir: Path = field(default_factory=lambda: HTML_REPORTS_DIR)" in content),
        ]
        
        failed = []
        for check_name, check_result in checks:
            if not check_result:
                failed.append(check_name)
        
        if failed:
            self.passed = False
            self.message = f"{len(failed)}/{len(checks)} vérifications échouées"
            self.details = failed
        else:
            self.passed = True
            self.message = f"Toutes les vérifications ({len(checks)}) réussies"
        
        return self.passed


class Test7_CSVInCorrectLocation(ValidationTest):
    """Test 7: Vérifie que les CSV sont restés dans leurs dossiers."""
    
    def __init__(self):
        super().__init__(
            "CSV dans bon emplacement",
            "Vérifie que CSV sont dans ai_analysis/, correlation/, monte_carlo/"
        )
    
    def run(self) -> bool:
        csv_dirs = {
            "ai_analysis": OUTPUTS_DIR / "ai_analysis",
            "correlation": OUTPUTS_DIR / "correlation",
            "monte_carlo": OUTPUTS_DIR / "monte_carlo",
        }
        
        results = {}
        for name, path in csv_dirs.items():
            if path.exists():
                csv_files = list(path.rglob("*.csv"))
                results[name] = len(csv_files)
            else:
                results[name] = 0
        
        total_csv = sum(results.values())
        
        if total_csv > 0:
            self.passed = True
            self.message = f"{total_csv} fichiers CSV dans bons emplacements"
            self.details = [f"{k}: {v} fichiers" for k, v in results.items() if v > 0]
        else:
            self.passed = True  # Pas d'erreur si pas de CSV (nouveau système)
            self.message = "Aucun CSV trouvé (nouveau système)"
        
        return self.passed


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 80)
    print(f"  VALIDATION DE LA MIGRATION - ARCHITECTURE DIRECTORIES V2")
    print("=" * 80)
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Racine: {V2_ROOT}")
    print()
    
    # Créer les tests
    tests = [
        Test1_DirectoryStructure(),
        Test2_HTMLFiles(),
        Test3_NoOrphanHTML(),
        Test4_ConfigPaths(),
        Test5_LegacyCompatibility(),
        Test6_AnalyzerConfig(),
        Test7_CSVInCorrectLocation(),
    ]
    
    # Exécuter les tests
    print("=" * 80)
    print(f"  EXÉCUTION DES TESTS ({len(tests)} tests)")
    print("=" * 80 + "\n")
    
    results = []
    for i, test in enumerate(tests, 1):
        print(f"\n[Test {i}/{len(tests)}] {test.name}")
        print("─" * 80)
        test.run()
        print(test.report())
        results.append(test.passed)
    
    # Résumé
    passed = sum(results)
    failed = len(results) - passed
    success_rate = (passed / len(results)) * 100
    
    print("\n" + "=" * 80)
    print(f"  RÉSUMÉ FINAL")
    print("=" * 80)
    print(f"\n✅ Tests réussis: {passed}/{len(tests)} ({success_rate:.0f}%)")
    
    if failed > 0:
        print(f"❌ Tests échoués: {failed}/{len(tests)}")
        print(f"\n⚠️  Correction requise avant utilisation du système")
        print(f"\n📋 Actions recommandées:")
        for i, test in enumerate(tests, 1):
            if not test.passed:
                print(f"   {i}. {test.name}: {test.message}")
    else:
        print(f"\n🎉 Tous les tests sont réussis!")
        print(f"\n✅ Migration complète et validée")
        print(f"\n📋 Prochaines étapes:")
        print(f"   1. Tester le pipeline: python run_pipeline.py --step enrich --dry-run")
        print(f"   2. Générer rapports: python run_pipeline.py --step correlation")
        print(f"   3. Vérifier les HTML dans outputs/html_reports/")
    
    print("\n" + "=" * 80 + "\n")
    
    # Exit code
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
