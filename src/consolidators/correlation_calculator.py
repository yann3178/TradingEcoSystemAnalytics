"""
Calculateur de Corrélation V2 - Méthodologie Kevin Davey.

Fonctionnalités:
- Matrice de corrélation Long Terme (depuis START_YEAR)
- Matrice de corrélation Court Terme (derniers N mois)
- Score de corrélation par stratégie (méthode Davey)
- Identification des paires extrêmes
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Tuple, Optional, Any

from .config import DEFAULT_CONFIG, SCORE_THRESHOLDS, get_correlation_status


class CorrelationAnalyzer:
    """
    Analyseur de corrélation entre stratégies de trading.
    
    Utilisation:
        analyzer = CorrelationAnalyzer(consolidated_df)
        analyzer.run()
        analyzer.print_summary()
        analyzer.export_results('output_dir')
    """
    
    def __init__(
        self,
        data: pd.DataFrame,
        start_year_longterm: int = None,
        recent_months: int = None,
        correlation_threshold: float = None,
        min_common_days_longterm: int = None,
        min_common_days_recent: int = None,
        min_active_days: int = None,
        weight_longterm: float = None,
        weight_recent: float = None,
        correlation_method: str = None,
    ):
        """
        Initialise l'analyseur de corrélation.
        
        Args:
            data: DataFrame avec colonnes Date, Strategy_Name, Symbol, DailyProfit
            start_year_longterm: Année de début pour analyse long terme
            recent_months: Nombre de mois pour analyse court terme
            correlation_threshold: Seuil pour considérer deux stratégies corrélées
            min_common_days_longterm: Jours communs minimum pour LT
            min_common_days_recent: Jours communs minimum pour CT
            min_active_days: Jours d'activité minimum pour inclure une stratégie
            weight_longterm: Poids du score LT dans le score Davey
            weight_recent: Poids du score CT dans le score Davey
            correlation_method: Méthode de corrélation ('pearson', 'spearman', 'kendall')
        """
        # Paramètres avec valeurs par défaut
        self.start_year_longterm = start_year_longterm or DEFAULT_CONFIG['start_year_longterm']
        self.recent_months = recent_months or DEFAULT_CONFIG['recent_months']
        self.correlation_threshold = correlation_threshold or DEFAULT_CONFIG['correlation_threshold']
        self.min_common_days_longterm = min_common_days_longterm or DEFAULT_CONFIG['min_common_days_longterm']
        self.min_common_days_recent = min_common_days_recent or DEFAULT_CONFIG['min_common_days_recent']
        self.min_active_days = min_active_days or DEFAULT_CONFIG['min_active_days']
        self.weight_longterm = weight_longterm or DEFAULT_CONFIG['weight_longterm']
        self.weight_recent = weight_recent or DEFAULT_CONFIG['weight_recent']
        self.correlation_method = correlation_method or DEFAULT_CONFIG['correlation_method']
        
        # Préparer les données
        self.data = self._prepare_data(data)
        
        # Résultats
        self.corr_matrix_lt: Optional[pd.DataFrame] = None
        self.corr_matrix_ct: Optional[pd.DataFrame] = None
        self.common_days_lt: Optional[pd.DataFrame] = None
        self.common_days_ct: Optional[pd.DataFrame] = None
        self.delta_matrix: Optional[pd.DataFrame] = None
        self.scores: Optional[pd.DataFrame] = None
        self.stats_lt: Optional[Dict] = None
        self.stats_ct: Optional[Dict] = None
        self.run_timestamp: Optional[datetime] = None
    
    def _prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prépare et valide les données."""
        df = df.copy()
        
        # Vérifier les colonnes requises
        required_cols = ['Date', 'DailyProfit']
        strategy_col = None
        for col in ['Strategy_ID', 'Strategy_Name', 'Strategie']:
            if col in df.columns:
                strategy_col = col
                break
        
        if strategy_col is None:
            raise ValueError("Colonne de stratégie non trouvée (Strategy_ID, Strategy_Name, ou Strategie)")
        
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Colonne requise manquante: {col}")
        
        # Convertir la date
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
            df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
        
        df = df.dropna(subset=['Date'])
        
        # Créer Strategy_ID si nécessaire
        if 'Strategy_ID' not in df.columns:
            if 'Symbol' in df.columns:
                df['Strategy_ID'] = df[strategy_col].astype(str) + '_' + df['Symbol'].astype(str)
            else:
                df['Strategy_ID'] = df[strategy_col].astype(str)
        
        # Convertir DailyProfit
        df['DailyProfit'] = pd.to_numeric(df['DailyProfit'], errors='coerce').fillna(0)
        
        return df
    
    def run(self, verbose: bool = True) -> None:
        """
        Exécute l'analyse de corrélation complète.
        
        Args:
            verbose: Afficher la progression
        """
        self.run_timestamp = datetime.now()
        
        if verbose:
            print("=" * 70)
            print("📊 ANALYSE DE CORRÉLATION - Méthode Kevin Davey")
            print("=" * 70)
        
        # Définir les périodes
        end_date = self.data['Date'].max()
        start_date_ct = end_date - relativedelta(months=self.recent_months)
        start_date_lt = datetime(self.start_year_longterm, 1, 1)
        
        if verbose:
            print(f"\n📅 Périodes d'analyse:")
            print(f"   Long Terme: {start_date_lt.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")
            print(f"   Court Terme: {start_date_ct.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')} ({self.recent_months} mois)")
        
        # Filtrer les données par période
        data_lt = self.data[self.data['Date'] >= start_date_lt]
        data_ct = self.data[self.data['Date'] >= start_date_ct]
        
        if verbose:
            print(f"\n📈 Données:")
            print(f"   Long Terme: {len(data_lt):,} lignes, {data_lt['Strategy_ID'].nunique()} stratégies")
            print(f"   Court Terme: {len(data_ct):,} lignes, {data_ct['Strategy_ID'].nunique()} stratégies")
        
        # Construire les matrices de profit
        if verbose:
            print("\n🔧 Construction des matrices de profit...")
        
        matrix_lt = build_profit_matrix(data_lt)
        matrix_ct = build_profit_matrix(data_ct)
        
        # Filtrer les stratégies actives
        matrix_lt = filter_active_strategies(matrix_lt, self.min_active_days)
        matrix_ct = filter_active_strategies(matrix_ct, max(10, self.min_active_days // 5))
        
        if verbose:
            print(f"   Long Terme: {len(matrix_lt.columns)} stratégies actives")
            print(f"   Court Terme: {len(matrix_ct.columns)} stratégies actives")
        
        # Calculer les matrices de corrélation
        if verbose:
            print("\n📊 Calcul des corrélations...")
        
        self.corr_matrix_lt, self.common_days_lt = calculate_correlation_matrix(
            matrix_lt, self.min_common_days_longterm, self.correlation_method
        )
        
        self.corr_matrix_ct, self.common_days_ct = calculate_correlation_matrix(
            matrix_ct, self.min_common_days_recent, self.correlation_method
        )
        
        if verbose:
            print(f"   Long Terme: {len(self.corr_matrix_lt)}×{len(self.corr_matrix_lt)} matrice")
            print(f"   Court Terme: {len(self.corr_matrix_ct)}×{len(self.corr_matrix_ct)} matrice")
        
        # Calculer la matrice delta
        self.delta_matrix = calculate_delta_matrix(self.corr_matrix_lt, self.corr_matrix_ct)
        
        # Calculer les scores Davey
        if verbose:
            print("\n🎯 Calcul des scores Davey...")
        
        self.scores = calculate_davey_scores(
            self.corr_matrix_lt,
            self.corr_matrix_ct,
            self.correlation_threshold,
            self.weight_longterm,
            self.weight_recent
        )
        
        # Statistiques
        self.stats_lt = compute_matrix_statistics(self.corr_matrix_lt, "Long Terme")
        self.stats_ct = compute_matrix_statistics(self.corr_matrix_ct, "Court Terme")
        
        if verbose:
            print(f"\n✅ Analyse terminée en {(datetime.now() - self.run_timestamp).total_seconds():.1f}s")
            print(f"   {len(self.scores)} stratégies analysées")
    
    def get_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des résultats."""
        if self.scores is None:
            return {}
        
        # Compter par statut
        status_counts = self.scores['Status'].value_counts().to_dict()
        
        return {
            'nb_strategies': len(self.scores),
            'avg_score_davey': round(self.scores['Score_Davey'].mean(), 2),
            'nb_diversifying': status_counts.get('Diversifiant', 0),
            'nb_moderate': status_counts.get('Modéré', 0),
            'nb_correlated': status_counts.get('Corrélé', 0),
            'nb_highly_correlated': status_counts.get('Très corrélé', 0),
            'stats_lt': self.stats_lt,
            'stats_ct': self.stats_ct,
        }
    
    def print_summary(self):
        """Affiche un résumé des résultats."""
        if self.scores is None:
            print("Aucun résultat. Lancez run() d'abord.")
            return
        
        print()
        print("=" * 80)
        print("📊 RÉSUMÉ DE L'ANALYSE DE CORRÉLATION")
        print("=" * 80)
        
        # Statistiques par matrice
        print("\n📈 Statistiques des matrices:")
        for stats in [self.stats_lt, self.stats_ct]:
            if stats:
                print(f"\n   {stats['label']}:")
                print(f"      Stratégies: {stats['nb_strategies']}")
                print(f"      Paires valides: {stats['nb_pairs_valid']}/{stats['nb_pairs_total']}")
                print(f"      Corr. moyenne: {stats['corr_mean']:.3f}")
                print(f"      Corr. médiane: {stats['corr_median']:.3f}")
                print(f"      % haute corr. (>0.7): {stats['pct_high_corr']:.1f}%")
        
        # Distribution des scores
        print("\n🎯 Distribution des scores Davey:")
        status_counts = self.scores['Status'].value_counts()
        for status in ['Diversifiant', 'Modéré', 'Corrélé', 'Très corrélé']:
            count = status_counts.get(status, 0)
            pct = count / len(self.scores) * 100 if len(self.scores) > 0 else 0
            emoji = {'Diversifiant': '🟢', 'Modéré': '🟡', 'Corrélé': '🟠', 'Très corrélé': '🔴'}[status]
            print(f"   {emoji} {status}: {count} ({pct:.1f}%)")
        
        # Top stratégies les plus corrélées
        print("\n🔴 Top 10 stratégies les plus corrélées:")
        print("-" * 70)
        top_corr = self.scores.head(10)
        for _, row in top_corr.iterrows():
            print(f"   {row['Status_Emoji']} {row['Strategy'][:40]:<40} Score: {row['Score_Davey']:.1f}")
        
        # Top stratégies diversifiantes
        print("\n🟢 Top 10 stratégies diversifiantes:")
        print("-" * 70)
        top_div = self.scores.tail(10).iloc[::-1]
        for _, row in top_div.iterrows():
            print(f"   {row['Status_Emoji']} {row['Strategy'][:40]:<40} Score: {row['Score_Davey']:.1f}")
        
        print()
    
    def export_csv(self, output_dir: Path, prefix: str = "correlation") -> Dict[str, Path]:
        """
        Exporte les résultats en CSV.
        
        Args:
            output_dir: Répertoire de sortie
            prefix: Préfixe des fichiers
            
        Returns:
            Dict avec les chemins des fichiers créés
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        files = {}
        
        # Scores
        if self.scores is not None:
            path = output_dir / f"{prefix}_scores_{timestamp}.csv"
            self.scores.to_csv(path, sep=';', decimal=',', index=False, encoding='utf-8-sig')
            files['scores'] = path
            print(f"📁 Scores exportés: {path}")
        
        # Matrice LT
        if self.corr_matrix_lt is not None:
            path = output_dir / f"{prefix}_matrix_lt_{timestamp}.csv"
            self.corr_matrix_lt.to_csv(path, sep=';', decimal=',', encoding='utf-8-sig')
            files['matrix_lt'] = path
            print(f"📁 Matrice LT exportée: {path}")
        
        # Matrice CT
        if self.corr_matrix_ct is not None:
            path = output_dir / f"{prefix}_matrix_ct_{timestamp}.csv"
            self.corr_matrix_ct.to_csv(path, sep=';', decimal=',', encoding='utf-8-sig')
            files['matrix_ct'] = path
            print(f"📁 Matrice CT exportée: {path}")
        
        return files


# ==============================================================================
# FONCTIONS UTILITAIRES
# ==============================================================================

def build_profit_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construit une matrice Date × Strategy avec les profits journaliers.
    
    Args:
        df: DataFrame avec colonnes Date, Strategy_ID, DailyProfit
        
    Returns:
        DataFrame pivot avec dates en index et stratégies en colonnes
    """
    profit_matrix = df.pivot_table(
        index='Date',
        columns='Strategy_ID',
        values='DailyProfit',
        aggfunc='sum',
        fill_value=0
    )
    return profit_matrix.sort_index()


def filter_active_strategies(profit_matrix: pd.DataFrame, min_active_days: int) -> pd.DataFrame:
    """
    Filtre les stratégies avec suffisamment de jours d'activité.
    
    Args:
        profit_matrix: Matrice de profits
        min_active_days: Minimum de jours avec activité (P&L != 0)
        
    Returns:
        Matrice filtrée
    """
    active_days = (profit_matrix != 0).sum()
    active_strategies = active_days[active_days >= min_active_days].index.tolist()
    return profit_matrix[active_strategies]


def calculate_correlation_matrix(
    profit_matrix: pd.DataFrame,
    min_common_days: int,
    method: str = 'pearson'
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calcule la matrice de corrélation avec filtre sur jours communs.
    
    Args:
        profit_matrix: Matrice de profits journaliers
        min_common_days: Jours communs minimum pour calculer une corrélation
        method: Méthode de corrélation ('pearson', 'spearman', 'kendall')
        
    Returns:
        Tuple (matrice de corrélation, matrice des jours communs)
    """
    strategies = profit_matrix.columns.tolist()
    n = len(strategies)
    
    corr_matrix = pd.DataFrame(np.nan, index=strategies, columns=strategies)
    common_days_matrix = pd.DataFrame(0, index=strategies, columns=strategies, dtype=int)
    
    for i, strat_i in enumerate(strategies):
        corr_matrix.loc[strat_i, strat_i] = 1.0
        common_days_matrix.loc[strat_i, strat_i] = (profit_matrix[strat_i] != 0).sum()
        
        for j in range(i + 1, n):
            strat_j = strategies[j]
            
            # Masque: jours où les deux stratégies ont tradé
            mask = (profit_matrix[strat_i] != 0) & (profit_matrix[strat_j] != 0)
            common_days = mask.sum()
            
            common_days_matrix.loc[strat_i, strat_j] = common_days
            common_days_matrix.loc[strat_j, strat_i] = common_days
            
            if common_days >= min_common_days:
                series_i = profit_matrix.loc[mask, strat_i]
                series_j = profit_matrix.loc[mask, strat_j]
                corr = series_i.corr(series_j, method=method)
                corr_matrix.loc[strat_i, strat_j] = corr
                corr_matrix.loc[strat_j, strat_i] = corr
    
    return corr_matrix, common_days_matrix


def calculate_delta_matrix(corr_lt: pd.DataFrame, corr_ct: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule la matrice de différence CT - LT.
    
    Args:
        corr_lt: Matrice de corrélation long terme
        corr_ct: Matrice de corrélation court terme
        
    Returns:
        Matrice delta (CT - LT)
    """
    common = list(set(corr_lt.columns) & set(corr_ct.columns))
    if len(common) == 0:
        return pd.DataFrame()
    
    delta = corr_ct.loc[common, common] - corr_lt.loc[common, common]
    return delta


def calculate_davey_scores(
    corr_lt: pd.DataFrame,
    corr_ct: pd.DataFrame,
    threshold: float,
    weight_lt: float,
    weight_ct: float
) -> pd.DataFrame:
    """
    Calcule les scores de corrélation selon la méthode Kevin Davey.
    
    Pour chaque stratégie:
    - N_corr_LT: Nombre de stratégies corrélées (|corr| > seuil) en Long Terme
    - N_corr_CT: Nombre de stratégies corrélées en Court Terme
    - Score_Davey: N_corr_LT × W_LT + N_corr_CT × W_CT
    
    Args:
        corr_lt: Matrice de corrélation long terme
        corr_ct: Matrice de corrélation court terme
        threshold: Seuil de corrélation
        weight_lt: Poids long terme
        weight_ct: Poids court terme
        
    Returns:
        DataFrame avec les scores par stratégie
    """
    # Stratégies communes aux deux matrices
    common_strategies = list(set(corr_lt.columns) & set(corr_ct.columns))
    
    scores = []
    
    for strat in common_strategies:
        # Long Terme
        lt_corrs = corr_lt.loc[strat].drop(strat, errors='ignore').dropna()
        n_corr_lt = (lt_corrs.abs() > threshold).sum()
        avg_corr_lt = lt_corrs.abs().mean() if len(lt_corrs) > 0 else 0
        max_corr_lt = lt_corrs.abs().max() if len(lt_corrs) > 0 else 0
        max_corr_lt_with = lt_corrs.abs().idxmax() if len(lt_corrs) > 0 else ""
        
        # Court Terme
        ct_corrs = corr_ct.loc[strat].drop(strat, errors='ignore').dropna()
        n_corr_ct = (ct_corrs.abs() > threshold).sum()
        avg_corr_ct = ct_corrs.abs().mean() if len(ct_corrs) > 0 else 0
        max_corr_ct = ct_corrs.abs().max() if len(ct_corrs) > 0 else 0
        max_corr_ct_with = ct_corrs.abs().idxmax() if len(ct_corrs) > 0 else ""
        
        # Score Davey combiné
        score_davey = n_corr_lt * weight_lt + n_corr_ct * weight_ct
        
        # Delta de corrélation moyenne
        delta_corr = avg_corr_ct - avg_corr_lt
        
        # Classification
        status, status_emoji = get_correlation_status(score_davey)
        
        scores.append({
            'Strategy': strat,
            'Score_Davey': round(score_davey, 1),
            'N_Corr_LT': int(n_corr_lt),
            'N_Corr_CT': int(n_corr_ct),
            'Avg_Corr_LT': round(avg_corr_lt, 3),
            'Avg_Corr_CT': round(avg_corr_ct, 3),
            'Delta_Corr': round(delta_corr, 3),
            'Max_Corr_LT': round(max_corr_lt, 3),
            'Max_Corr_LT_With': max_corr_lt_with,
            'Max_Corr_CT': round(max_corr_ct, 3),
            'Max_Corr_CT_With': max_corr_ct_with,
            'Status': status,
            'Status_Emoji': status_emoji
        })
    
    df_scores = pd.DataFrame(scores)
    df_scores = df_scores.sort_values('Score_Davey', ascending=False).reset_index(drop=True)
    
    return df_scores


def compute_matrix_statistics(corr_matrix: pd.DataFrame, label: str) -> Dict[str, Any]:
    """
    Calcule les statistiques d'une matrice de corrélation.
    
    Args:
        corr_matrix: Matrice de corrélation
        label: Nom de la matrice pour l'affichage
        
    Returns:
        Dictionnaire de statistiques
    """
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    values = corr_matrix.values[mask]
    values = values[~np.isnan(values)]
    
    return {
        'label': label,
        'nb_strategies': len(corr_matrix),
        'nb_pairs_valid': int(len(values)),
        'nb_pairs_total': len(corr_matrix) * (len(corr_matrix) - 1) // 2,
        'corr_mean': float(np.mean(values)) if len(values) > 0 else 0,
        'corr_median': float(np.median(values)) if len(values) > 0 else 0,
        'corr_std': float(np.std(values)) if len(values) > 0 else 0,
        'corr_min': float(np.min(values)) if len(values) > 0 else 0,
        'corr_max': float(np.max(values)) if len(values) > 0 else 0,
        'pct_high_corr': float((np.abs(values) > 0.7).mean() * 100) if len(values) > 0 else 0,
        'pct_low_corr': float((np.abs(values) < 0.3).mean() * 100) if len(values) > 0 else 0,
    }


def find_extreme_pairs(corr_matrix: pd.DataFrame, top_n: int = 20) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Trouve les paires avec corrélations extrêmes.
    
    Args:
        corr_matrix: Matrice de corrélation
        top_n: Nombre de paires à retourner
        
    Returns:
        Tuple (paires les plus corrélées, paires les moins corrélées)
    """
    pairs = []
    strategies = corr_matrix.columns.tolist()
    
    for i, strat_i in enumerate(strategies):
        for j in range(i + 1, len(strategies)):
            strat_j = strategies[j]
            corr = corr_matrix.loc[strat_i, strat_j]
            if not np.isnan(corr):
                pairs.append({
                    'Strategy_1': strat_i,
                    'Strategy_2': strat_j,
                    'Correlation': float(corr)
                })
    
    df_pairs = pd.DataFrame(pairs)
    if len(df_pairs) == 0:
        return pd.DataFrame(), pd.DataFrame()
    
    most = df_pairs.nlargest(top_n, 'Correlation')
    least = df_pairs.nsmallest(top_n, 'Correlation')
    
    return most, least
