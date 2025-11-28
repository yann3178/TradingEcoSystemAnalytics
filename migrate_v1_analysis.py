"""
Script de Migration V1 → V2 des Analyses IA
=============================================
Migre les résultats d'analyse depuis mc_ai_analysis (V1) vers V2
sans avoir à relancer les appels API Claude.

Usage:
    python migrate_v1_analysis.py [OPTIONS]

Options:
    --dry-run           Analyser sans écrire (voir mapping types)
    --force             Écraser fichiers existants V2
    --skip-html         Migrer données uniquement, pas de HTML
    --report-only       Générer uniquement le rapport de mapping types
    --verbose           Afficher détails
"""

import os
import sys
import csv
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field, asdict
from collections import Counter

# Ajouter le chemin V2 pour les imports
V2_ROOT = Path(__file__).parent
sys.path.insert(0, str(V2_ROOT))
sys.path.insert(0, str(V2_ROOT / "src"))

# =============================================================================
# CONFIGURATION
# =============================================================================

V1_ROOT = Path(r"C:\TradeData\mc_ai_analysis")
V1_CSV = V1_ROOT / "strategies_ai_analysis.csv"
V1_TRACKING = V1_ROOT / "strategy_tracking.json"
V1_HTML_REPORTS = V1_ROOT / "html_reports"

V2_OUTPUT = V2_ROOT / "outputs" / "ai_analysis"
V2_CSV = V2_OUTPUT / "strategies_ai_analysis.csv"
V2_TRACKING = V2_OUTPUT / "strategy_tracking.json"
V2_HTML_REPORTS = V2_OUTPUT / "html_reports"
V2_MIGRATION_REPORT = V2_OUTPUT / "migration_report.json"

STRATEGIES_SOURCE = Path(r"C:\MC_Export_Code\clean\Strategies")

# =============================================================================
# MAPPING V1 → V2
# =============================================================================

# Mapping des types V1 vers les catégories V2
TYPE_V1_TO_V2 = {
    # BREAKOUT
    'breakout': 'BREAKOUT',
    'breakout strategy': 'BREAKOUT',
    'session breakout': 'BREAKOUT',
    'session-based breakout': 'BREAKOUT',
    'intraday breakout': 'BREAKOUT',
    'channel breakout': 'BREAKOUT',
    'level breakout': 'BREAKOUT',
    'swing point breakout': 'BREAKOUT',
    'range expansion breakout': 'BREAKOUT',
    'pivot-based breakout': 'BREAKOUT',
    'volatility breakout': 'BREAKOUT',
    'momentum breakout': 'BREAKOUT',
    'bollinger band breakout': 'BREAKOUT',
    'multi-timeframe breakout with pattern filtering': 'BREAKOUT',
    'trend following breakout': 'BREAKOUT',
    'trend following / breakout': 'BREAKOUT',
    'breakout/deviation': 'BREAKOUT',
    
    # MEAN_REVERSION
    'reversal': 'MEAN_REVERSION',
    'mean reversion': 'MEAN_REVERSION',
    'mean reverting': 'MEAN_REVERSION',
    'mean reversal': 'MEAN_REVERSION',
    'countertrend/reversal': 'MEAN_REVERSION',
    'counter-trend reversal': 'MEAN_REVERSION',
    'reversal/fading strategy': 'MEAN_REVERSION',
    'reversal/counter-trend': 'MEAN_REVERSION',
    'reversal/mean reversion': 'MEAN_REVERSION',
    'bollinger band reversal': 'MEAN_REVERSION',
    'pivot point reversal': 'MEAN_REVERSION',
    'multi-timeframe mean reversion/breakout hybrid': 'MEAN_REVERSION',
    
    # TREND_FOLLOWING
    'trend following': 'TREND_FOLLOWING',
    'trend following / momentum': 'TREND_FOLLOWING',
    
    # PATTERN_PURE
    'pattern-based bias strategy': 'PATTERN_PURE',
    'pattern-based day trading': 'PATTERN_PURE',
    'pattern-based reversal/momentum': 'PATTERN_PURE',
    'intraday pattern-based trading': 'PATTERN_PURE',
    'stochastic oscillator with pattern recognition': 'PATTERN_PURE',
    'time-based pattern trading': 'PATTERN_PURE',
    'time-based pattern breakout': 'PATTERN_PURE',
    'time-based pattern strategy': 'PATTERN_PURE',
    
    # VOLATILITY
    'hybrid breakout/volatility-based': 'VOLATILITY',
    
    # BIAS_TEMPORAL
    'time-based bias strategy': 'BIAS_TEMPORAL',
    'time-based directional bias': 'BIAS_TEMPORAL',
    'time-based bias': 'BIAS_TEMPORAL',
    'time-based breakout': 'BIAS_TEMPORAL',
    'time-based weekly bias strategy': 'BIAS_TEMPORAL',
    'bias trading': 'BIAS_TEMPORAL',
    'bias/session-based': 'BIAS_TEMPORAL',
    'bias/time-based': 'BIAS_TEMPORAL',
    'bias/trend following': 'BIAS_TEMPORAL',
    'bias/seasonal': 'BIAS_TEMPORAL',
    'bias-based breakout': 'BIAS_TEMPORAL',
    'bias/breakout hybrid': 'BIAS_TEMPORAL',
    'day-of-week bias': 'BIAS_TEMPORAL',
    'day-of-week bias with breakout': 'BIAS_TEMPORAL',
    'seasonal/day-of-week bias': 'BIAS_TEMPORAL',
    'session-based bias trading': 'BIAS_TEMPORAL',
    'channel breakout / time-based bias': 'BIAS_TEMPORAL',
    
    # GAP_TRADING
    'gap trading': 'GAP_TRADING',
    'breakout/gap trading': 'GAP_TRADING',
    
    # HYBRID
    'dual-mode strategy': 'HYBRID',
    'hybrid breakout/reversal': 'HYBRID',
    'hybrid breakout/mean reversion': 'HYBRID',
    'breakout/mean reversion hybrid': 'HYBRID',
    'breakout/reversal hybrid': 'HYBRID',
    'pivot point breakout/reversal': 'HYBRID',
}

# Subtypes V2 standardisés par catégorie
STRATEGY_SUBTYPES = {
    'BREAKOUT': [
        'Session_Range', 'Daily_Range', 'Channel', 'Donchian', 'Bollinger',
        'Keltner', 'Pivot', 'Opening_Range', 'Swing_Point', 'Momentum',
        'ATR_Based', 'Multi_Timeframe'
    ],
    'MEAN_REVERSION': [
        'Bollinger_Bounce', 'RSI_Extreme', 'Pivot_Fade', 'False_Breakout',
        'VWAP', 'Stochastic'
    ],
    'TREND_FOLLOWING': [
        'MA_Crossover', 'Channel_Ride', 'Donchian_Trend', 'SuperTrend',
        'ADX_Momentum'
    ],
    'BIAS_TEMPORAL': [
        'Day_of_Week', 'Hour_of_Day', 'Session_Open', 'Session_Close',
        'Weekly_Cycle', 'Seasonal'
    ],
    'GAP_TRADING': [
        'Gap_Breakout', 'Gap_Fade', 'Gap_Reversal', 'Overnight_Gap'
    ],
    'HYBRID': [
        'Breakout_Reversal', 'Trend_MeanRev', 'Multi_Mode', 'Adaptive'
    ],
    'VOLATILITY': [
        'Expansion', 'Contraction', 'ATR_Regime', 'Low_Vol_Breakout'
    ],
    'PATTERN_PURE': [
        'Candlestick', 'Price_Action', 'Multi_Pattern'
    ],
}

# Mots-clés pour détecter le subtype V2
SUBTYPE_KEYWORDS = {
    # BREAKOUT
    'session': 'Session_Range',
    'session high': 'Session_Range',
    'session low': 'Session_Range',
    'daily': 'Daily_Range',
    'channel': 'Channel',
    'donchian': 'Donchian',
    'bollinger': 'Bollinger',
    'keltner': 'Keltner',
    'pivot': 'Pivot',
    'opening range': 'Opening_Range',
    'swing': 'Swing_Point',
    'momentum': 'Momentum',
    'atr': 'ATR_Based',
    'multi-timeframe': 'Multi_Timeframe',
    'multi timeframe': 'Multi_Timeframe',
    
    # MEAN_REVERSION
    'bollinger bounce': 'Bollinger_Bounce',
    'bollinger band': 'Bollinger_Bounce',
    'rsi': 'RSI_Extreme',
    'pivot fade': 'Pivot_Fade',
    'false breakout': 'False_Breakout',
    'vwap': 'VWAP',
    'stochastic': 'Stochastic',
    
    # TREND_FOLLOWING
    'ma crossover': 'MA_Crossover',
    'sma crossover': 'MA_Crossover',
    'sma': 'MA_Crossover',
    'moving average': 'MA_Crossover',
    'supertrend': 'SuperTrend',
    'adx': 'ADX_Momentum',
    
    # BIAS_TEMPORAL
    'day of week': 'Day_of_Week',
    'day-of-week': 'Day_of_Week',
    'hour': 'Hour_of_Day',
    'session open': 'Session_Open',
    'session close': 'Session_Close',
    'weekly': 'Weekly_Cycle',
    'seasonal': 'Seasonal',
    'bias': 'Day_of_Week',
    
    # GAP_TRADING
    'gap breakout': 'Gap_Breakout',
    'gap fade': 'Gap_Fade',
    'gap reversal': 'Gap_Reversal',
    'overnight': 'Overnight_Gap',
    
    # HYBRID
    'breakout reversal': 'Breakout_Reversal',
    'breakout/reversal': 'Breakout_Reversal',
    'multi mode': 'Multi_Mode',
    'adaptive': 'Adaptive',
    
    # VOLATILITY
    'expansion': 'Expansion',
    'contraction': 'Contraction',
    'low vol': 'Low_Vol_Breakout',
    
    # PATTERN_PURE
    'candlestick': 'Candlestick',
    'price action': 'Price_Action',
    'pattern filtering': 'Multi_Pattern',
    'pattern': 'Multi_Pattern',
}


# =============================================================================
# FONCTIONS DE MAPPING
# =============================================================================

def normalize_type_v1_to_v2(type_v1: str) -> str:
    """Convertit un type V1 vers une catégorie V2."""
    if not type_v1:
        return "HYBRID"
    
    type_lower = type_v1.lower().strip()
    
    # Correspondance exacte
    if type_lower in TYPE_V1_TO_V2:
        return TYPE_V1_TO_V2[type_lower]
    
    # Correspondance partielle (chercher dans les clés)
    for key, value in TYPE_V1_TO_V2.items():
        if key in type_lower or type_lower in key:
            return value
    
    # Fallbacks par mots-clés
    if 'breakout' in type_lower:
        return 'BREAKOUT'
    if 'reversal' in type_lower or 'reversion' in type_lower:
        return 'MEAN_REVERSION'
    if 'trend' in type_lower:
        return 'TREND_FOLLOWING'
    if 'bias' in type_lower or 'time' in type_lower or 'seasonal' in type_lower:
        return 'BIAS_TEMPORAL'
    if 'gap' in type_lower:
        return 'GAP_TRADING'
    if 'pattern' in type_lower:
        return 'PATTERN_PURE'
    if 'volatility' in type_lower:
        return 'VOLATILITY'
    if 'hybrid' in type_lower or 'dual' in type_lower:
        return 'HYBRID'
    
    return 'HYBRID'


def map_subtype_v1_to_v2(subtype_v1: str, type_v1: str, category_v2: str) -> str:
    """Mappe un subtype V1 vers un subtype V2 standardisé."""
    if not subtype_v1 and not type_v1:
        if category_v2 in STRATEGY_SUBTYPES:
            return STRATEGY_SUBTYPES[category_v2][0]
        return ""
    
    # Combiner subtype et type pour la recherche
    search_text = f"{subtype_v1} {type_v1}".lower()
    
    # Chercher les mots-clés
    for keyword, subtype in SUBTYPE_KEYWORDS.items():
        if keyword in search_text:
            # Vérifier que le subtype est valide pour la catégorie
            if category_v2 in STRATEGY_SUBTYPES:
                if subtype in STRATEGY_SUBTYPES[category_v2]:
                    return subtype
    
    # Défaut: premier subtype de la catégorie
    if category_v2 in STRATEGY_SUBTYPES and STRATEGY_SUBTYPES[category_v2]:
        return STRATEGY_SUBTYPES[category_v2][0]
    
    return ""


def check_source_exists(file_name: str) -> Tuple[bool, Optional[Path]]:
    """Vérifie si le fichier source existe."""
    if not file_name:
        return False, None
    
    # Chemin direct
    direct_path = STRATEGIES_SOURCE / file_name
    if direct_path.exists():
        return True, direct_path
    
    # Recherche avec pattern
    for f in STRATEGIES_SOURCE.glob(f"*{file_name}*"):
        return True, f
    
    return False, None


# =============================================================================
# LECTURE V1
# =============================================================================

def load_v1_csv() -> List[Dict]:
    """Charge le CSV V1."""
    if not V1_CSV.exists():
        raise FileNotFoundError(f"CSV V1 introuvable: {V1_CSV}")
    
    records = []
    with open(V1_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            records.append(dict(row))
    
    return records


def load_v1_tracking() -> Dict:
    """Charge le tracking JSON V1."""
    if not V1_TRACKING.exists():
        return {"metadata": {}, "strategies": {}}
    
    with open(V1_TRACKING, 'r', encoding='utf-8') as f:
        return json.load(f)


# =============================================================================
# MIGRATION
# =============================================================================

@dataclass
class MigrationStats:
    """Statistiques de migration."""
    total_v1: int = 0
    migrated: int = 0
    source_missing: int = 0
    type_mapped: Counter = field(default_factory=Counter)
    type_unmapped: List[str] = field(default_factory=list)
    subtype_mapped: Counter = field(default_factory=Counter)


def migrate_record(record: Dict, v1_tracking: Dict, stats: MigrationStats) -> Dict:
    """Migre un enregistrement V1 vers V2."""
    strategy_name = record.get('strategy_name', '')
    file_name = record.get('file_name', '')
    type_v1 = record.get('strategy_type', '')
    subtype_v1 = record.get('strategy_subtype', '')
    
    # Mapping type
    type_v2 = normalize_type_v1_to_v2(type_v1)
    stats.type_mapped[f"{type_v1} → {type_v2}"] += 1
    
    # Mapping subtype
    subtype_v2 = map_subtype_v1_to_v2(subtype_v1, type_v1, type_v2)
    stats.subtype_mapped[subtype_v2] += 1
    
    # Vérifier source
    source_exists, source_path = check_source_exists(file_name)
    if not source_exists:
        stats.source_missing += 1
    
    # Récupérer code_hash du tracking V1
    code_hash = ""
    if strategy_name in v1_tracking.get('strategies', {}):
        code_hash = v1_tracking['strategies'][strategy_name].get('code_hash', '')
    
    # Construire enregistrement V2
    record_v2 = {
        'strategy_name': strategy_name,
        'file_name': file_name,
        'strategy_type': type_v2,
        'strategy_subtype': subtype_v2,
        'tags': subtype_v1,  # Le subtype V1 devient le tag
        'summary': record.get('summary', ''),
        'entry_conditions': record.get('entry_conditions', ''),
        'exit_conditions': record.get('exit_conditions', ''),
        'stop_loss_level': record.get('stop_loss_level', ''),
        'take_profit_level': record.get('take_profit_level', ''),
        'exit_on_close': record.get('exit_on_close', ''),
        'time_exit_condition': record.get('time_exit_condition', ''),
        'time_exit_details': record.get('time_exit_details', ''),
        'function_patterns': record.get('function_patterns', ''),
        'pattern_details': record.get('pattern_details', ''),
        'number_of_patterns': record.get('number_of_patterns', ''),
        'complexity_score': record.get('complexity_score', ''),
        'quality_score': record.get('quality_score', ''),
        'quality_analysis': record.get('quality_analysis', ''),
        'code_hash': code_hash,
        'source_missing': not source_exists,
        'migrated_from_v1': True,
        'migration_date': datetime.now().isoformat(),
    }
    
    stats.migrated += 1
    return record_v2


def run_migration(dry_run: bool = False, verbose: bool = True) -> Tuple[List[Dict], MigrationStats]:
    """Exécute la migration complète."""
    print("=" * 60)
    print("MIGRATION V1 → V2 DES ANALYSES IA")
    print("=" * 60)
    
    # Charger V1
    print("\n📂 Chargement des données V1...")
    v1_records = load_v1_csv()
    v1_tracking = load_v1_tracking()
    
    stats = MigrationStats(total_v1=len(v1_records))
    print(f"   • {stats.total_v1} stratégies dans le CSV V1")
    print(f"   • {len(v1_tracking.get('strategies', {}))} stratégies dans le tracking V1")
    
    # Migrer
    print("\n🔄 Migration en cours...")
    v2_records = []
    
    for i, record in enumerate(v1_records):
        v2_record = migrate_record(record, v1_tracking, stats)
        v2_records.append(v2_record)
        
        if verbose and (i + 1) % 50 == 0:
            print(f"   • {i + 1}/{stats.total_v1} migrées...")
    
    print(f"\n✅ Migration terminée: {stats.migrated}/{stats.total_v1} stratégies")
    print(f"   • {stats.source_missing} fichiers sources manquants")
    
    return v2_records, stats


# =============================================================================
# EXPORT V2
# =============================================================================

def export_v2_csv(records: List[Dict], force: bool = False):
    """Exporte le CSV V2."""
    if V2_CSV.exists() and not force:
        print(f"⚠️  CSV V2 existe déjà: {V2_CSV}")
        print("   Utilisez --force pour écraser")
        return False
    
    V2_OUTPUT.mkdir(parents=True, exist_ok=True)
    
    if not records:
        print("❌ Aucun enregistrement à exporter")
        return False
    
    fieldnames = list(records[0].keys())
    
    with open(V2_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(records)
    
    print(f"✅ CSV V2 exporté: {V2_CSV}")
    return True


def export_v2_tracking(records: List[Dict], v1_tracking: Dict, force: bool = False):
    """Exporte le tracking JSON V2."""
    if V2_TRACKING.exists() and not force:
        print(f"⚠️  Tracking V2 existe déjà: {V2_TRACKING}")
        return False
    
    tracking_v2 = {
        "metadata": {
            "last_full_run": datetime.now().isoformat(),
            "tracking_version": "2.0",
            "analysis_version": "2.0",
            "migrated_from_v1": True,
            "migration_date": datetime.now().isoformat(),
            "v1_metadata": v1_tracking.get('metadata', {}),
        },
        "strategies": {}
    }
    
    for record in records:
        strategy_name = record['strategy_name']
        tracking_v2['strategies'][strategy_name] = {
            'code_hash': record.get('code_hash', ''),
            'code_file': str(STRATEGIES_SOURCE / record.get('file_name', '')),
            'last_analyzed': record.get('migration_date', datetime.now().isoformat()),
            'html_file': f"{strategy_name}.html",
            'in_scope': not record.get('source_missing', False),
            'strategy_type': record['strategy_type'],
            'strategy_subtype': record['strategy_subtype'],
            'tags': record.get('tags', ''),
            'quality_score': record.get('quality_score', ''),
            'complexity_score': record.get('complexity_score', ''),
            'migrated_from_v1': True,
        }
    
    with open(V2_TRACKING, 'w', encoding='utf-8') as f:
        json.dump(tracking_v2, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Tracking V2 exporté: {V2_TRACKING}")
    return True


def export_migration_report(stats: MigrationStats, force: bool = False):
    """Exporte le rapport de migration."""
    report = {
        "migration_date": datetime.now().isoformat(),
        "summary": {
            "total_v1": stats.total_v1,
            "migrated": stats.migrated,
            "source_missing": stats.source_missing,
        },
        "type_mapping": dict(stats.type_mapped),
        "subtype_distribution": dict(stats.subtype_mapped),
        "unmapped_types": stats.type_unmapped,
    }
    
    with open(V2_MIGRATION_REPORT, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Rapport de migration: {V2_MIGRATION_REPORT}")


# =============================================================================
# GÉNÉRATION HTML V2
# =============================================================================

def generate_html_reports(records: List[Dict], skip_html: bool = False):
    """Génère les rapports HTML V2."""
    if skip_html:
        print("⏭️  Génération HTML ignorée (--skip-html)")
        return
    
    V2_HTML_REPORTS.mkdir(parents=True, exist_ok=True)
    
    try:
        from analyzers.html_generator import HTMLReportGenerator
        
        print("\n📄 Génération des rapports HTML V2...")
        generator = HTMLReportGenerator(V2_HTML_REPORTS)
        
        generated = 0
        for i, record in enumerate(records):
            strategy_name = record['strategy_name']
            
            # Convertir le record pour le générateur
            analysis = {
                'strategy_name': strategy_name,
                'strategy_type': record['strategy_type'],
                'strategy_subtype': record['strategy_subtype'],
                'tags': record.get('tags', ''),
                'summary': record.get('summary', ''),
                'entry_conditions': record.get('entry_conditions', ''),
                'exit_conditions': record.get('exit_conditions', ''),
                'stop_loss_level': record.get('stop_loss_level', ''),
                'take_profit_level': record.get('take_profit_level', ''),
                'exit_on_close': record.get('exit_on_close', ''),
                'time_exit_condition': record.get('time_exit_condition', ''),
                'time_exit_details': record.get('time_exit_details', ''),
                'function_patterns': record.get('function_patterns', ''),
                'pattern_details': record.get('pattern_details', ''),
                'number_of_patterns': record.get('number_of_patterns', ''),
                'complexity_score': record.get('complexity_score', ''),
                'quality_score': record.get('quality_score', ''),
                'quality_analysis': record.get('quality_analysis', ''),
                'code_hash': record.get('code_hash', ''),
            }
            
            try:
                # Charger le code source si disponible
                code = ""
                source_exists, source_path = check_source_exists(record.get('file_name', ''))
                if source_exists and source_path:
                    try:
                        code = source_path.read_text(encoding='utf-8-sig')
                    except:
                        code = "// Code source non disponible"
                else:
                    code = "// Code source non trouvé"
                
                # Utiliser la signature correcte du générateur V2
                generator.generate_strategy_report(
                    analysis=analysis,
                    strategy_code=code
                )
                generated += 1
                
            except Exception as e:
                print(f"   ⚠️  Erreur HTML pour {strategy_name}: {e}")
            
            if (i + 1) % 50 == 0:
                print(f"   • {i + 1}/{len(records)} rapports générés...")
        
        print(f"✅ {generated} rapports HTML générés")
        
        # Générer le dashboard
        print("\n📊 Génération du dashboard...")
        
        # Préparer les données pour le dashboard
        strategies_data = []
        for record in records:
            strategies_data.append({
                'strategy_name': record['strategy_name'],
                'strategy_type': record['strategy_type'],
                'strategy_subtype': record['strategy_subtype'],
                'tags': record.get('tags', ''),
                'quality_score': record.get('quality_score', '0'),
                'complexity_score': record.get('complexity_score', '0'),
                'summary': record.get('summary', ''),
            })
        
        generator.generate_dashboard(strategies_data)
        print(f"✅ Dashboard généré: {V2_HTML_REPORTS / 'index.html'}")
        
    except ImportError as e:
        print(f"⚠️  Module HTML non disponible: {e}")
        print("   Les rapports HTML ne seront pas générés.")


# =============================================================================
# RAPPORT SEUL (--report-only)
# =============================================================================

def generate_mapping_report():
    """Génère uniquement le rapport de mapping sans migration."""
    print("=" * 60)
    print("RAPPORT DE MAPPING V1 → V2")
    print("=" * 60)
    
    v1_records = load_v1_csv()
    
    type_mapping = Counter()
    subtype_analysis = {}
    
    for record in v1_records:
        type_v1 = record.get('strategy_type', '')
        subtype_v1 = record.get('strategy_subtype', '')
        
        type_v2 = normalize_type_v1_to_v2(type_v1)
        subtype_v2 = map_subtype_v1_to_v2(subtype_v1, type_v1, type_v2)
        
        key = f"{type_v1} → {type_v2}"
        type_mapping[key] += 1
        
        if type_v2 not in subtype_analysis:
            subtype_analysis[type_v2] = Counter()
        subtype_analysis[type_v2][subtype_v2] += 1
    
    print("\n📊 MAPPING DES TYPES:")
    print("-" * 60)
    for mapping, count in sorted(type_mapping.items(), key=lambda x: -x[1]):
        print(f"  {mapping}: {count}")
    
    print("\n📊 DISTRIBUTION DES SUBTYPES V2:")
    print("-" * 60)
    for cat, subtypes in sorted(subtype_analysis.items()):
        print(f"\n  {cat}:")
        for subtype, count in sorted(subtypes.items(), key=lambda x: -x[1]):
            print(f"    • {subtype}: {count}")
    
    print("\n" + "=" * 60)


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Migration V1 → V2 des analyses IA")
    parser.add_argument('--dry-run', action='store_true', help='Analyser sans écrire')
    parser.add_argument('--force', action='store_true', help='Écraser fichiers existants')
    parser.add_argument('--skip-html', action='store_true', help='Ne pas générer les HTML')
    parser.add_argument('--report-only', action='store_true', help='Rapport de mapping uniquement')
    parser.add_argument('--verbose', action='store_true', help='Afficher détails')
    
    args = parser.parse_args()
    
    # Mode rapport seul
    if args.report_only:
        generate_mapping_report()
        return
    
    # Migration
    v2_records, stats = run_migration(dry_run=args.dry_run, verbose=args.verbose)
    
    if args.dry_run:
        print("\n🔍 MODE DRY-RUN - Aucun fichier écrit")
        print("\n📊 Aperçu du mapping:")
        for mapping, count in sorted(stats.type_mapped.items(), key=lambda x: -x[1])[:20]:
            print(f"   {mapping}: {count}")
        return
    
    # Export
    print("\n" + "=" * 60)
    print("EXPORT V2")
    print("=" * 60)
    
    v1_tracking = load_v1_tracking()
    
    export_v2_csv(v2_records, force=args.force)
    export_v2_tracking(v2_records, v1_tracking, force=args.force)
    export_migration_report(stats, force=args.force)
    
    # HTML
    generate_html_reports(v2_records, skip_html=args.skip_html)
    
    print("\n" + "=" * 60)
    print("✅ MIGRATION TERMINÉE")
    print("=" * 60)
    print(f"   • Stratégies migrées: {stats.migrated}/{stats.total_v1}")
    print(f"   • Sources manquantes: {stats.source_missing}")
    print(f"   • CSV V2: {V2_CSV}")
    print(f"   • Tracking V2: {V2_TRACKING}")
    print(f"   • HTML: {V2_HTML_REPORTS}")


if __name__ == "__main__":
    main()
