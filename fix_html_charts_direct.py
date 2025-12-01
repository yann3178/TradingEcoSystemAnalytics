#!/usr/bin/env python3
"""
CORRECTIF DIRECT - Modification du fichier HTML généré
=======================================================

Au lieu de modifier le template Python, on va directement modifier
le fichier HTML généré pour corriger le bug des graphiques.

Cela permettra de tester immédiatement sans régénérer.
"""

from pathlib import Path
import re

HTML_FILE = Path("C:/TradeData/V2/outputs/html_reports/montecarlo/all_strategies_montecarlo.html")

print("=" * 70)
print("CORRECTIF DIRECT DES GRAPHIQUES")
print("=" * 70)
print()

# 1. Vérifier que le fichier existe
if not HTML_FILE.exists():
    print(f"❌ Fichier introuvable: {HTML_FILE}")
    exit(1)

print(f"✅ Fichier trouvé: {HTML_FILE.name}")
print()

# 2. Créer un backup
backup = HTML_FILE.parent / f"{HTML_FILE.stem}_backup_before_fix.html"
import shutil
shutil.copy2(HTML_FILE, backup)
print(f"✅ Backup créé: {backup.name}")
print()

# 3. Lire le contenu
print("📝 Lecture du fichier HTML...")
content = HTML_FILE.read_text(encoding='utf-8')
print(f"   Taille: {len(content) / 1024:.1f} KB")
print()

# 4. Vérifier si déjà corrigé
if "statusChartInstance" in content:
    print("ℹ️  Le fichier semble déjà avoir été corrigé.")
    print("   Si les graphiques ne se mettent pas à jour, il y a un autre problème.")
    print()
else:
    print("📝 Application des corrections...")
    print()
    
    # Correction 1: Ajouter les variables globales
    pattern1 = r"(Chart\.defaults\.font\.size = 12;)"
    replacement1 = r'''\1
        
        // =====================================================================
        // VARIABLES GLOBALES POUR LES GRAPHIQUES (CORRECTIF)
        // =====================================================================
        
        let statusChartInstance = null;
        let scatterChartInstance = null;
        let topPnlChartInstance = null;
        let topRatioChartInstance = null;
'''
    
    if re.search(pattern1, content):
        content = re.sub(pattern1, replacement1, content, count=1)
        print("✅ 1. Variables globales ajoutées")
    else:
        print("⚠️  1. Pattern Chart.defaults non trouvé")
    
    # Correction 2: Stocker les instances
    replacements = [
        ("new Chart(document.getElementById('statusChart')", 
         "statusChartInstance = new Chart(document.getElementById('statusChart')"),
        ("new Chart(document.getElementById('scatterChart')", 
         "scatterChartInstance = new Chart(document.getElementById('scatterChart')"),
        ("new Chart(document.getElementById('topPnlChart')", 
         "topPnlChartInstance = new Chart(document.getElementById('topPnlChart')"),
        ("new Chart(document.getElementById('topRatioChart')", 
         "topRatioChartInstance = new Chart(document.getElementById('topRatioChart')"),
    ]
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new, 1)
    print("✅ 2. Instances Chart.js stockées")
    
    # Correction 3: Ajouter la fonction updateCharts
    update_function = '''
        // =====================================================================
        // MISE À JOUR DES GRAPHIQUES (CORRECTIF)
        // =====================================================================
        
        /**
         * Met à jour tous les graphiques après recalcul
         */
        function updateCharts(okCount, warningCount, highRiskCount) {
            console.log('🔄 Mise à jour des graphiques...', {okCount, warningCount, highRiskCount});
            
            // 1. Pie Chart - Distribution par statut
            if (statusChartInstance) {
                statusChartInstance.data.datasets[0].data = [okCount, warningCount, highRiskCount];
                statusChartInstance.update('none');
                console.log('  ✅ Pie chart mis à jour');
            } else {
                console.log('  ❌ statusChartInstance est null');
            }
            
            // 2. Scatter Chart - Return/DD vs Ruine
            if (scatterChartInstance) {
                const tbody = document.getElementById('table-body');
                const rows = tbody.querySelectorAll('tr');
                const newData = [];
                const newColors = [];
                
                rows.forEach(row => {
                    const status = row.getAttribute('data-status');
                    const ruinCell = row.querySelectorAll('td')[8];
                    const ratioCell = row.querySelectorAll('td')[9];
                    
                    if (ruinCell && ratioCell) {
                        const ruin = parseFloat(ruinCell.textContent) || 0;
                        const ratio = parseFloat(ratioCell.textContent) || 0;
                        
                        newData.push({ x: ruin, y: Math.min(ratio, 10) });
                        newColors.push(
                            status === 'OK' ? '#00d4aa' : 
                            status === 'WARNING' ? '#ffe66d' : '#ff6b6b'
                        );
                    }
                });
                
                scatterChartInstance.data.datasets[0].data = newData;
                scatterChartInstance.data.datasets[0].backgroundColor = newColors;
                scatterChartInstance.update('none');
                console.log('  ✅ Scatter chart mis à jour avec', newData.length, 'points');
            } else {
                console.log('  ❌ scatterChartInstance est null');
            }
            
            // 3. Top P&L Chart - Recalculer le top 10
            if (topPnlChartInstance) {
                // Récupérer les stratégies visibles du tableau
                const tbody = document.getElementById('table-body');
                const rows = Array.from(tbody.querySelectorAll('tr:not([style*="display: none"])'));
                
                // Trier par P&L
                const strategies = rows.map(row => {
                    const cells = row.querySelectorAll('td');
                    return {
                        name: cells[0].textContent.substring(0, 25),
                        pnl: parseFloat(cells[5].textContent.replace(/[$,]/g, '')) || 0
                    };
                }).sort((a, b) => b.pnl - a.pnl).slice(0, 10);
                
                topPnlChartInstance.data.labels = strategies.map(s => s.name);
                topPnlChartInstance.data.datasets[0].data = strategies.map(s => s.pnl);
                topPnlChartInstance.update('none');
                console.log('  ✅ Top P&L chart mis à jour');
            }
            
            // 4. Top Ratio Chart - Recalculer le top 10
            if (topRatioChartInstance) {
                const tbody = document.getElementById('table-body');
                const rows = Array.from(tbody.querySelectorAll('tr:not([style*="display: none"])'));
                
                // Trier par Return/DD Ratio
                const strategies = rows.map(row => {
                    const cells = row.querySelectorAll('td');
                    return {
                        name: cells[0].textContent.substring(0, 25),
                        ratio: parseFloat(cells[9].textContent) || 0
                    };
                }).filter(s => s.ratio < 100).sort((a, b) => b.ratio - a.ratio).slice(0, 10);
                
                topRatioChartInstance.data.labels = strategies.map(s => s.name);
                topRatioChartInstance.data.datasets[0].data = strategies.map(s => s.ratio);
                topRatioChartInstance.data.datasets[0].backgroundColor = strategies.map(s => 
                    s.ratio >= 2 ? '#00d4aa' : '#ffe66d'
                );
                topRatioChartInstance.update('none');
                console.log('  ✅ Top Ratio chart mis à jour');
            }
            
            console.log('✅ Tous les graphiques ont été mis à jour');
        }
'''
    
    # Insérer avant la fonction findRecommendedCapital
    pattern3 = r"(        function findRecommendedCapital\(strategyName\))"
    if re.search(pattern3, content):
        content = re.sub(pattern3, update_function + "\n        \\1", content, count=1)
        print("✅ 3. Fonction updateCharts() ajoutée")
    else:
        print("⚠️  3. Pattern findRecommendedCapital non trouvé")
    
    # Correction 4: Appeler updateCharts dans recalculateAll
    pattern4 = r"(            console\.log\('Recalcul terminé:',)"
    replacement4 = r"""            
            // Mettre à jour les graphiques
            updateCharts(okCount, warningCount, highRiskCount);
            
\1"""
    
    if re.search(pattern4, content):
        content = re.sub(pattern4, replacement4, content, count=1)
        print("✅ 4. Appel à updateCharts() ajouté dans recalculateAll()")
    else:
        print("⚠️  4. Pattern console.log('Recalcul terminé') non trouvé")
    
    print()
    
    # 5. Sauvegarder
    print("💾 Sauvegarde du fichier corrigé...")
    HTML_FILE.write_text(content, encoding='utf-8')
    print(f"✅ Fichier sauvegardé: {HTML_FILE.name}")

print()
print("=" * 70)
print("✅ CORRECTION TERMINÉE")
print("=" * 70)
print()
print("🧪 TEST:")
print("   1. Ouvrir le fichier dans le navigateur:")
print(f"      {HTML_FILE}")
print()
print("   2. Ouvrir la console F12")
print()
print("   3. Déplacer un slider et cliquer sur 'Recalculer'")
print()
print("   4. Vous devriez voir dans la console:")
print("      🔄 Mise à jour des graphiques...")
print("      ✅ Pie chart mis à jour")
print("      ✅ Scatter chart mis à jour")
print("      ✅ Top P&L chart mis à jour")
print("      ✅ Top Ratio chart mis à jour")
print()
print("   5. Les 4 graphiques doivent se mettre à jour visuellement ! ✨")
print()
print(f"📁 Backup disponible: {backup.name}")
print()
