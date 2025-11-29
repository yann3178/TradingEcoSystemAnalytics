# Templates HTML

Ce répertoire contient les templates HTML utilisés par les générateurs.

## Templates disponibles

### correlation_page.html (optionnel)

Template pour les pages de corrélation individuelles. 

**Note**: Actuellement, le générateur utilise un template inline si ce fichier n'existe pas. Le template inline est complet et fonctionnel, donc ce fichier externe est optionnel.

Si vous souhaitez créer un template externe pour faciliter la personnalisation du design, vous pouvez créer `correlation_page.html` avec les placeholders suivants :

- `{{strategy_id}}` - Nom complet de la stratégie
- `{{strategy_name}}` - Nom sans le symbole
- `{{symbol}}` - Symbole du marché
- `{{status}}` - Statut de corrélation (Diversifiant, Modéré, etc.)
- `{{status_emoji}}` - Emoji du statut
- `{{status_class}}` - Classe CSS du statut
- `{{score_davey}}` - Score Davey
- `{{n_corr_lt}}` - Nombre de corrélations LT
- `{{n_corr_ct}}` - Nombre de corrélations CT
- `{{avg_corr_lt}}` - Corrélation moyenne LT
- `{{avg_corr_ct}}` - Corrélation moyenne CT
- `{{delta_avg}}` - Delta moyenne (CT - LT)
- `{{max_corr_lt}}` - Corrélation max LT
- `{{most_correlated}}` - JSON des stratégies les plus corrélées
- `{{least_correlated}}` - JSON des stratégies les moins corrélées
- `{{alerts}}` - JSON des alertes
- `{{distribution}}` - JSON de la distribution
- `{{timestamp}}` - Date/heure de génération

Le générateur détectera automatiquement la présence du template et l'utilisera.
