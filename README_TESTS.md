# SEB OPS SYSTEM v5 - Test Suite

## 🧪 Full System Test

Ce système de test automatisé vérifie toutes les fonctionnalités principales de l'application.

### Prérequis

1. **Chrome Browser** installé
2. **Python 3.x** avec pip
3. **ChromeDriver** compatible avec votre version de Chrome

### Installation

```powershell
# Activer l'environnement virtuel
.venv\Scripts\Activate.ps1

# Installer Selenium
pip install -r requirements-test.txt

# Télécharger ChromeDriver (si pas déjà installé)
# https://chromedriver.chromium.org/downloads
# Placer chromedriver.exe dans le PATH ou dans le dossier du projet
```

### Lancer les tests

```powershell
# 1. S'assurer que l'app tourne
python app.py

# 2. Dans un nouveau terminal, lancer les tests
python test_full_system.py
```

### Tests effectués

1. ✅ **Créer une catégorie** - Créer "TEST CATEGORY" avec couleur orange
2. ✅ **Éditer le nom de la catégorie** - Renommer en "TEST CATEGORY EDITED"
3. ✅ **Créer une personne** - Ajouter "Test User"
4. ✅ **Créer une tâche** - Ajouter "Test Task for Automation"
5. ✅ **Assigner une personne** - Assigner "Test User" à la tâche
6. ✅ **Éditer la tâche** - Modifier le texte en "Test Task - EDITED"
7. ✅ **Ajouter des commentaires** - Notes sur 3 jours différents
8. ✅ **Marquer comme fait** - Cocher la checkbox de la tâche
9. ✅ **Changer de semaine** - Naviguer vers semaine suivante
10. ✅ **Commentaire nouvelle semaine** - Ajouter une note dans la nouvelle semaine
11. ✅ **Click TODAY** - Retour à la semaine courante

### Résultat attendu

```
🧪 STARTING FULL SYSTEM TEST SUITE
============================================================

📋 TEST 1: Creating new category...
✅ TEST 1 PASSED: Category created successfully

✏️ TEST 2: Editing category name...
✅ TEST 2 PASSED: Category name edited successfully

👤 TEST 3: Creating new person...
✅ TEST 3 PASSED: Person created successfully

... (tous les tests)

============================================================
✅ ALL TESTS PASSED! 🎉
============================================================
```

### En cas d'erreur

- Vérifier que l'app tourne sur http://127.0.0.1:5000
- Vérifier que ChromeDriver est installé et compatible
- Vérifier la console pour les messages d'erreur détaillés

### Automatisation

Vous pouvez intégrer ces tests dans votre workflow:

```powershell
# Script pour tester après chaque modification
python test_full_system.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Tests passed - Safe to commit" -ForegroundColor Green
} else {
    Write-Host "❌ Tests failed - Fix before committing" -ForegroundColor Red
}
```

### Notes

- Les tests créent des données de test (catégorie, personne, tâche)
- Ces données restent dans la base après les tests
- Vous pouvez les supprimer manuellement ou réinitialiser la base
- Le navigateur Chrome s'ouvre en mode maximisé pendant les tests
- Il se ferme automatiquement à la fin (après 3 secondes de pause)
