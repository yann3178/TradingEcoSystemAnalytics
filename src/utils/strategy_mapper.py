"""
Strategy Mapper Module
======================
Centralizes the mapping between strategy names and their symbols/instruments.
Uses Portfolio Report as the source of truth.

Author: Trading Analytics V2
Date: 2025-11-28
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict


class StrategyMapper:
    """Manages strategy name to symbol(s) mappings."""
    
    def __init__(self, portfolio_report_path: str):
        """
        Initialize the mapper with a Portfolio Report CSV file.
        
        Args:
            portfolio_report_path: Path to the Portfolio_Report_V2_*.csv file
        """
        self.portfolio_report_path = Path(portfolio_report_path)
        self.mappings: Dict[str, Dict] = {}
        self.reverse_mappings: Dict[str, str] = {}  # full_key -> strategy_name
        self.load_mappings()
    
    def load_mappings(self):
        """Load mappings from the Portfolio Report CSV."""
        if not self.portfolio_report_path.exists():
            raise FileNotFoundError(f"Portfolio Report not found: {self.portfolio_report_path}")
        
        strategy_to_symbols = defaultdict(set)
        
        with open(self.portfolio_report_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                strategy_name = row.get('Strategie', '').strip()
                symbol = row.get('Symbol', '').strip()
                
                if strategy_name and symbol:
                    strategy_to_symbols[strategy_name].add(symbol)
        
        # Build the mappings dictionary
        for strategy_name, symbols in strategy_to_symbols.items():
            symbols_list = sorted(list(symbols))
            full_keys = [f"{symbol}_{strategy_name}" for symbol in symbols_list]
            
            self.mappings[strategy_name] = {
                'symbols': symbols_list,
                'full_keys': full_keys,
                'count': len(symbols_list)
            }
            
            # Build reverse mapping
            for full_key in full_keys:
                self.reverse_mappings[full_key] = strategy_name
        
        print(f"✓ Loaded {len(self.mappings)} strategies with symbol mappings")
        print(f"✓ Total strategy-symbol combinations: {len(self.reverse_mappings)}")
    
    def get_symbols_for_strategy(self, strategy_name: str) -> List[str]:
        """
        Get all symbols associated with a strategy.
        
        Args:
            strategy_name: The strategy name
            
        Returns:
            List of symbols (empty list if strategy not found)
        """
        return self.mappings.get(strategy_name, {}).get('symbols', [])
    
    def get_full_keys_for_strategy(self, strategy_name: str) -> List[str]:
        """
        Get all full keys (Symbol_StrategyName) for a strategy.
        
        Args:
            strategy_name: The strategy name
            
        Returns:
            List of full keys (empty list if strategy not found)
        """
        return self.mappings.get(strategy_name, {}).get('full_keys', [])
    
    def get_strategy_from_full_key(self, full_key: str) -> Optional[str]:
        """
        Extract the strategy name from a full key.
        
        Args:
            full_key: Format "Symbol_StrategyName"
            
        Returns:
            Strategy name if found, None otherwise
        """
        return self.reverse_mappings.get(full_key)
    
    def is_multi_symbol_strategy(self, strategy_name: str) -> bool:
        """
        Check if a strategy runs on multiple symbols.
        
        Args:
            strategy_name: The strategy name
            
        Returns:
            True if strategy runs on 2+ symbols
        """
        return self.mappings.get(strategy_name, {}).get('count', 0) > 1
    
    def find_strategy_fuzzy(self, partial_name: str, min_similarity: float = 0.8) -> List[Tuple[str, float]]:
        """
        Find strategies matching a partial name using fuzzy matching.
        
        Args:
            partial_name: Partial strategy name to search for
            min_similarity: Minimum similarity score (0-1)
            
        Returns:
            List of (strategy_name, similarity_score) tuples, sorted by score
        """
        from difflib import SequenceMatcher
        
        matches = []
        for strategy_name in self.mappings.keys():
            similarity = SequenceMatcher(None, partial_name.lower(), strategy_name.lower()).ratio()
            if similarity >= min_similarity:
                matches.append((strategy_name, similarity))
        
        return sorted(matches, key=lambda x: x[1], reverse=True)
    
    def export_to_json(self, output_path: str):
        """
        Export the mappings to a JSON file for reference.
        
        Args:
            output_path: Path where to save the JSON file
        """
        output_data = {
            'generated_at': datetime.now().isoformat(),
            'source': str(self.portfolio_report_path),
            'total_strategies': len(self.mappings),
            'total_combinations': len(self.reverse_mappings),
            'mappings': self.mappings
        }
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Mapping exported to: {output_path}")
    
    def get_statistics(self) -> Dict:
        """Get mapping statistics."""
        multi_symbol_count = sum(1 for v in self.mappings.values() if v['count'] > 1)
        single_symbol_count = len(self.mappings) - multi_symbol_count
        
        symbol_distribution = defaultdict(int)
        for data in self.mappings.values():
            symbol_distribution[data['count']] += 1
        
        return {
            'total_strategies': len(self.mappings),
            'total_combinations': len(self.reverse_mappings),
            'single_symbol_strategies': single_symbol_count,
            'multi_symbol_strategies': multi_symbol_count,
            'symbol_distribution': dict(symbol_distribution)
        }
    
    def print_statistics(self):
        """Print mapping statistics to console."""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("STRATEGY MAPPING STATISTICS")
        print("="*60)
        print(f"Total unique strategies: {stats['total_strategies']}")
        print(f"Total strategy-symbol combinations: {stats['total_combinations']}")
        print(f"Single-symbol strategies: {stats['single_symbol_strategies']}")
        print(f"Multi-symbol strategies: {stats['multi_symbol_strategies']}")
        print("\nSymbol distribution:")
        for count, num_strategies in sorted(stats['symbol_distribution'].items()):
            print(f"  {num_strategies} strategies run on {count} symbol(s)")
        print("="*60 + "\n")


def main():
    """Test the mapper with the latest Portfolio Report."""
    import sys
    
    # Find the latest Portfolio Report
    reports_dir = Path(r"C:\TradeData\V2\data\portfolio_reports")
    reports = sorted(reports_dir.glob("Portfolio_Report_V2_*.csv"), reverse=True)
    
    if not reports:
        print("❌ No Portfolio Report found!")
        sys.exit(1)
    
    latest_report = reports[0]
    print(f"Using Portfolio Report: {latest_report.name}")
    
    # Create mapper
    mapper = StrategyMapper(str(latest_report))
    
    # Print statistics
    mapper.print_statistics()
    
    # Export to JSON
    output_json = Path(r"C:\TradeData\V2\outputs\consolidated\strategy_mapping.json")
    mapper.export_to_json(str(output_json))
    
    # Test some lookups
    print("\nExample lookups:")
    print("-" * 60)
    
    # Example 1: Get symbols for a strategy
    test_strategy = list(mapper.mappings.keys())[0] if mapper.mappings else None
    if test_strategy:
        symbols = mapper.get_symbols_for_strategy(test_strategy)
        full_keys = mapper.get_full_keys_for_strategy(test_strategy)
        print(f"Strategy: {test_strategy}")
        print(f"  Symbols: {symbols}")
        print(f"  Full keys: {full_keys}")
        print(f"  Multi-symbol: {mapper.is_multi_symbol_strategy(test_strategy)}")


if __name__ == "__main__":
    main()
