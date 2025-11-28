"""
Tests - Module Analyseur IA
============================
Tests unitaires pour les modules d'analyse IA.

Usage:
    pytest tests/test_ai_analyzer.py -v
    python tests/test_ai_analyzer.py  # Pour exécution directe
"""

import sys
from pathlib import Path
import pytest

# Ajouter le chemin V2 au path
V2_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(V2_ROOT))


# =============================================================================
# TESTS CONFIG
# =============================================================================

class TestConfig:
    """Tests pour la configuration de l'analyseur."""
    
    def test_strategy_categories_defined(self):
        """Vérifie que les 8 catégories sont définies."""
        from src.analyzers.config import STRATEGY_CATEGORIES
        
        assert len(STRATEGY_CATEGORIES) == 8
        assert "BREAKOUT" in STRATEGY_CATEGORIES
        assert "MEAN_REVERSION" in STRATEGY_CATEGORIES
        assert "TREND_FOLLOWING" in STRATEGY_CATEGORIES
        assert "PATTERN" in STRATEGY_CATEGORIES
        assert "VOLATILITY" in STRATEGY_CATEGORIES
        assert "SEASONAL" in STRATEGY_CATEGORIES
        assert "MOMENTUM" in STRATEGY_CATEGORIES
        assert "OTHER" in STRATEGY_CATEGORIES
    
    def test_normalize_category(self):
        """Teste la normalisation des catégories."""
        from src.analyzers.config import normalize_category
        
        # Catégories standard
        assert normalize_category("BREAKOUT") == "BREAKOUT"
        assert normalize_category("breakout") == "BREAKOUT"
        
        # Mapping des anciens types
        assert normalize_category("Reversal") == "MEAN_REVERSION"
        assert normalize_category("Mean Reversion") == "MEAN_REVERSION"
        assert normalize_category("Trend Following") == "TREND_FOLLOWING"
        assert normalize_category("Counter-Trend") == "MEAN_REVERSION"
        
        # Cas inconnus
        assert normalize_category("Unknown Type") == "OTHER"
        assert normalize_category("") == "OTHER"
        assert normalize_category(None) == "OTHER"
    
    def test_config_defaults(self):
        """Teste les valeurs par défaut de la config."""
        from src.analyzers.config import AIAnalyzerConfig
        
        config = AIAnalyzerConfig()
        
        assert config.model == "claude-sonnet-4-20250514"
        assert config.max_tokens == 6000
        assert config.delay_between_requests == 2.5
        assert config.max_retries == 3
        assert config.mode == "delta"
        assert config.analysis_version == "2.0"


# =============================================================================
# TESTS CODE PARSER
# =============================================================================

class TestCodeParser:
    """Tests pour le parser de code PowerLanguage."""
    
    def test_clean_strategy_name(self):
        """Teste le nettoyage des noms de stratégies."""
        from src.utils.file_utils import clean_strategy_name
        
        # Extension
        assert clean_strategy_name("Strategy.txt") == "Strategy"
        
        # Préfixes
        assert clean_strategy_name("s_MyStrategy.txt") == "MyStrategy"
        assert clean_strategy_name("sa_MyStrategy.txt") == "MyStrategy"
        
        # Suffixes
        assert clean_strategy_name("Strategy_RAW.txt") == "Strategy"
        
        # Caractères encodés
        assert "." in clean_strategy_name("Strategyb2eTest.txt")
        assert " " in clean_strategy_name("Strategya20Test.txt")
    
    def test_extract_function_calls(self):
        """Teste l'extraction des appels de fonction."""
        from src.analyzers.code_parser import extract_function_calls
        
        code = """
        if RSI(Close, 14) > 70 then
            Buy next bar at market;
        if PatternFast(23) then
            Sell next bar at market;
        value1 = ATR(10);
        """
        
        functions = extract_function_calls(code)
        
        # RSI, PatternFast, ATR doivent être trouvés
        function_names = [f.split('(')[0] for f in functions]
        assert "RSI" in function_names
        assert "PatternFast" in function_names
        assert "ATR" in function_names
        
        # Les mots-clés ne doivent pas être inclus
        assert "if" not in function_names
        assert "then" not in function_names
        assert "Buy" not in function_names
    
    def test_compute_code_hash(self):
        """Teste le calcul de hash."""
        from src.analyzers.code_parser import compute_code_hash
        
        code1 = "Buy next bar at market;"
        code2 = "Sell next bar at market;"
        
        hash1 = compute_code_hash(code1)
        hash2 = compute_code_hash(code2)
        
        # Même code = même hash
        assert compute_code_hash(code1) == hash1
        
        # Code différent = hash différent
        assert hash1 != hash2
        
        # Format SHA-256
        assert len(hash1) == 64
        assert all(c in '0123456789abcdef' for c in hash1)


# =============================================================================
# TESTS HTML GENERATOR
# =============================================================================

class TestHTMLGenerator:
    """Tests pour le générateur HTML."""
    
    def test_html_escape(self):
        """Teste l'échappement HTML."""
        from src.analyzers.html_generator import html_escape
        
        assert html_escape("<script>") == "&lt;script&gt;"
        assert html_escape("a & b") == "a &amp; b"
        assert html_escape('"quoted"') == "&quot;quoted&quot;"
        assert html_escape("") == ""
    
    def test_format_text_for_html(self):
        """Teste la conversion du texte en HTML."""
        from src.analyzers.html_generator import format_text_for_html
        
        # Bold
        result = format_text_for_html("This is **bold** text")
        assert "<strong>bold</strong>" in result
        
        # Bullet points
        result = format_text_for_html("• Item 1\\n• Item 2")
        assert "<ul" in result
        assert "<li>Item 1</li>" in result
        assert "<li>Item 2</li>" in result
        
        # Numbered list
        result = format_text_for_html("1. First\\n2. Second")
        assert "<ol" in result
        assert "<li>First</li>" in result
        
        # N/A passthrough
        assert format_text_for_html("N/A") == "N/A"
        assert format_text_for_html("None") == "None"
    
    def test_get_score_class(self):
        """Teste les classes CSS des scores."""
        from src.analyzers.html_generator import get_score_class
        
        assert get_score_class(8) == "score-high"
        assert get_score_class(7) == "score-high"
        assert get_score_class(5) == "score-medium"
        assert get_score_class(4) == "score-medium"
        assert get_score_class(3) == "score-low"
        assert get_score_class("N/A") == ""
        assert get_score_class(None) == ""
    
    def test_get_type_color(self):
        """Teste les couleurs par type."""
        from src.analyzers.html_generator import get_type_color
        
        assert get_type_color("BREAKOUT") == "#3498db"
        assert get_type_color("TREND_FOLLOWING") == "#27ae60"
        assert get_type_color("OTHER") == "#95a5a6"
        
        # Inconnu
        assert get_type_color("UNKNOWN") == "#7f8c8d"


# =============================================================================
# TESTS TRACKING
# =============================================================================

class TestTracking:
    """Tests pour le système de tracking."""
    
    def test_should_process_new_strategy(self):
        """Une nouvelle stratégie doit être traitée."""
        from src.analyzers.ai_analyzer import AnalysisTracking
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            tracking_file = Path(f.name)
        
        try:
            tracking = AnalysisTracking(tracking_file)
            
            should, reason = tracking.should_process("NewStrategy", "abc123", "delta")
            
            assert should is True
            assert reason == "new_strategy"
        finally:
            tracking_file.unlink(missing_ok=True)
    
    def test_should_process_unchanged(self):
        """Une stratégie inchangée ne doit pas être retraitée."""
        from src.analyzers.ai_analyzer import AnalysisTracking
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            tracking_file = Path(f.name)
        
        try:
            tracking = AnalysisTracking(tracking_file)
            
            # Simuler une analyse précédente
            tracking.strategies["ExistingStrategy"] = {
                "code_hash": "abc123",
                "strategy_type": "BREAKOUT",
            }
            tracking.metadata["analysis_version"] = tracking.analysis_version
            
            should, reason = tracking.should_process("ExistingStrategy", "abc123", "delta")
            
            assert should is False
            assert reason == "unchanged"
        finally:
            tracking_file.unlink(missing_ok=True)
    
    def test_should_process_modified(self):
        """Une stratégie modifiée doit être retraitée."""
        from src.analyzers.ai_analyzer import AnalysisTracking
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            tracking_file = Path(f.name)
        
        try:
            tracking = AnalysisTracking(tracking_file)
            
            # Simuler une analyse précédente
            tracking.strategies["ModifiedStrategy"] = {
                "code_hash": "old_hash",
                "strategy_type": "BREAKOUT",
            }
            tracking.metadata["analysis_version"] = tracking.analysis_version
            
            should, reason = tracking.should_process("ModifiedStrategy", "new_hash", "delta")
            
            assert should is True
            assert reason == "code_modified"
        finally:
            tracking_file.unlink(missing_ok=True)
    
    def test_should_process_full_mode(self):
        """En mode full, tout doit être traité."""
        from src.analyzers.ai_analyzer import AnalysisTracking
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            tracking_file = Path(f.name)
        
        try:
            tracking = AnalysisTracking(tracking_file)
            
            # Simuler une stratégie existante
            tracking.strategies["ExistingStrategy"] = {
                "code_hash": "abc123",
                "strategy_type": "BREAKOUT",
            }
            tracking.metadata["analysis_version"] = tracking.analysis_version
            
            should, reason = tracking.should_process("ExistingStrategy", "abc123", "full")
            
            assert should is True
            assert reason == "full_mode"
        finally:
            tracking_file.unlink(missing_ok=True)


# =============================================================================
# TESTS INTEGRATION
# =============================================================================

class TestIntegration:
    """Tests d'intégration."""
    
    def test_config_validation(self):
        """Teste la validation de la configuration."""
        from src.analyzers.config import AIAnalyzerConfig
        
        config = AIAnalyzerConfig()
        errors = config.validate()
        
        # Les erreurs possibles sont:
        # - API key manquante
        # - Répertoire stratégies manquant
        
        # Au minimum, on vérifie que la validation retourne une liste
        assert isinstance(errors, list)
    
    def test_html_report_generation(self):
        """Teste la génération d'un rapport HTML."""
        import tempfile
        from src.analyzers.html_generator import HTMLReportGenerator
        
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = HTMLReportGenerator(Path(tmpdir))
            
            test_analysis = {
                "strategy_name": "TestStrategy",
                "strategy_type": "BREAKOUT",
                "strategy_subtype": "Channel Breakout",
                "summary": "A test **strategy**",
                "entry_conditions": "• Buy condition",
                "exit_conditions": "• Sell condition",
                "stop_loss_level": "None",
                "take_profit_level": "None",
                "exit_on_close": "YES",
                "time_exit_condition": "NO",
                "time_exit_details": "None",
                "function_patterns": ["RSI(14)"],
                "pattern_details": "None",
                "number_of_patterns": "1",
                "complexity_score": "5",
                "quality_score": "7",
                "quality_analysis": "Good strategy",
                "code_hash": "abc123",
            }
            
            test_code = "Buy next bar at market;"
            
            report_path = generator.generate_strategy_report(test_analysis, test_code)
            
            assert report_path.exists()
            content = report_path.read_text(encoding='utf-8')
            assert "TestStrategy" in content
            assert "BREAKOUT" in content
            assert "RSI(14)" in content


# =============================================================================
# MAIN
# =============================================================================

def run_tests():
    """Exécute tous les tests."""
    import subprocess
    
    # Exécuter avec pytest si disponible
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"],
            cwd=V2_ROOT
        )
        return result.returncode
    except Exception:
        # Fallback: exécution manuelle
        print("📋 Exécution manuelle des tests...\n")
        
        test_classes = [
            TestConfig,
            TestCodeParser,
            TestHTMLGenerator,
            TestTracking,
            TestIntegration,
        ]
        
        passed = 0
        failed = 0
        
        for test_class in test_classes:
            print(f"\n{'='*60}")
            print(f"📦 {test_class.__name__}")
            print("="*60)
            
            instance = test_class()
            
            for method_name in dir(instance):
                if method_name.startswith('test_'):
                    try:
                        method = getattr(instance, method_name)
                        method()
                        print(f"  ✅ {method_name}")
                        passed += 1
                    except Exception as e:
                        print(f"  ❌ {method_name}: {e}")
                        failed += 1
        
        print(f"\n{'='*60}")
        print(f"📊 Résultats: {passed} passés, {failed} échoués")
        print("="*60)
        
        return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_tests())
