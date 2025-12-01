"""
Test de génération des pages de corrélation individuelles.

Ce script teste le nouveau module CorrelationPagesGenerator
avec un échantillon réduit de stratégies.
"""

from pathlib import Path
import sys

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent))

from src.consolidators.correlation_calculator import CorrelationAnalyzer
from src.generators.correlation_pages import CorrelationPagesGenerator
import pandas as pd


def main():
    """Fonction principale de test."""
    
    print("=" * 70)
    print("🧪 TEST GÉNÉRATION PAGES DE CORRÉLATION INDIVIDUELLES")
    print("=" * 70)
    
    # Chemins
    consolidated_file = Path(r"C:\TradeData\V2\outputs\consolidated\consolidated_strategies.csv")
    test_output_dir = Path(r"C:\TradeData\V2\outputs\correlation_pages_test")
    
    # Vérifier que le fichier existe
    if not consolidated_file.exists():
        print(f"\n❌ Fichier consolidé introuvable: {consolidated_file}")
        return 1
    
    # Charger les données
    print(f"\n📂 Chargement des données...")
    print(f"   Source: {consolidated_file}")
    
    df = pd.read_csv(
        consolidated_file,
        sep=';',
        encoding='utf-8-sig',
        decimal=','
    )
    
    print(f"   ✓ {len(df):,} lignes chargées")
    print(f"   ✓ {df['Strategy_ID'].nunique()} stratégies uniques")
    
    # Créer l'analyseur
    print(f"\n🔧 Création de l'analyseur de corrélation...")
    analyzer = CorrelationAnalyzer(df)
    
    # Exécuter l'analyse
    print(f"\n📊 Analyse de corrélation en cours...")
    analyzer.run(verbose=True)
    
    # Afficher le résumé
    analyzer.print_summary()
    
    # TEST 1: Génération d'un petit échantillon (5 stratégies)
    print("\n" + "=" * 70)
    print("🧪 TEST 1: Génération de 5 pages (échantillon)")
    print("=" * 70)
    
    # Créer un générateur avec seulement 5 stratégies
    test_analyzer = analyzer
    test_analyzer.scores = analyzer.scores.head(5).copy()
    
    generator = CorrelationPagesGenerator(test_analyzer)
    
    stats = generator.generate_all(
        output_dir=test_output_dir / "sample_5",
        top_n=10,
        verbose=True
    )
    
    print(f"\n📊 Résultats TEST 1:")
    print(f"   ✅ Générées: {stats['generated']}/{stats['total']}")
    print(f"   ⚠️  Erreurs: {stats['errors']}")
    print(f"   📁 Emplacement: {test_output_dir / 'sample_5'}")
    
    # TEST 2: Génération complète (toutes les stratégies)
    print("\n" + "=" * 70)
    print("🧪 TEST 2: Génération complète (confirmation)")
    print("=" * 70)
    
    confirm = input(f"\nGénérer {len(analyzer.scores)} pages ? (o/N): ").strip().lower()
    
    if confirm == 'o':
        full_generator = CorrelationPagesGenerator(analyzer)
        
        full_stats = full_generator.generate_all(
            output_dir=test_output_dir / "full",
            top_n=15,
            verbose=True
        )
        
        print(f"\n📊 Résultats TEST 2:")
        print(f"   ✅ Générées: {full_stats['generated']}/{full_stats['total']}")
        print(f"   ⚠️  Erreurs: {full_stats['errors']}")
        print(f"   📁 Emplacement: {test_output_dir / 'full'}")
    else:
        print("\n⏭️  TEST 2 ignoré")
    
    # Résumé final
    print("\n" + "=" * 70)
    print("✅ TESTS TERMINÉS")
    print("=" * 70)
    print(f"\n📁 Résultats disponibles dans: {test_output_dir}")
    print(f"\n💡 Prochaines étapes:")
    print(f"   1. Ouvrir une page HTML dans {test_output_dir / 'sample_5'}")
    print(f"   2. Vérifier l'affichage et les données")
    print(f"   3. Si OK, intégrer au pipeline run_pipeline.py")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
