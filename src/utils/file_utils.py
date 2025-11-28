"""
Utilitaires pour la lecture de fichiers
=======================================
Gestion des encodages, lecture robuste, etc.
"""

from pathlib import Path
from typing import Optional, List
import re


def safe_read(filepath: Path, encodings: Optional[List[str]] = None) -> str:
    """
    Lecture robuste d'un fichier texte avec plusieurs encodages.
    
    Args:
        filepath: Chemin du fichier à lire
        encodings: Liste d'encodages à essayer (défaut: utf-8-sig, utf-8, latin-1, cp1252)
    
    Returns:
        Contenu du fichier en string
    """
    if encodings is None:
        encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]
    
    for enc in encodings:
        try:
            return filepath.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    
    # Dernier recours: ignorer les erreurs
    return filepath.read_text(encoding="utf-8", errors="ignore")


def extract_powerlanguage_code(text: str) -> List[str]:
    """
    Extrait le code PowerLanguage depuis un fichier XML MultiCharts.
    
    Args:
        text: Contenu brut du fichier
    
    Returns:
        Liste des blocs de code extraits
    """
    pattern = re.compile(
        r"<PLESOURCE[^>]*><!\[CDATA\[(.*?)\]\]></PLESOURCE>",
        re.DOTALL | re.IGNORECASE
    )
    blocks = pattern.findall(text)
    return [b.strip() for b in blocks] if blocks else []


def clean_strategy_name(filename: str) -> str:
    """
    Nettoie le nom de fichier pour obtenir un nom de stratégie propre.
    
    Transformations:
        - Retire extension .txt
        - Décode caractères hex (a20 -> espace, b2e -> ., etc.)
        - Retire préfixes s_, sa_, sb_, sc_, sd_
        - Retire suffixe _RAW
    
    Args:
        filename: Nom du fichier
    
    Returns:
        Nom de stratégie nettoyé
    """
    name = filename.replace(".txt", "")
    
    # Décodage caractères spéciaux
    decode_map = {
        "a20": " ", "b2e": ".", "c2e": ".", "b3a": ":", "a3a": ":",
        "c20": "_", "b20": "_", "a24": "$", "b24": "$", "b2d": "-",
        "b28": "(", "b29": ")", "b2f": "/", "b26": "&",
    }
    
    for code, char in decode_map.items():
        name = name.replace(code, char)
    
    # Retirer préfixes
    name = re.sub(r'^(s_|sa_|sb_|sc_|sd_)', "", name, flags=re.IGNORECASE)
    
    # Retirer suffixe _RAW
    name = re.sub(r'_RAW$', "", name, flags=re.IGNORECASE)
    
    # Nettoyer espaces multiples
    name = re.sub(r"\s+", " ", name).strip()
    
    return name


def get_file_size_mb(filepath: Path) -> float:
    """Retourne la taille d'un fichier en MB."""
    return filepath.stat().st_size / (1024 * 1024)


def is_file_too_large(filepath: Path, max_mb: float = 10.0) -> bool:
    """Vérifie si un fichier est trop volumineux pour être traité."""
    return get_file_size_mb(filepath) > max_mb
