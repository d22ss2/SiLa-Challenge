
# Jour 1 : Système Bancaire sécurisé

## Langage : python
## Notion : POO

Il était question de concevoir un système bancaire orienté objet avec les classes *Compte*, *Compte épargne et Compte pro*
Implementater : méthodes
- déposer()
- retirer()
- virement() avec contrôle de solde
- Historique de transactions avec temps
- ajouter des exception(SoldeInsuffisantError, PlafondDepasserError)
- persistez les données en JSON.

# Le Compte
 C'est le compte simple. il permet de faire les opérations basique dépôt, retrait, virement. A la création le montant initial est 0. Dans ce compte on ne pas faire un retrait d'un montant supérieur au montant qui est déjà dans le compte, sinon s'affiche une erreur. 

 # Le Compte Épargne 
  Il hérite du compte simple. ici on ajoute un plafond, c'est à dire qu'on fixe une certaine somme maximale à empreinter. Dépasser cette somme une erreur affiche.
# Le Compte Pro
 Il hérite du compte simple. sa particularité est qu'il autorise les découverts. On peut emprunter un montant supérieur au montant contenu dans le compte. 

# Transaction 
 Permet de gérer les différentes opérations effectuées dans les comptes : dépôt, retrait, virement.
 
 # Banque 
  Ici nous avons créé un fichier banque.json pour sauvegarder chaque compte. 
  
