AUTEUR: 
BERTHOLET Thomas  : 24068
MENET     Antonin : 24104

Ce projet consiste à développer un bot capable de jouer au Kamisado efficacement dans un temps limité. L’objectif est de mettre en place une stratégie simple, mais cohérente, permettant de prendre l’avantage sur l’adversaire.

La stratégie adoptée repose principalement sur un jeu offensif.

Stratégie offensive :

progression rapide des pions vers la ligne d’arrivée
recherche de coups permettant de se rapprocher directement d’une victoire
mise sous pression constante de l’adversaire

Cette approche permet d’augmenter les chances de victoire à court terme.

Mais également une volonté de contrôler les possibilités de l’adversaire.

Contrôle du jeu adverse :

réduction du nombre de coups possibles pour l’adversaire
orientation vers des positions défavorables
création de situations où l’adversaire a peu de choix
recherche de blocages ou de coups forcés

Cela permet de rendre l’adversaire plus prévisible et de mieux anticiper ses actions.

Une attention est aussi portée à la sécurité.

Aspect défensif :

évitement des coups donnant une victoire immédiate à l’adversaire
limitation des situations de blocage pour soi-même
maintien d’un équilibre entre progression et prudence

Pour appliquer ces principes, le bot simule plusieurs coups et anticipe les réponses adverses sur quelques tours, tout en respectant une contrainte de temps.

Bibliothèques utilisées :

socket : communication avec le serveur
json : échange des données de jeu
struct : format des messages réseau
time : gestion du temps de calcul
random : messages aléatoires

Améliorations possibles :

améliorer la détection des pièges adverses
affiner le choix des coups les plus critiques
mieux adapter la stratégie selon la situation
optimiser la gestion du temps de calcul. 
