import json
from datetime import datetime
import os

#erreur quand on veut retirer plus d'argent qu'on a
class SoldeInsuffisantError (Exception) :
    def __init__(self, solde, montant):
        self.solde = solde
        self.montant = montant
        super().__init__(f"Pas assez d'argent! vous avez {solde}fcfa, mais vous voulez retirer {montant}fcfa")

#erreur quand on depasse la limite de retrait autorisee
class PlafondDepasserError (Exception) :
    def __init__(self, plafond, montant):
        self.plafond = plafond
        self.montant = montant
        super().__init__(f"Limite depassee! Maximun autorise: {plafond}fcfa, vous voulez retirer {montant}fcfa")

#gestion des transaction(depot, retrait, virement)
class Transaction :
    def __init__(self, type_transaction, montant):
        self.type = type_transaction
        self.montant = montant
        self.date = datetime.now()

# affichage de la transaction 
    def __str__(self):
        return f"[{self.date.strftime('%d/%m/%y  %H:%M')}] {self.type}:  {self.montant}fcfa "

class Compte:
    def __init__(self, titulaire, numero_compte, solde_initial=0):
        self.titulaire = titulaire
        self.numero_compte = numero_compte
        self._solde = solde_initial
        self.historique = []

        #si on met de l'argent dans le compte a la creation 
        if solde_initial > 0:
            self._ajouter_transaction("depot initial", solde_initial)
    
    #proprite pour acceder au solde
    @property
    def solde(self):
        return self._solde

    def _ajouter_transaction(self, type_transaction, montant):
        transaction = Transaction(type_transaction, montant)
        self.historique.append(transaction)
    
    def deposer(self, montant):
        if montant <= 0:
            print("Erreur : le montant doit etre positif!")
            return False
        self._solde += montant
        self._ajouter_transaction("depot", montant)
        print(f"Depot de {montant}fcfa effectue avec succes. Votre nouveau solde est de: {self._solde}fcfa")
        return True
    
    def retirer(self, montant):
        if montant <= 0:
            print("Error: le montant doit etre positif!")
            return False
        if montant > self._solde:
            raise SoldeInsuffisantError(self._solde, montant)
        self._solde -= montant
        self._ajouter_transaction("retrait", montant)
        print(f"Retrait de {montant}fcfa effectue avec succes. Votre nouveau solde est de: {self._solde}fcfa")
        return True

    def virement(self, compte_destination, montant):
        if montant <= 0:
            print("Erreur: le montant doit etre positif! ")
            return False
        if montant > self._solde:
            raise SoldeInsuffisantError(self._solde, montant)

        self._solde -= montant
        compte_destination._solde += montant

        self._ajouter_transaction("virement effectue", montant)
        compte_destination._ajouter_transaction("virement recu", montant)

        return True

    def afficher_historique(self):
        # affiche toutes les transactions du compte
        print(f"\n--- Historique du compte {self.numero_compte} ---")
        if not self.historique:
            print("Aucune transaction pour ce compte")
        else:
            for transaction in self.historique:
                print(transaction)
        print(f"Solde actuel: {self._solde}fcfa\n")
    
    # methodes pour la sauvegarde JSON
    def to_dict(self):
        #Convertit le compte en dictionnaire (pour JSON)
        # On transforme chaque transaction en dictionnaire
        transactions_dict = []
        for t in self.historique:
            transactions_dict.append({
                'type': t.type,
                'montant': t.montant,
                'date': t.date.isoformat()
            })
        
        return {
            'titulaire': self.titulaire,
            'numero_compte': self.numero_compte,
            'solde': self._solde,
            'transactions': transactions_dict
        }
    
    @classmethod
    def from_dict(cls, data):
        #Cree un compte à partir d'un dictionnaire (chargement JSON)
        compte = cls(data['titulaire'], data['numero_compte'], data['solde'])
        compte.historique = []
        
        # Reconstruire l'historique
        for t_data in data['transactions']:
            transaction = Transaction(
                t_data['type'], 
                t_data['montant']
            )
            # restaurer la date originale
            transaction.date = datetime.fromisoformat(t_data['date'])
            compte.historique.append(transaction)
        
        return compte

class CompteEpargne(Compte):    
    def __init__(self, titulaire, numero_compte, solde_initial=0, plafond_retrait=500):
        # Appel du constructeur de la classe parent (Compte)
        super().__init__(titulaire, numero_compte, solde_initial)
        self.plafond_retrait = plafond_retrait 
        self.retraits_aujourdhui = 0  
    
    def retirer(self, montant):
        # Vérifier qu'on ne dépasse pas le plafond
        if self.retraits_aujourdhui + montant > self.plafond_retrait:
            raise PlafondDepasserError(self.plafond_retrait, montant)
        
        # Appeler la méthode retirer de la classe parent
        resultat = super().retirer(montant)
        
        # Si le retrait a réussi, on met à jour le compteur
        if resultat:
            self.retraits_aujourdhui += montant
        
        return resultat

class ComptePro(Compte):
    # autorise un découvert (on peut avoir un solde négatif)
    
    def __init__(self, titulaire, numero_compte, solde_initial=0, decouvert_autorise=1000):
        super().__init__(titulaire, numero_compte, solde_initial)
        self.decouvert_autorise = decouvert_autorise  # Limite de découvert
    
    def retirer(self, montant):
        if montant <= 0:
            print("Erreur: le montant doit être positif!")
            return False
        
        # Vérification avec découvert autorisé
        if montant > self._solde + self.decouvert_autorise:
            raise SoldeInsuffisantError(self._solde + self.decouvert_autorise, montant)
        
        self._solde -= montant
        self._ajouter_transaction("retrait", montant)
        
        if self._solde < 0:
            print(f"Attention: vous êtes à découvert! Solde: {self._solde}fcfa")
        
        print(f"Retrait de {montant}fcfa réussi. Nouveau solde: {self._solde}fcfa")
        return True

class Banque:
    # gerer tous les comptes et la sauvegarde JSON
    
    def __init__(self, fichier="banque.json"):
        self.comptes = []
        self.fichier = fichier
    
    def ajouter_compte(self, compte):
        self.comptes.append(compte)
        print(f"Compte {compte.numero_compte} créé pour {compte.titulaire}")
    
    def trouver_compte(self, numero_compte):
        for compte in self.comptes:
            if compte.numero_compte == numero_compte:
                return compte
        return None
    
    def sauvegarder(self):
        donnees = {
            'comptes': [compte.to_dict() for compte in self.comptes]
        }
        
        with open(self.fichier, 'w', encoding='utf-8') as f:
            json.dump(donnees, f, indent=4, ensure_ascii=False)

        print(f"Données sauvegardées dans {self.fichier}")
    
    def charger(self):
        #charge les comptes depuis un fichier JSON
        if not os.path.exists(self.fichier):
            print("Aucune sauvegarde trouvée")
            return
        
        with open(self.fichier, 'r', encoding='utf-8') as f:
            donnees = json.load(f)
        
        self.comptes = []
        for compte_data in donnees['comptes']:
            compte = Compte.from_dict(compte_data)
            self.comptes.append(compte)
        
        print(f"Données chargées depuis {self.fichier}")

def main():
    print("="*50)
    print("SYSTEME BANCAIRE")
    print("="*50)

    banque = Banque("test_banque.json")
    
    print("\n--- Création des comptes ---")
    compte1 = Compte("Tchalong Megane", "CM001", 10000)
    compte2 = CompteEpargne("Tcho Pierre", "CM002", 50000, 3000)
    compte3 = ComptePro("Ngassam Joyce", "CM003", 200000, 50000)
    
    banque.ajouter_compte(compte1)
    banque.ajouter_compte(compte2)
    banque.ajouter_compte(compte3)
    
    print("\n--- Test des opérations ---")
    
    compte1.deposer(20000)
    compte1.retirer(200000)
    
    print("\n--- Test: retrait trop important ---")
    try:
        compte2.retirer(60000)
    except SoldeInsuffisantError as e:
        print(f"Exception attrapée: {e}")
    
    print("\n--- Test: plafond dépassé (compte épargne) ---")
    try:
        compte2.retirer(4000)
    except PlafondDepasserError as e:
        print(f"Exception attrapée: {e}")
    
    print("\n--- Test: virement ---")
    compte1.virement(compte3, 15000)
    
    print("\n--- Test: découvert autorisé (compte pro) ---")
    compte3.retirer(205000)
    
    print("\n--- Historiques des comptes ---")
    compte1.afficher_historique()
    compte2.afficher_historique()
    compte3.afficher_historique()
    
    print("\n--- Sauvegarde ---")
    banque.sauvegarder()
    
    print("\n--- Test de chargement ---")
    nouvelle_banque = Banque("test_banque.json")
    nouvelle_banque.charger()
    
    print(f"\nComptes chargés: {len(nouvelle_banque.comptes)}")

# Lancer le programme
if __name__ == "__main__":
    main()

