#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML Report Enricher - Script principal d'enrichissement
========================================================
Enrichit les rapports HTML avec KPIs et Equity Curves.

Usage:
    python run_enrich.py [--html-dir PATH] [--no-backup] [--force]

Version: 2.0.0
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Ajouter le répertoire racine au path
V2_ROOT = Path(__file__).parent
sys.path.insert(0, str(V2_ROOT))

from config.settings import (
    HTML_REPORTS_DIR, PORTFOLIO_REPORTS_DIR, EQUITY_CURVES_DIR,
    LOGS_DIR, get_latest_portfolio_report
)
from src.utils.file_utils import safe_read
from src.enrichers.kpi_enricher import KPIEnricher
from src.enrichers.equity_enricher import EquityCurveEnricher
from src.enrichers.styles import KPI_DASHBOARD_CSS


class HTMLEnricher:
    """
    Orchestrateur d'enrichissement des rapports HTML.
    """
    
    def __init__(
        self,
        html_dir: Path,
        portfolio_report_path: Optional[Path] = None,
        datasources_dir: Optional[Path] = None,
        backup: bool = True,
        force: bool = False
    ):
        """
        Initialise l'enrichisseur.
        
        Args:
            html_dir: Répertoire des fichiers HTML
            portfolio_report_path: Chemin du Portfolio Report
            datasources_dir: Répertoire des DataSources
            backup: Créer des backups
            force: Réécrire même si déjà enrichi
        """
        self.html_dir = html_dir
        self.backup = backup
        self.force = force
        
        # Initialiser les enrichisseurs
        self.kpi_enricher = KPIEnricher(portfolio_report_path)
        self.equity_enricher = EquityCurveEnricher(datasources_dir)
        
        # Statistiques
        self.stats = {
            'total': 0,
            'enriched': 0,
            'with_kpis': 0,
            'with_equity': 0,
            'skipped': 0,
            'errors': 0
        }
    
    def enrich_file(self, html_path: Path) -> bool:
        """
        Enrichit un fichier HTML.
        
        Args:
            html_path: Chemin du fichier HTML
        
        Returns:
            True si succès
        """
        try:
            content = safe_read(html_path)
            
            # Vérifier si déjà enrichi
            already_enriched = 'kpi-dashboard' in content or 'equity-section' in content
            
            if already_enriched and not self.force:
                self.stats['skipped'] += 1
                return True
            
            # Nettoyer les anciennes sections si nécessaire
            if already_enriched:
                content = self._clean_existing_enrichment(content)
            
            # Créer backup si première fois
            if self.backup and not already_enriched:
                backup_path = html_path.with_suffix('.html.bak')
                if not backup_path.exists():
                    backup_path.write_text(content, encoding='utf-8')
            
            # Trouver les KPIs
            kpis = self.kpi_enricher.find_kpis_for_strategy(html_path.name)
            
            # Trouver les données equity
            equity_data = None
            oos_date = None
            if kpis:
                symbol = kpis.get('Symbol', '')
                strategy_name = kpis.get('Strategie', html_path.stem)
                equity_data = self.equity_enricher.load_equity_data(strategy_name, symbol)
                oos_date = kpis.get('Date_Debut_OOS')
            
            # Générer les sections HTML
            kpi_html = self.kpi_enricher.generate_kpi_html(kpis)
            equity_html = self.equity_enricher.generate_equity_html(equity_data, oos_date)
            
            # Injecter le CSS
            if 'kpi-dashboard {' not in content:
                content = self._inject_css(content)
            
            # Injecter les sections
            content = self._inject_sections(content, kpi_html, equity_html)
            
            # Écrire le fichier
            html_path.write_text(content, encoding='utf-8')
            
            # Mettre à jour les stats
            self.stats['enriched'] += 1
            if kpis:
                self.stats['with_kpis'] += 1
            if equity_data:
                self.stats['with_equity'] += 1
            
            return True
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            self.stats['errors'] += 1
            return False
    
    def _clean_existing_enrichment(self, content: str) -> str:
        """Nettoie les anciennes sections d'enrichissement."""
        # Supprimer section KPI
        content = re.sub(
            r'\s*<div class="kpi-dashboard">.*?</div>\s*(?=\s*<div class="(?:equity-section|section)"|$)',
            '',
            content,
            flags=re.DOTALL
        )
        
        # Supprimer section Equity avec scripts
        content = re.sub(
            r'\s*<div class="equity-section">.*?</script>\s*',
            '',
            content,
            flags=re.DOTALL
        )
        
        # Supprimer imports Chart.js orphelins
        content = re.sub(
            r'<script src="https://cdn\.jsdelivr\.net/npm/chart\.js[^"]*"></script>\s*',
            '',
            content
        )
        content = re.sub(
            r'<script src="https://cdn\.jsdelivr\.net/npm/chartjs-plugin-annotation[^"]*"></script>\s*',
            '',
            content
        )
        
        # Nettoyer lignes vides multiples
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        return content
    
    def _inject_css(self, content: str) -> str:
        """Injecte le CSS dans le document."""
        if '</style>' in content:
            last_style_pos = content.rfind('</style>')
            return content[:last_style_pos + 8] + KPI_DASHBOARD_CSS + content[last_style_pos + 8:]
        elif '</head>' in content:
            return content.replace('</head>', KPI_DASHBOARD_CSS + '\n</head>')
        return content
    
    def _inject_sections(self, content: str, kpi_html: str, equity_html: str) -> str:
        """Injecte les sections KPI et Equity."""
        combined = '\n' + kpi_html + '\n' + equity_html
        
        # Points d'insertion possibles
        insertion_points = [
            ('</div>\n        \n        <div class="section">', 
             '</div>\n' + combined + '\n        <div class="section">'),
            ('<div class="section">\n            <h2>📝 Summary</h2>', 
             combined + '\n        <div class="section">\n            <h2>📝 Summary</h2>'),
        ]
        
        for old, new in insertion_points:
            if old in content:
                return content.replace(old, new, 1)
        
        # Fallback: après le h1
        container_match = re.search(r'(<div class="container">.*?<h1>.*?</h1>)', content, re.DOTALL)
        if container_match:
            insert_pos = container_match.end()
            return content[:insert_pos] + combined + content[insert_pos:]
        
        return content
    
    def run(self) -> bool:
        """
        Exécute l'enrichissement de tous les fichiers HTML.
        
        Returns:
            True si aucune erreur
        """
        print("=" * 80)
        print("🚀 ENRICHISSEMENT DES RAPPORTS HTML V2")
        print("=" * 80)
        print()
        
        # Lister les fichiers
        html_files = sorted(self.html_dir.glob("*.html"))
        html_files = [f for f in html_files if f.name != "index.html" and not f.name.endswith('.bak')]
        
        self.stats['total'] = len(html_files)
        print(f"📁 {len(html_files)} fichiers HTML à traiter")
        print()
        
        # Traiter chaque fichier
        for i, html_file in enumerate(html_files, 1):
            print(f"[{i}/{len(html_files)}] {html_file.name}...", end=" ")
            
            success = self.enrich_file(html_file)
            
            if success:
                parts = []
                # Déterminer ce qui a été ajouté
                content = safe_read(html_file)
                if 'kpi-dashboard' in content:
                    parts.append("KPIs")
                if 'equityChart' in content:
                    parts.append("Equity")
                
                if parts:
                    print(f"✓ ({', '.join(parts)})")
                else:
                    print("✓ (skipped)")
            else:
                print("❌")
        
        # Rapport final
        self._print_report()
        
        return self.stats['errors'] == 0
    
    def _print_report(self):
        """Affiche le rapport final."""
        print()
        print("=" * 80)
        print("📊 RAPPORT D'ENRICHISSEMENT")
        print("=" * 80)
        print(f"   Fichiers traités:     {self.stats['total']}")
        print(f"   Fichiers enrichis:    {self.stats['enriched']}")
        print(f"   Avec KPIs:            {self.stats['with_kpis']}")
        print(f"   Avec Equity Curve:    {self.stats['with_equity']}")
        print(f"   Ignorés (déjà OK):    {self.stats['skipped']}")
        print(f"   Erreurs:              {self.stats['errors']}")
        print()
        print(f"📁 Fichiers dans: {self.html_dir}")
        print()


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Enrichit les rapports HTML avec KPIs et Equity Curves"
    )
    parser.add_argument(
        "--html-dir", 
        type=str, 
        default=str(HTML_REPORTS_DIR),
        help="Répertoire des fichiers HTML"
    )
    parser.add_argument(
        "--portfolio-report", 
        type=str, 
        default=None,
        help="Chemin du Portfolio Report (auto-détecté si omis)"
    )
    parser.add_argument(
        "--datasources-dir", 
        type=str, 
        default=str(EQUITY_CURVES_DIR),
        help="Répertoire des DataSources"
    )
    parser.add_argument(
        "--no-backup", 
        action="store_true",
        help="Ne pas créer de backup des fichiers"
    )
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Réécrire même si déjà enrichi"
    )
    
    args = parser.parse_args()
    
    # Résoudre les chemins
    html_dir = Path(args.html_dir)
    portfolio_report = Path(args.portfolio_report) if args.portfolio_report else None
    datasources_dir = Path(args.datasources_dir)
    
    # Vérifications
    if not html_dir.exists():
        print(f"❌ Répertoire HTML non trouvé: {html_dir}")
        return 1
    
    # Créer et exécuter l'enrichisseur
    enricher = HTMLEnricher(
        html_dir=html_dir,
        portfolio_report_path=portfolio_report,
        datasources_dir=datasources_dir,
        backup=not args.no_backup,
        force=args.force
    )
    
    success = enricher.run()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
