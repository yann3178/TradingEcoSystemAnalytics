"""Script pour ajouter la méthode generate_individual_pages() à CorrelationAnalyzer."""

from pathlib import Path

# Chemin du fichier
filepath = Path(r"C:\TradeData\V2\src\consolidators\correlation_calculator.py")

# Nouvelle méthode à ajouter
new_method = '''
    
    def generate_individual_pages(
        self,
        output_dir: Path,
        top_n: int = 15,
        verbose: bool = True
    ) -> Dict[str, int]:
        """
        Génère des pages HTML individuelles pour chaque stratégie.
        
        Chaque page contient :
        - Profil de corrélation de la stratégie
        - Top N stratégies les plus corrélées
        - Top N stratégies les moins corrélées (diversification)
        - Distribution des corrélations
        - Alertes et recommandations
        
        Args:
            output_dir: Répertoire de sortie pour les pages HTML
            top_n: Nombre de stratégies dans les listes top/bottom
            verbose: Afficher la progression
            
        Returns:
            Dict avec statistiques de génération
        """
        if self.corr_matrix_lt is None or self.corr_matrix_ct is None:
            raise ValueError("Exécutez run() avant de générer les pages individuelles")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if verbose:
            print("\\n" + "=" * 70)
            print("📄 GÉNÉRATION DES PAGES DE CORRÉLATION INDIVIDUELLES")
            print("=" * 70)
        
        # Récupérer la liste des stratégies
        all_strategies = self.scores['Strategy'].tolist()
        
        if verbose:
            print(f"\\n📊 Génération de {len(all_strategies)} pages...")
        
        generated = 0
        errors = 0
        
        for i, strategy in enumerate(all_strategies):
            if verbose and (i + 1) % 50 == 0:
                print(f"   → {i + 1}/{len(all_strategies)} pages générées...")
            
            try:
                # Calculer le profil détaillé
                profile = self._calculate_strategy_profile(strategy, top_n)
                
                # Générer la page HTML
                html_path = output_dir / f"{self._sanitize_filename(strategy)}_correlation.html"
                self._generate_strategy_html(profile, html_path)
                
                generated += 1
                
            except Exception as e:
                if verbose:
                    print(f"   ⚠️  Erreur pour {strategy}: {e}")
                errors += 1
        
        if verbose:
            print(f"\\n✅ {generated} pages générées")
            if errors > 0:
                print(f"⚠️  {errors} erreurs")
        
        return {
            'generated': generated,
            'errors': errors,
            'total': len(all_strategies)
        }
'''

# Lire le fichier
content = filepath.read_text(encoding='utf-8')

# Trouver le point d'insertion (après export_dashboard)
marker = '        print(f"📊 Dashboard HTML généré: {output_path}")\n        return output_path'

if marker in content:
    # Insérer la nouvelle méthode
    content = content.replace(marker, marker + new_method)
    
    # Écrire le fichier modifié
    filepath.write_text(content, encoding='utf-8')
    
    print("✅ Méthode generate_individual_pages() ajoutée avec succès!")
    print(f"📁 Fichier modifié: {filepath}")
else:
    print("❌ Marqueur d'insertion non trouvé")
    print("Recherche du contenu...")
    if 'export_dashboard' in content:
        print("✓ export_dashboard trouvé")
    if 'Dashboard HTML généré' in content:
        print("✓ Message trouvé")
