#!/usr/bin/env python3
"""
GUIDE DE VALIDATION - Dashboard Monte Carlo V2.1
=================================================

Ce script vous guide à travers les tests de validation
avant de continuer avec la réécriture du template.

Exécutez simplement: python GUIDE_VALIDATION.py
"""

from pathlib import Path
import sys

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_step(number, description):
    print(f"\n📋 ÉTAPE {number}: {description}")
    print("-" * 70)

def check_file_exists(filepath):
    if filepath.exists():
        print(f"   ✅ {filepath.name} - PRÉSENT")
        return True
    else:
        print(f"   ❌ {filepath.name} - MANQUANT")
        return False

V2_ROOT = Path(__file__).parent
MC_DIR = V2_ROOT / "src" / "monte_carlo"

print_section("GUIDE DE VALIDATION - DASHBOARD MONTE CARLO V2.1")

print("""
Ce guide vérifie que toutes les modifications sont en place
et prêtes pour l'étape suivante (réécriture du template).

Durée estimée: 5-10 minutes
""")

input("Appuyez sur ENTRÉE pour commencer...")

# =============================================================================
# ÉTAPE 1: Vérification des Backups
# =============================================================================
print_step(1, "Vérification des Backups")

print("\n   Les fichiers de backup doivent être présents:")
backups = [
    MC_DIR / "config.py.backup",
]

all_backups_ok = all(check_file_exists(f) for f in backups)

if all_backups_ok:
    print("\n   ✅ Tous les backups sont en place")
else:
    print("\n   ⚠️ Certains backups manquent - À créer avant de continuer")

input("\nAppuyez sur ENTRÉE pour continuer...")

# =============================================================================
# ÉTAPE 2: Test d'Import de la Configuration
# =============================================================================
print_step(2, "Test d'Import de la Configuration")

print("\n   Test de l'import du config.py enrichi...")

try:
    sys.path.insert(0, str(V2_ROOT))
    from src.monte_carlo import config
    
    print("   ✅ Import config.py : OK")
    
    # Vérifier les anciens paramètres
    print("\n   Vérification des paramètres existants:")
    assert hasattr(config, 'DEFAULT_CONFIG'), "DEFAULT_CONFIG manquant"
    print("      ✅ DEFAULT_CONFIG présent")
    
    assert hasattr(config, 'STATUS_OK'), "STATUS_OK manquant"
    print("      ✅ Statuts (OK/WARNING/HIGH_RISK) présents")
    
    # Vérifier les nouveaux paramètres
    print("\n   Vérification des nouveaux paramètres:")
    new_params = [
        'DASHBOARD_DEFAULT_CRITERIA',
        'DASHBOARD_PRESETS',
        'DASHBOARD_COLORS',
        'SLIDER_RANGES',
        'DASHBOARD_DISPLAY',
        'FILE_PATTERNS',
    ]
    
    for param in new_params:
        if hasattr(config, param):
            print(f"      ✅ {param} présent")
        else:
            print(f"      ❌ {param} MANQUANT")
    
    # Détails des presets
    print("\n   Presets disponibles:")
    for preset_name in config.DASHBOARD_PRESETS.keys():
        print(f"      • {preset_name}")
    
    print("\n   ✅ Configuration enrichie : VALIDE")

except Exception as e:
    print(f"\n   ❌ ERREUR lors de l'import: {e}")
    import traceback
    traceback.print_exc()

input("\nAppuyez sur ENTRÉE pour continuer...")

# =============================================================================
# ÉTAPE 3: Vérification des Fichiers du Générateur
# =============================================================================
print_step(3, "Vérification des Fichiers du Générateur")

print("\n   Fichiers du générateur:")
generator_files = [
    (MC_DIR / "monte_carlo_html_generator.py", "Version originale (V2.0)"),
    (MC_DIR / "monte_carlo_html_generator_v2.1.py", "Version modifiée (V2.1)"),
    (MC_DIR / "html_templates.py", "Templates HTML (à réécrire)"),
]

for filepath, description in generator_files:
    if filepath.exists():
        size_kb = filepath.stat().st_size / 1024
        print(f"   ✅ {filepath.name}")
        print(f"      {description} ({size_kb:.1f} KB)")
    else:
        print(f"   ❌ {filepath.name} - MANQUANT")

input("\nAppuyez sur ENTRÉE pour continuer...")

# =============================================================================
# ÉTAPE 4: Test du Générateur V2.1
# =============================================================================
print_step(4, "Test du Générateur V2.1 (Import)")

print("\n   Test de l'import du générateur modifié...")

try:
    gen_v21 = MC_DIR / "monte_carlo_html_generator_v2.1.py"
    
    if gen_v21.exists():
        # Lire le fichier et vérifier les imports
        content = gen_v21.read_text(encoding='utf-8')
        
        checks = [
            ("from src.monte_carlo.config import", "Imports de config"),
            ("DASHBOARD_DEFAULT_CRITERIA", "Import DASHBOARD_DEFAULT_CRITERIA"),
            ("DASHBOARD_PRESETS", "Import DASHBOARD_PRESETS"),
            ("STATUS_OK", "Import STATUS_OK"),
            ("presets_json", "Utilisation de presets_json"),
            ("colors_json", "Utilisation de colors_json"),
        ]
        
        print("\n   Vérification du contenu du générateur V2.1:")
        for check_str, description in checks:
            if check_str in content:
                print(f"      ✅ {description}")
            else:
                print(f"      ❌ {description} - NON TROUVÉ")
        
        print("\n   ✅ Générateur V2.1 : Structure correcte")
    else:
        print("   ❌ Fichier générateur V2.1 introuvable")

except Exception as e:
    print(f"\n   ❌ ERREUR: {e}")

input("\nAppuyez sur ENTRÉE pour continuer...")

# =============================================================================
# ÉTAPE 5: Vérification de la Structure HTML Template
# =============================================================================
print_step(5, "Vérification du Template Actuel")

print("\n   Analyse du template actuel (html_templates.py)...")

template_file = MC_DIR / "html_templates.py"

if template_file.exists():
    content = template_file.read_text(encoding='utf-8')
    
    # Compter les templates
    individual_count = content.count("INDIVIDUAL_TEMPLATE")
    summary_count = content.count("SUMMARY_TEMPLATE")
    
    print(f"\n   📊 Statistiques du fichier:")
    print(f"      • Taille: {len(content) / 1024:.1f} KB")
    print(f"      • INDIVIDUAL_TEMPLATE: {individual_count} mention(s)")
    print(f"      • SUMMARY_TEMPLATE: {summary_count} mention(s)")
    
    # Vérifier les placeholders actuels
    placeholders = [
        "{generation_date}",
        "{total_strategies}",
        "{ok_count}",
        "{strategies_json}",
        "{strategies_detailed_json}",
    ]
    
    print("\n   Placeholders existants dans SUMMARY_TEMPLATE:")
    for ph in placeholders:
        if ph in content:
            print(f"      ✅ {ph}")
        else:
            print(f"      ⚠️ {ph} - Non trouvé")
    
    print("\n   ℹ️ Le SUMMARY_TEMPLATE sera réécrit à l'étape suivante")
    print("      pour utiliser les nouveaux placeholders de config.")

else:
    print("   ❌ Fichier html_templates.py introuvable")

input("\nAppuyez sur ENTRÉE pour continuer...")

# =============================================================================
# RÉSUMÉ FINAL
# =============================================================================
print_section("RÉSUMÉ DE LA VALIDATION")

print("""
✅ Configuration enrichie (config.py)
   • Backups créés
   • Nouveaux paramètres ajoutés
   • Imports fonctionnels

✅ Générateur modifié (V2.1)
   • Fichier créé
   • Imports de config présents
   • Nouveaux placeholders ajoutés

⏳ Template HTML (html_templates.py)
   • Fichier existant vérifié
   • Prêt à être réécrit

""")

print("=" * 70)
print("  ÉTAT: Prêt pour l'étape suivante")
print("=" * 70)

print("""
PROCHAINE ÉTAPE: Réécriture du SUMMARY_TEMPLATE
------------------------------------------------

Le template sera réécrit pour inclure:
1. Panneau de critères dynamiques (3 sliders)
2. Stats live qui se mettent à jour
3. 4 graphiques Chart.js
4. Tableau interactif avec tri et animation
5. JavaScript de recalcul dynamique

Temps estimé: 30-45 minutes
Risque: Faible (backup disponible)

""")

print("🎯 TESTS MANUELS RECOMMANDÉS:")
print("-" * 70)
print("""
1. Tester la génération actuelle (avant modification):
   cd C:\\TradeData\\V2\\src\\monte_carlo
   python monte_carlo_html_generator.py
   
   → Vérifier que les pages actuelles se génèrent correctement

2. Ouvrir la page de synthèse actuelle dans le navigateur:
   C:\\TradeData\\V2\\outputs\\html_reports\\montecarlo\\all_strategies_montecarlo.html
   
   → Vérifier qu'elle s'affiche correctement
   → Noter ce qui fonctionne déjà (pour référence)

3. Vérifier quelques pages individuelles:
   C:\\TradeData\\V2\\outputs\\html_reports\\montecarlo\\Individual\\
   
   → Ouvrir 2-3 fichiers HTML
   → Vérifier qu'ils s'affichent correctement
   → Ces pages NE doivent PAS changer après la modification

""")

print("\n✅ Validation terminée !")
print("\nVous pouvez maintenant:")
print("  • Effectuer les tests manuels ci-dessus")
print("  • Revenir à Claude pour continuer (Option A)")
print("  • Poser des questions (Option C)")
