"""
Test de génération des pages de corrélation - Version Simplifiée.

Ce script utilise les résultats de corrélation EXISTANTS
au lieu de recalculer (car pas de données consolidées).
"""

from pathlib import Path
import sys
import pandas as pd
import numpy as np

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent))

from src.generators.correlation_pages import CorrelationPagesGenerator


def create_mock_analyzer(scores_file: Path, output_dir: Path):
    """
    Crée un mock analyzer depuis les scores existants.
    
    Args:
        scores_file: Fichier CSV des scores
        output_dir: Répertoire de sortie
        
    Returns:
        Mock analyzer avec les données minimales nécessaires
    """
    print(f"\n📂 Chargement des scores depuis : {scores_file}")
    
    # Charger les scores
    scores = pd.read_csv(scores_file, sep=';', encoding='utf-8-sig', decimal=',')
    
    print(f"   ✓ {len(scores)} stratégies chargées")
    print(f"   Colonnes: {list(scores.columns)}")
    
    # Renommer la colonne pour correspondre à ce qu'attend le générateur
    if 'Strategy_ID' in scores.columns and 'Strategy' not in scores.columns:
        scores = scores.rename(columns={'Strategy_ID': 'Strategy'})
        print(f"   ✓ Colonne 'Strategy_ID' renommée en 'Strategy'")
    
    # Créer des matrices de corrélation mock
    strategies = scores['Strategy'].tolist()
    n = len(strategies)
    
    print(f"   🎲 Création de matrices de corrélation simulées ({n}×{n})...")
    
    # Matrices avec corrélations aléatoires pour le test
    corr_matrix_lt = pd.DataFrame(
        np.random.rand(n, n) * 0.6 - 0.3,  # Corrélations entre -0.3 et 0.3
        index=strategies,
        columns=strategies
    )
    
    corr_matrix_ct = pd.DataFrame(
        np.random.rand(n, n) * 0.6 - 0.3,
        index=strategies,
        columns=strategies
    )
    
    # Diagonale = 1
    for i in range(n):
        corr_matrix_lt.iloc[i, i] = 1.0
        corr_matrix_ct.iloc[i, i] = 1.0
    
    # Créer un objet mock analyzer
    class MockAnalyzer:
        def __init__(self):
            self.scores = scores
            self.corr_matrix_lt = corr_matrix_lt
            self.corr_matrix_ct = corr_matrix_ct
            self.correlation_threshold = 0.70
            self.start_year_longterm = 2012
            self.recent_months = 12
    
    return MockAnalyzer()


def main():
    """Fonction principale de test."""
    
    print("=" * 70)
    print("🧪 TEST GÉNÉRATION PAGES DE CORRÉLATION (VERSION SIMPLIFIÉE)")
    print("=" * 70)
    
    # Chemins
    correlation_dir = Path(r"C:\TradeData\V2\outputs\correlation")
    test_output_dir = Path(r"C:\TradeData\V2\outputs\correlation_pages_test")
    
    # Trouver le fichier de scores le plus récent
    score_files = list(correlation_dir.glob("all_strategy_scores_*.csv"))
    
    if not score_files:
        print("\n❌ Aucun fichier de scores trouvé dans:")
        print(f"   {correlation_dir}")
        print("\n💡 Exécutez d'abord: python run_pipeline.py --step correlation")
        return 1
    
    scores_file = max(score_files, key=lambda p: p.stat().st_mtime)
    
    print(f"\n📁 Fichier de scores trouvé:")
    print(f"   {scores_file.name}")
    
    # Créer un mock analyzer
    try:
        analyzer = create_mock_analyzer(scores_file, test_output_dir)
        print(f"\n✅ Mock analyzer créé avec {len(analyzer.scores)} stratégies")
    except Exception as e:
        print(f"\n❌ Erreur lors de la création du mock analyzer:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # TEST 1: Génération d'un petit échantillon (5 stratégies)
    print("\n" + "=" * 70)
    print("🧪 TEST 1: Génération de 5 pages (échantillon)")
    print("=" * 70)
    
    # Créer un analyzer limité à 5 stratégies
    test_analyzer = analyzer
    test_analyzer.scores = analyzer.scores.head(5).copy()
    
    # Filtrer les matrices aussi
    test_strategies = test_analyzer.scores['Strategy'].tolist()
    test_analyzer.corr_matrix_lt = analyzer.corr_matrix_lt.loc[test_strategies, test_strategies]
    test_analyzer.corr_matrix_ct = analyzer.corr_matrix_ct.loc[test_strategies, test_strategies]
    
    # Créer le générateur
    try:
        generator = CorrelationPagesGenerator(test_analyzer)
        
        # Générer les pages
        stats = generator.generate_all(
            output_dir=test_output_dir / "sample_5",
            top_n=5,  # Réduit car seulement 5 stratégies au total
            verbose=True
        )
        
        print(f"\n📊 Résultats TEST 1:")
        print(f"   ✅ Générées: {stats['generated']}/{stats['total']}")
        print(f"   ⚠️  Erreurs: {stats['errors']}")
        print(f"   📁 Emplacement: {test_output_dir / 'sample_5'}")
        
        # Lister les fichiers générés
        generated_files = list((test_output_dir / "sample_5").glob("*.html"))
        if generated_files:
            print(f"\n📄 Fichiers générés:")
            for f in generated_files[:5]:
                print(f"   • {f.name}")
                
    except Exception as e:
        print(f"\n❌ Erreur lors de la génération TEST 1:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # TEST 2: Génération complète (optionnel)
    print("\n" + "=" * 70)
    print("🧪 TEST 2: Génération complète (confirmation)")
    print("=" * 70)
    
    confirm = input(f"\nGénérer {len(analyzer.scores)} pages ? (o/N): ").strip().lower()
    
    if confirm == 'o':
        try:
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
        except Exception as e:
            print(f"\n❌ Erreur lors de la génération TEST 2:")
            print(f"   {e}")
            import traceback
            traceback.print_exc()
            return 1
    else:
        print("\n⏭️  TEST 2 ignoré")
    
    # Résumé final
    print("\n" + "=" * 70)
    print("✅ TESTS TERMINÉS")
    print("=" * 70)
    print(f"\n📁 Résultats disponibles dans: {test_output_dir}")
    print(f"\n⚠️  NOTE IMPORTANTE:")
    print(f"   Les matrices de corrélation sont SIMULÉES (aléatoires)")
    print(f"   pour ce test. Les scores sont RÉELS (depuis {scores_file.name})")
    print(f"\n💡 Pour générer avec les vraies corrélations:")
    print(f"   1. Exécuter: python run_pipeline.py --step correlation")
    print(f"   2. Le générateur sera intégré au pipeline")
    print(f"\n🎯 Validation:")
    print(f"   • Ouvrir un fichier HTML dans {test_output_dir / 'sample_5'}")
    print(f"   • Vérifier que la page s'affiche correctement")
    print(f"   • Vérifier les tableaux et graphiques")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
