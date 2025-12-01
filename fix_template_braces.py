#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour corriger les accolades dans html_templates.py
Tous les {} JavaScript doivent devenir {{}} pour .format()
"""
import re
from pathlib import Path

def fix_javascript_braces(content):
    """
    Corrige les accolades JavaScript pour qu'elles fonctionnent avec .format()
    
    Stratégie:
    1. Trouver toutes les sections <script>
    2. Dans ces sections, doubler toutes les accolades qui ne sont pas déjà doublées
    """
    
    # Pattern pour trouver les sections script
    script_pattern = r'(<script>.*?</script>)'
    
    def fix_braces_in_script(match):
        script_content = match.group(1)
        
        # Remplacer { par {{ sauf si déjà {{
        # Et } par }} sauf si déjà }}
        fixed = script_content
        
        # Méthode : remplacer par des marqueurs temporaires
        # Protéger les {{ et }} existants
        fixed = fixed.replace('{{', '<<<DOUBLE_OPEN>>>')
        fixed = fixed.replace('}}', '<<<DOUBLE_CLOSE>>>')
        
        # Maintenant doubler tous les { et }
        fixed = fixed.replace('{', '{{')
        fixed = fixed.replace('}', '}}')
        
        # Restaurer les doubles accolades d'origine
        fixed = fixed.replace('<<<DOUBLE_OPEN>>>', '{{')
        fixed = fixed.replace('<<<DOUBLE_CLOSE>>>', '}}')
        
        return fixed
    
    # Appliquer la correction à toutes les sections script
    result = re.sub(script_pattern, fix_braces_in_script, content, flags=re.DOTALL)
    
    return result


def main():
    template_file = Path("C:/TradeData/V2/src/monte_carlo/html_templates.py")
    
    print("=" * 80)
    print("CORRECTION DES ACCOLADES JAVASCRIPT")
    print("=" * 80)
    
    # Lire le fichier
    print(f"\n📖 Lecture de {template_file.name}...")
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"   Taille originale: {len(content)} caractères")
    
    # Corriger
    print("\n🔧 Correction des accolades...")
    fixed_content = fix_javascript_braces(content)
    
    print(f"   Taille corrigée: {len(fixed_content)} caractères")
    
    # Sauvegarder
    backup_file = template_file.with_suffix('.py.bak')
    print(f"\n💾 Sauvegarde de l'original: {backup_file.name}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✍️  Écriture du fichier corrigé...")
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("\n" + "=" * 80)
    print("✅ CORRECTION TERMINÉE")
    print("=" * 80)
    print(f"\n📁 Fichier original sauvegardé: {backup_file}")
    print(f"📁 Fichier corrigé: {template_file}")
    print("\nVous pouvez maintenant relancer la génération HTML")


if __name__ == "__main__":
    main()
