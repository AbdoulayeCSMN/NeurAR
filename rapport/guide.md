# Preparation a la soutenance - NeurAR

## 0. Strategie generale (pas de demo live)

Le jury va chercher la faille. La meilleure defense est de **ne jamais
pretendre que le systeme fonctionne de bout en bout si vous ne l'avez pas
verifie**. Construisez votre discours autour de ce qui EST verifiable :

- Le code existe, il est structure, il compile/tourne (montrez `curl
  http://localhost:8000/health`, `/architecture`, `/network` en local si
  possible, ou des captures d'ecran de ces reponses JSON).
- Chaque brique a ete pensee et codee individuellement (modele PyTorch,
  API FastAPI, scripts Unity).
- L'integration complete (casque AR + reseau Wi-Fi + Unity) necessite du
  materiel specifique que vous n'aviez pas en permanence.

### Phrases de transition utiles
- "Je n'ai pas de demonstration live aujourd'hui car elle necessite un
  appareil AR connecte au meme reseau que le backend ; je vais vous montrer
  le fonctionnement via les schemas et les echanges JSON reels."
- "Cette partie est validee au niveau du backend (je peux montrer la
  reponse de l'API), l'integration finale en AR est la derniere etape que
  je decris dans les perspectives."
- Ne dites jamais "ca marche parfaitement" si vous n'avez pas teste de bout
  en bout. Dites plutot "l'architecture est concue pour, voici comment je
  le validerais".

### Avant le jour J
- Preparez des **captures d'ecran** : reponses JSON de `/health`,
  `/architecture`, `/network` (via navigateur ou Postman/curl).
- Si possible, un **screen recording court** (meme sur telephone) de la
  scene Unity dans l'editeur (sans casque AR), montrant le placement et le
  rendu 3D.
- Imprimez ou ayez sous les yeux les diagrammes du rapport (architecture,
  MLP, sequence forward pass) : ils remplacent la demo.


## 1. Questions sur l'absence de demo

**Q : "Vous n'avez rien a nous montrer qui marche ?"**
> "Le backend est fonctionnel et testable independamment : voici la reponse
> de l'API `/network` qui renvoie l'etat complet du reseau (capture
> d'ecran). La partie Unity est developpee et la scene 3D se construit dans
> l'editeur ; l'execution sur un appareil AR physique est l'etape
> d'integration finale, qui necessite un materiel specifique."

**Q : "Comment peut-on etre sur que ca fonctionnerait reellement en AR ?"**
> "Le protocole d'echange (JSON, WebSocket) est defini et les classes C#
> Unity sont alignees terme a terme avec les modeles Pydantic du backend
> (alias camelCase). Le rendu 3D (NetworkRenderer, NeuronVisual,
> ConnectionVisual) est code et fonctionne dans la scene Unity standard ;
> le passage en AR ne change que le support d'affichage (AR Foundation),
> pas la logique de rendu."

**Q : "Avez-vous teste avec un vrai casque/telephone ?"**
> Soyez honnete si non testé : "Pas encore sur appareil physique, faute de
> materiel disponible au moment du developpement. C'est la prochaine etape
> que je decris dans les perspectives."


## 2. Questions sur le choix du modele (MLP, MNIST)

**Q : "Pourquoi un MLP et pas un CNN, qui est bien plus adapte a MNIST ?"**
> "Le choix du MLP est volontairement pedagogique : un MLP entierement
> connecte se pretend naturellement a une representation 3D claire (couches
> de neurones, connexions = poids). Un CNN introduirait des cartes de
> caracteristiques (feature maps) et des convolutions, plus difficiles a
> representer simplement en AR. Le MLP permet de se concentrer sur le
> pipeline de visualisation temps reel, qui est le coeur du projet. Le
> support d'autres architectures (CNN, RNN) est une perspective."

**Q : "Un seul pas de SGD a chaque backward_pass, est-ce vraiment de
l'apprentissage ?"**
> "Non, ce n'est pas un entrainement complet : c'est une **mise a jour de
> poids visible et instantanee**, choisie pour illustrer concretement.
> l'effet d'une retropropagation sur les poids et la perte, dans un cadre
> interactif. Un entrainement complet (plusieurs epoques) serait invisible
> a l'echelle humaine et ne se preterait pas a une animation en temps reel."

**Q : "BatchNorm avec un batch de taille 1, ca pose un probleme non ?"**
> "En mode `eval()`, BatchNorm utilise ses statistiques courantes
> (moyenne/variance accumulees), pas celles du batch courant. Cela evite
> l'instabilite d'un batch de taille 1 tout en laissant les gradients se
> propager normalement pour la mise a jour des poids."

**Q : "Pourquoi normaliser les poids avec tanh et les activations en min-max ?"**
> "Les poids peuvent prendre n'importe quelle valeur reelle ; `tanh` les
> ramene dans [-1, 1] en conservant leur signe, ce qui est directement
> exploitable pour la couleur/epaisseur des connexions en 3D. Les
> activations sont normalisees entre 0 et 1 (min-max) pour controler
> l'intensite visuelle des neurones, qui doit rester dans une plage
> affichable."


## 3. Questions sur l'architecture technique

**Q : "Que se passe-t-il si plusieurs clients Unity se connectent en meme
temps ? Le ModelManager est un singleton..."**
> "C'est une limite reelle du prototype : le `ModelManager` est partage par
> tous les clients, donc des actions concurrentes (deux `forward_pass`
> simultanes) pourraient se chevaucher. Pour une version multi-utilisateurs,
> il faudrait soit une instance de modele par session, soit un verrou
> (lock) autour des operations de calcul. C'est une piste d'amelioration
> que j'ai identifiee."

**Q : "2,4 Mo par message JSON, n'est-ce pas enorme pour du temps reel ?"**
> "C'est effectivement la limite actuelle, identifiee et documentee. Sur un
> reseau Wi-Fi local, cela reste gerable avec une limite de message
> WebSocket augmentee cote client. Pour aller plus loin, on pourrait
> envoyer uniquement les deltas (poids modifies) ou compresser le JSON
> (gzip), ce que je mentionne dans les perspectives."

**Q : "Pourquoi REST ET WebSocket, n'est-ce pas redondant ?"**
> "Non : le REST sert pour des requetes ponctuelles et sans etat (sante du
> serveur, configuration, instantane a la demande), typiquement pour du
> debug ou un client simple. Le WebSocket sert specifiquement au flux
> d'animation temps reel (couche par couche), qui necessite une connexion
> persistante et une diffusion progressive."

**Q : "Votre API n'a aucune authentification, n'importe qui sur le reseau
peut declencher un reset ou un forward_pass ?"**
> "C'est exact, et c'est un choix assume pour un prototype de demonstration
> sur reseau local ferme. Pour un deploiement reel, il faudrait ajouter une
> authentification (token), un controle d'acces, et limiter les actions
> sensibles (reset) a un role 'administrateur'."


## 4. Questions sur l'originalite / la contribution personnelle

**Q : "Qu'avez-vous code vous-meme par rapport aux librairies utilisees
(PyTorch, FastAPI, Unity AR Foundation) ?"**
> Soyez precis, listez :
> - La definition et l'entrainement du reseau `NeuroARNet` (architecture
>   configurable, extraction des activations/poids/biais).
> - La conception du **format d'echange** (`NetworkData`, `LayerData`,
>   `NeuronData`) et son alignement strict Python <-> C# (camelCase).
> - Le **protocole temps reel** (actions WebSocket, diffusion couche par
>   couche avec delai).
> - Les scripts Unity de rendu (`NetworkRenderer`, `NeuronVisual`,
>   `ConnectionVisual`), de communication (`WebSocketClient`,
>   `NetworkDataParser`, dispatcher thread principal) et d'interaction AR
>   (`ARPlacementManager`, `ARInteractionManager`).
> - PyTorch/FastAPI/AR Foundation sont des **outils**, le projet est
>   l'integration et le protocole qui les relient.

**Q : "En quoi c'est different de TensorBoard, Netron, ou
playground.tensorflow.org qui existent deja ?"**
> "Ces outils affichent des graphes ou des courbes en 2D, sur un ecran,
> de maniere statique ou semi-interactive. NeurAR propose une
> representation **3D, spatiale et immersive en realite augmentee**, avec
> une animation en temps reel synchronisee avec les calculs du modele. La
> difference est l'experience d'apprentissage : manipuler physiquement
> (zoom, rotation, selection) un objet 3D superpose au monde reel."

**Q : "Avez-vous valide l'interet pedagogique aupres d'utilisateurs ?"**
> Si non : "Pas encore, c'est une evaluation que je propose en
> perspective : un test utilisateur aupres d'etudiants pour mesurer l'apport
> par rapport a un support de cours classique."


## 5. Questions de "culture generale" IA / reseau (pour tester les bases)

Preparez des reponses courtes et sures :

- **Forward pass** : propagation de l'entree a travers les couches,
  chaque couche applique `Linear` puis (BatchNorm +) une fonction
  d'activation, jusqu'a la sortie.
- **Backward pass / retropropagation** : calcul du gradient de la perte
  par rapport a chaque poids (regle de la chaine), puis mise a jour des
  poids dans le sens oppose au gradient (descente de gradient).
- **Pourquoi ReLU sur les couches cachees ?** Simplicite, rapidite de
  calcul, evite la disparition du gradient (vanishing gradient) mieux que
  sigmoid/tanh.
- **Pourquoi Softmax en sortie ?** Transforme les scores en distribution de
  probabilites sur les 10 classes (somme = 1), adapte a la classification
  multi-classes.
- **A quoi sert BatchNorm ?** Stabilise et accelere l'entrainement en
  normalisant les activations de chaque couche.
- **WebSocket vs REST ?** REST = requete/reponse ponctuelle, sans etat.
  WebSocket = connexion bidirectionnelle persistante, ideale pour le flux
  temps reel et les notifications serveur -> client.
- **Pourquoi MNIST ?** Jeu de donnees standard, simple, rapide a charger,
  suffisant pour illustrer le fonctionnement d'un MLP sans nécessiter de
  ressources de calcul importantes.


## 6. Questions "destabilisantes" generiques (pieges relationnels)

**"Ce projet ne sert a rien, ca existe deja."**
> Restez calme, ne soyez pas sur la defensive : "Je comprends la remarque,
> des outils de visualisation existent en effet. La valeur ajoutee ici est
> la combinaison avec la realite augmentee et l'interaction temps reel, qui
> n'est pas couverte par les outils 2D existants."

**"Vous n'avez clairement pas fini ce projet."**
> "Le coeur technique (modele, backend, protocole, scripts Unity) est
> developpe et fonctionnel independamment. L'integration finale sur
> materiel AR est la derniere etape, que je presente comme perspective
> immediate plutot que comme un manque de travail."

**Le jury vous coupe / enchaine les questions rapidement**
> Ne paniquez pas. Repondez a la question posee, brievement, sans tout
> reexpliquer. Si vous ne savez pas : "Je n'ai pas approfondi ce point,
> mais je pense que [piste raisonnable]" -- mieux que d'inventer une
> reponse fausse.

**Question hors sujet (RGPD, biais MNIST, ethique IA...)**
> Repondez brievement et honnetement, puis recentrez : "C'est un point
> interessant, dans le cadre de ce projet (prototype pedagogique local) ce
> n'etait pas la priorite, mais ce serait a considerer pour un deploiement
> reel."


## 7. A retenir le jour J

1. Ne jamais affirmer qu'une chose marche si vous ne l'avez pas testee --
   reformulez en "concu pour" / "l'architecture le permet".
2. Toujours retomber sur vos pieds avec "perspectives" : chaque faiblesse
   identifiee = une amelioration future, pas un echec.
3. Restez calme et concis : une reponse courte et honnete vaut mieux qu'une
   longue reponse qui s'enfonce.
4. Ayez vos diagrammes (architecture, MLP, sequence) sous les yeux : ils
   remplacent la demo et montrent que vous maitrisez le systeme.
5. Connaissez par coeur les 3-4 chiffres cles : architecture du reseau
   (784-128-64-10), taille du JSON (~2,4 Mo), delai d'animation (100 ms),
   dataset (MNIST).
