"""
Test rapide du générateur de Dashboard de Corrélation V2.
Vérifie que le module peut être importé et génère un HTML valide.
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au path
V2_ROOT = Path(__file__).parent
sys.path.insert(0, str(V2_ROOT))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def create_sample_data(n_strategies: int = 10, n_days: int = 500) -> pd.DataFrame:
    """Crée des données de test pour l'analyse de corrélation."""
    np.random.seed(42)
    
    strategies = [f"Strategy_{i:02d}_ES" for i in range(1, n_strategies + 1)]
    start_date = datetime(2020, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_days)]
    
    rows = []
    for strat in strategies:
        # Générer des profits journaliers avec un peu de corrélation
        base_trend = np.random.randn(n_days).cumsum() * 50
        noise = np.random.randn(n_days) * 200
        profits = base_trend + noise
        
        for i, date in enumerate(dates):
            # Simuler 30% de jours sans trade
            if np.random.random() > 0.3:
                rows.append({
                    'Date': date.strftime('%d/%m/%Y'),
                    'Strategy_Name': strat.split('_')[0] + '_' + strat.split('_')[1],
                    'Symbol': 'ES',
                    'DailyProfit': round(profits[i], 2)
                })
    
    return pd.DataFrame(rows)


def test_correlation_dashboard():
    """Test le générateur de dashboard de corrélation."""
    print("=" * 70)
    print("TEST DU GÉNÉRATEUR DE DASHBOARD DE CORRÉLATION")
    print("=" * 70)
    
    # Créer des données de test
    print("\n1. Création des données de test...")
    df = create_sample_data(n_strategies=15, n_days=400)
    print(f"   ✓ {len(df)} lignes créées")
    print(f"   ✓ {df['Strategy_Name'].nunique()} stratégies")
    
    # Importer et créer l'analyseur
    print("\n2. Import des modules...")
    try:
        from src.consolidators.correlation_calculator import CorrelationAnalyzer
        from src.generators.correlation_dashboard import CorrelationDashboardGenerator
        print("   ✓ Modules importés avec succès")
    except ImportError as e:
        print(f"   ✗ Erreur d'import: {e}")
        return False
    
    # Créer Strategy_ID
    df['Strategy_ID'] = df['Strategy_Name'] + '_' + df['Symbol']
    
    # Exécuter l'analyse
    print("\n3. Exécution de l'analyse de corrélation...")
    try:
        analyzer = CorrelationAnalyzer(
            data=df,
            start_year_longterm=2020,
            recent_months=6,
            correlation_threshold=0.70
        )
        analyzer.run(verbose=False)
        print(f"   ✓ Analyse terminée")
        print(f"   ✓ {len(analyzer.scores)} stratégies analysées")
    except Exception as e:
        print(f"   ✗ Erreur d'analyse: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Générer le dashboard
    print("\n4. Génération du dashboard HTML...")
    try:
        output_dir = V2_ROOT / "outputs" / "test_dashboard"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        dashboard_path = output_dir / f"test_correlation_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        analyzer.export_dashboard(dashboard_path)
        
        print(f"   ✓ Dashboard généré: {dashboard_path}")
        
        # Vérifier le contenu
        content = dashboard_path.read_text(encoding='utf-8')
        checks = [
            ('DOCTYPE html', 'Structure HTML'),
            ('Analyse de Corrélation', 'Titre'),
            ('scoresData', 'Données JavaScript'),
            ('showTab', 'Navigation'),
            ('heatmapLT', 'Heatmap Long Terme'),
            ('heatmapCT', 'Heatmap Court Terme'),
            ('Méthodologie', 'Onglet Méthodologie'),
        ]
        
        all_ok = True
        for check, label in checks:
            if check in content:
                print(f"   ✓ {label} présent")
            else:
                print(f"   ✗ {label} MANQUANT")
                all_ok = False
        
        file_size = dashboard_path.stat().st_size
        print(f"\n   📊 Taille du fichier: {file_size / 1024:.1f} KB")
        
        if all_ok:
            print(f"\n✅ TEST RÉUSSI!")
            print(f"   Ouvrez le dashboard: {dashboard_path}")
        else:
            print(f"\n⚠️  TEST PARTIEL - Certains éléments manquent")
        
        return all_ok
        
    except Exception as e:
        print(f"   ✗ Erreur de génération: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_correlation_dashboard()
    sys.exit(0 if success else 1)
