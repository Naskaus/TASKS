# Guide de Déploiement N.O.P.S. v0.3

## 🚀 Nouveautés v0.3
- **Nouvelle Page d'Accueil (Cyberpunk)** : `welcome.html` est maintenant la page par défaut (`/`).
- **Checklists Intégrées** : SHARK 2.0, RED DRAGON, MANDARIN accessibles depuis l'accueil.
- **Routing Mis à Jour** :
  - `/` -> Accueil Cyberpunk (Checklists & Menu)
  - `/landing` -> Ancienne Landing Page (Animations N.O.P.S.)
  - `/tasks` -> Application Principale (Tableau de bord)
- **Fix Navigation** : Le bouton "TASKS" redirige correctement vers `/landing`.

---

## 📥 Procédure de Mise à Jour (PythonAnywhere)

### 1. Connexion
Ouvrez une console Bash sur [PythonAnywhere](https://www.pythonanywhere.com/).

### 2. Récupération du Code (v0.3)
Exécutez les commandes suivantes pour tout mettre à jour :

```bash
cd /home/Naskaus/TASKS

# Sauvegarder vos changements locaux (DB, etc.) si nécessaire
git stash

# Récupérer la dernière version
git fetch --all
git fetch --tags

# Basculer sur la version v0.3
git checkout v0.3
# OU rester sur main : git pull origin main
```

### 3. Redémarrage
1. Allez dans l'onglet **Web**.
2. Cliquez sur le bouton vert **Reload**.

---

## ✅ Vérification
- Accédez à `https://tasks-naskaus.pythonanywhere.com/`
- Vous devez voir la nouvelle interface Cyberpunk.
- Testez le bouton **TASKS** -> Doit aller sur la page d'animation N.O.P.S.
- Testez le bouton **PROCEDURES** -> Doit ouvrir le menu des checklists.

---

## 🆘 En cas de problème (Rollback)
Si quelque chose ne va pas, revenez à la version précédente :

```bash
cd /home/Naskaus/TASKS
git checkout v0.22
# Puis Reload sur l'onglet Web
```
