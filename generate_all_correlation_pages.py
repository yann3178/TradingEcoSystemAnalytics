"""
Génération COMPLÈTE des pages de corrélation (245 pages).

Ce script génère toutes les pages sans demander de confirmation.
"""

from pathlib import Path
import sys
import pandas as pd
import numpy as np

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent))

from src.generators.correlation_pages import CorrelationPagesGenerator


def create_mock_analyzer(scores_file: Path):
    """Crée un mock analyzer depuis les scores existants."""
    print(f"📂 Chargement des scores depuis : {scores_file.name}")
    
    # Charger les scores
    scores = pd.read_csv(scores_file, sep=';', encoding='utf-8-sig', decimal=',')
    
    print(f"   ✓ {len(scores)} stratégies chargées")
    
    # Renommer la colonne
    if 'Strategy_ID' in scores.columns and 'Strategy' not in scores.columns:
        scores = scores.rename(columns={'Strategy_ID': 'Strategy'})
    
    # Créer des matrices de corrélation simulées
    strategies = scores['Strategy'].tolist()
    n = len(strategies)
    
    print(f"   🎲 Création de matrices de corrélation simulées ({n}×{n})...")
    
    corr_matrix_lt = pd.DataFrame(
        np.random.rand(n, n) * 0.6 - 0.3,
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
    """Fonction principale."""
    
    print("=" * 70)
    print("📄 GÉNÉRATION COMPLÈTE DES PAGES DE CORRÉLATION")
    print("=" * 70)
    
    # Chemins
    correlation_dir = Path(r"C:\TradeData\V2\outputs\correlation")
    output_dir = Path(r"C:\TradeData\V2\outputs\correlation_pages_full")
    
    # Trouver le fichier de scores
    score_files = list(correlation_dir.glob("all_strategy_scores_*.csv"))
    
    if not score_files:
        print("\n❌ Aucun fichier de scores trouvé")
        return 1
    
    scores_file = max(score_files, key=lambda p: p.stat().st_mtime)
    
    print(f"\n📁 Fichier : {scores_file.name}\n")
    
    # Créer l'analyzer
    analyzer = create_mock_analyzer(scores_file)
    
    print(f"\n✅ Analyzer créé avec {len(analyzer.scores)} stratégies")
    
    # Confirmation
    print(f"\n⚠️  Vous allez générer {len(analyzer.scores)} pages HTML")
    print(f"   Destination : {output_dir}")
    print(f"   Temps estimé : ~1-2 minutes")
    
    confirm = input("\n   Continuer ? (O/n) : ").strip().lower()
    
    if confirm in ['n', 'non']:
        print("\n❌ Annulé")
        return 0
    
    # Générer !
    print("\n" + "=" * 70)
    print("🚀 GÉNÉRATION EN COURS...")
    print("=" * 70)
    
    generator = CorrelationPagesGenerator(analyzer)
    
    stats = generator.generate_all(
        output_dir=output_dir,
        top_n=15,
        verbose=True
    )
    
    # Résultats
    print("\n" + "=" * 70)
    print("✅ GÉNÉRATION TERMINÉE")
    print("=" * 70)
    
    print(f"\n📊 Résultats :")
    print(f"   ✅ Pages générées : {stats['generated']}/{stats['total']}")
    
    if stats['errors'] > 0:
        print(f"   ⚠️  Erreurs : {stats['errors']}")
        pct_success = (stats['generated'] / stats['total']) * 100
        print(f"   📈 Taux de réussite : {pct_success:.1f}%")
    
    print(f"\n📁 Emplacement : {output_dir}")
    
    # Lister quelques fichiers
    generated_files = sorted(output_dir.glob("*.html"))
    if generated_files:
        print(f"\n📄 Exemples de fichiers générés :")
        for f in generated_files[:10]:
            print(f"   • {f.name}")
        if len(generated_files) > 10:
            print(f"   ... et {len(generated_files) - 10} autres")
    
    print(f"\n💡 Prochaines étapes :")
    print(f"   1. Ouvrir quelques fichiers HTML pour vérifier")
    print(f"   2. Intégrer au pipeline run_pipeline.py")
    print(f"   3. Créer les liens croisés avec AI Analysis")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
