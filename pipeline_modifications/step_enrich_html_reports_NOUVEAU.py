# =============================================================================
# ÉTAPE 1: ENRICHISSEMENT HTML REPORTS (KPI + EQUITY)
# =============================================================================

def step_enrich_html_reports(config: PipelineConfig) -> Dict[str, Any]:
    """
    Étape 1: Enrichir les rapports HTML avec KPIs + Equity Curves.
    
    Cette étape combine deux enrichissements:
    - KPI Dashboard: Métriques de performance depuis Portfolio Report
    - Equity Curves: Graphiques Chart.js depuis fichiers DataSource
    
    Returns:
        Dict avec statistiques de l'étape
    """
    print("\n" + "=" * 70)
    print("📊 ÉTAPE 1: ENRICHISSEMENT HTML REPORTS (KPI + EQUITY)")
    print("=" * 70)
    
    result = {
        'step': 'enrich_html_reports',
        'success': False,
        'enriched': 0,
        'enriched_kpi': 0,
        'enriched_equity': 0,           # Rafraîchi avec nouvelles données
        'enriched_both': 0,
        'equity_preserved_with_warning': 0,  # Equity préservée (DataSource manquant)
        'missing_equity_data': 0,       # Pas de données, section N/A ajoutée
        'skipped': 0,
        'errors': 0,
        'duration_seconds': 0
    }
    
    start_time = time.time()
    
    try:
        # Import des modules
        from src.enrichers.kpi_enricher import KPIEnricher
        from src.enrichers.equity_enricher import EquityCurveEnricher
        from src.enrichers.styles import get_kpi_styles
        
        # Charger le Portfolio Report
        try:
            portfolio_path = get_latest_portfolio_report()
            print(f"\n📁 Portfolio Report: {portfolio_path.name}")
        except FileNotFoundError:
            # Essayer dans le dossier Results legacy
            legacy_reports = list(LEGACY_ROOT.glob("Results/Portfolio_Report_V2_*.csv"))
            if legacy_reports:
                portfolio_path = max(legacy_reports, key=lambda p: p.stat().st_mtime)
                print(f"\n📁 Portfolio Report (legacy): {portfolio_path.name}")
            else:
                print("⚠️  Aucun Portfolio Report trouvé")
                result['errors'] = 1
                return result
        
        # Créer les enrichers
        kpi_enricher = KPIEnricher(portfolio_path)
        equity_enricher = EquityCurveEnricher(EQUITY_CURVES_DIR)
        
        if not kpi_enricher.portfolio_data:
            print("⚠️  Aucune donnée dans le Portfolio Report")
            result['errors'] = 1
            return result
        
        # Afficher info DataSource
        if EQUITY_CURVES_DIR.exists():
            nb_datasources = len(list(EQUITY_CURVES_DIR.glob("*.txt")))
            print(f"📈 DataSource Dir: {EQUITY_CURVES_DIR}")
            print(f"   {nb_datasources} fichiers DataSource disponibles")
        else:
            print(f"⚠️  DataSource Dir non trouvé: {EQUITY_CURVES_DIR}")
            print(f"   Equity Curves ne seront pas enrichies")
        
        # Trouver les rapports HTML à enrichir
        html_dirs = [
            HTML_REPORTS_DIR,
            LEGACY_ROOT / "Results" / "HTML_Reports",
        ]
        
        html_files = []
        for html_dir in html_dirs:
            if html_dir.exists():
                html_files.extend(html_dir.glob("*.html"))
        
        # Filtrer les index
        html_files = [f for f in html_files if f.name != "index.html"]
        
        print(f"\n📄 {len(html_files)} fichiers HTML trouvés")
        print(f"📊 {len(kpi_enricher.portfolio_data)} stratégies dans le Portfolio Report")
        
        if config.dry_run:
            print("\n🔍 Mode dry-run: aucune modification")
            result['success'] = True
            return result
        
        # Enrichir chaque fichier
        for html_file in html_files:
            try:
                strategy_name = html_file.stem
                
                # Lire le HTML existant
                content = html_file.read_text(encoding='utf-8')
                
                # Détecter si déjà enrichi
                has_existing_kpi = 'kpi-dashboard' in content
                has_existing_equity = 'equity-section' in content
                already_enriched = has_existing_kpi or has_existing_equity
                
                if already_enriched and not config.enrich_force:
                    if config.verbose:
                        print(f"   ✓ {strategy_name}: déjà enrichi")
                    result['skipped'] += 1
                    continue
                
                # ============================================================
                # 1. ENRICHISSEMENT KPI
                # ============================================================
                kpis = kpi_enricher.find_kpis_for_strategy(strategy_name)
                kpi_html = kpi_enricher.generate_kpi_html(kpis)
                has_kpi = kpis is not None
                
                # ============================================================
                # 2. ENRICHISSEMENT EQUITY
                # ============================================================
                equity_html = ""
                has_new_equity = False
                equity_status = "none"
                
                if config.enrich_include_equity:
                    # Charger les données equity
                    symbol = kpis.get('Symbol', '') if kpis else ''
                    oos_date = kpis.get('Date_Debut_OOS') if kpis else None
                    equity_data = equity_enricher.load_equity_data(strategy_name, symbol)
                    
                    # SCÉNARIO 1: Données disponibles → Enrichir/Rafraîchir
                    if equity_data is not None:
                        equity_html = equity_enricher.generate_equity_html(equity_data, oos_date)
                        has_new_equity = True
                        equity_status = "refreshed"
                    
                    # SCÉNARIO 2: Pas de données MAIS equity déjà présente → PRÉSERVER
                    elif has_existing_equity and equity_data is None:
                        # Générer bandeau d'avertissement
                        equity_html = _generate_equity_warning_banner()
                        equity_status = "preserved"
                    
                    # SCÉNARIO 3: Pas de données ET pas d'equity → Section N/A
                    elif not has_existing_equity and equity_data is None:
                        equity_html = equity_enricher._generate_no_data_section()
                        equity_status = "na"
                
                # ============================================================
                # 3. INJECTION DANS HTML
                # ============================================================
                
                # Injecter les styles CSS (une seule fois)
                if '</head>' in content and 'kpi-dashboard {' not in content:
                    kpi_styles = get_kpi_styles()
                    content = content.replace('</head>', f'{kpi_styles}\n</head>')
                
                # Injecter ou remplacer KPI
                if has_existing_kpi and config.enrich_force:
                    # Remplacer section existante
                    content = _replace_section(content, 'kpi-dashboard', kpi_html)
                elif not has_existing_kpi:
                    # Injecter après <body>
                    content = _inject_after_body(content, kpi_html)
                
                # Injecter ou remplacer Equity
                if config.enrich_include_equity:
                    if equity_status == "preserved":
                        # Injecter warning avant section existante
                        content = _inject_warning_before_equity(content, equity_html)
                    elif equity_status == "refreshed" and has_existing_equity:
                        # Remplacer section existante
                        content = _replace_section(content, 'equity-section', equity_html)
                    elif equity_status in ("refreshed", "na") and not has_existing_equity:
                        # Injecter après KPI
                        content = _inject_after_kpi(content, equity_html)
                
                # ============================================================
                # 4. SAUVEGARDE
                # ============================================================
                
                # Backup si demandé
                if config.enrich_backup:
                    backup_path = html_file.with_suffix('.html.bak')
                    if not backup_path.exists():
                        import shutil
                        shutil.copy2(html_file, backup_path)
                
                # Écrire le fichier enrichi
                html_file.write_text(content, encoding='utf-8')
                
                # ============================================================
                # 5. STATISTIQUES
                # ============================================================
                
                result['enriched'] += 1
                
                if has_kpi:
                    result['enriched_kpi'] += 1
                
                if equity_status == "refreshed":
                    result['enriched_equity'] += 1
                elif equity_status == "preserved":
                    result['equity_preserved_with_warning'] += 1
                elif equity_status == "na":
                    result['missing_equity_data'] += 1
                
                if has_kpi and equity_status == "refreshed":
                    result['enriched_both'] += 1
                
                # Log verbeux
                if config.verbose:
                    status_icon = "✅" if equity_status == "refreshed" else "⚠️" if equity_status == "preserved" else "📊"
                    kpi_status = "KPI" if has_kpi else "no KPI"
                    
                    if equity_status == "refreshed":
                        equity_label = "Equity rafraîchie"
                    elif equity_status == "preserved":
                        equity_label = "Equity préservée (DataSource manquant)"
                    elif equity_status == "na":
                        equity_label = "section Equity N/A"
                    else:
                        equity_label = "no Equity"
                    
                    print(f"   {status_icon} {strategy_name}: {kpi_status} + {equity_label}")
                
            except Exception as e:
                print(f"   ❌ {html_file.name}: {e}")
                result['errors'] += 1
                if config.verbose:
                    import traceback
                    traceback.print_exc()
        
        result['success'] = True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        result['errors'] += 1
        if config.verbose:
            import traceback
            traceback.print_exc()
    
    result['duration_seconds'] = round(time.time() - start_time, 1)
    
    # Résumé final
    print(f"\n📈 Résumé:")
    print(f"   • {result['enriched_both']} enrichis avec KPI + Equity rafraîchie")
    if result['equity_preserved_with_warning'] > 0:
        print(f"   • {result['equity_preserved_with_warning']} enrichis avec KPI + Equity préservée (warning)")
    if result['missing_equity_data'] > 0:
        print(f"   • {result['missing_equity_data']} enrichis avec KPI + section Equity N/A")
    if result['skipped'] > 0:
        print(f"   • {result['skipped']} ignorés (déjà à jour)")
    if result['errors'] > 0:
        print(f"   • {result['errors']} erreurs")
    print(f"⏱️  Durée: {result['duration_seconds']}s")
    
    return result


# =============================================================================
# FONCTIONS UTILITAIRES POUR INJECTION HTML
# =============================================================================

def _generate_equity_warning_banner() -> str:
    """Génère un bandeau d'avertissement pour equity non rafraîchie."""
    return '''
    <div class="equity-warning-banner" style="
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        color: white;
        padding: 12px 20px;
        margin: 20px 0 10px 0;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    ">
        <span style="font-size: 1.5em;">⚠️</span>
        <div>
            <strong>Equity Curve non rafraîchie</strong>
            <br>
            <small>DataSource manquant lors du dernier enrichissement. Les données affichées peuvent être obsolètes.</small>
        </div>
    </div>
    '''


def _inject_after_body(content: str, html: str) -> str:
    """Injecte du HTML juste après la balise <body>."""
    if '<body>' in content:
        content = content.replace('<body>', f'<body>\n{html}')
    elif '<body ' in content:
        import re
        content = re.sub(r'(<body[^>]*>)', rf'\1\n{html}', content)
    return content


def _inject_after_kpi(content: str, html: str) -> str:
    """Injecte du HTML après la section KPI."""
    if '</div><!-- end kpi-dashboard -->' in content:
        content = content.replace(
            '</div><!-- end kpi-dashboard -->',
            f'</div><!-- end kpi-dashboard -->\n{html}'
        )
    elif 'kpi-dashboard' in content:
        # Trouver la fin de la div kpi-dashboard
        import re
        pattern = r'(<div class="kpi-dashboard">.*?</div>)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            kpi_section = match.group(1)
            content = content.replace(kpi_section, f'{kpi_section}\n{html}')
    else:
        # Fallback: injecter après body
        content = _inject_after_body(content, html)
    return content


def _inject_warning_before_equity(content: str, warning_html: str) -> str:
    """Injecte le bandeau d'avertissement avant la section equity existante."""
    if '<div class="equity-section">' in content:
        # Vérifier si le warning n'est pas déjà présent
        if 'equity-warning-banner' not in content:
            content = content.replace(
                '<div class="equity-section">',
                f'{warning_html}\n    <div class="equity-section">'
            )
    return content


def _replace_section(content: str, section_class: str, new_html: str) -> str:
    """Remplace une section entière par du nouveau HTML."""
    import re
    
    # Pattern pour trouver la div et tout son contenu
    pattern = rf'(<div class="{section_class}">.*?</div>\s*(?:</div>)?)'
    
    # Chercher avec dotall pour matcher sur plusieurs lignes
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        old_section = match.group(0)
        content = content.replace(old_section, new_html)
    
    return content
