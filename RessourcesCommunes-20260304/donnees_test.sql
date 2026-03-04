-- ============================================================
-- DUMP DE DONNÉES DE TEST - Projet PlatonAAV
-- ============================================================
-- Ce fichier contient un jeu de données complet pour permettre
-- à chaque groupe de tester son travail indépendamment.
--
-- Contenu:
-- - 20 AAV (types entiers, flottants, opérateurs, etc.)
-- - 1 Ontologie de référence (Langage C)
-- - 5 Apprenants avec profils variés
-- - Statuts d'apprentissage pour chaque apprenant
-- - Tentatives d'exercices
-- - Activités pédagogiques
-- - Prompts de fabrication
--
-- Ordre d'insertion respecte les contraintes de clés étrangères
-- ============================================================

-- ============================================================
-- 1. TABLE: aav (GROUPE 1)
-- ============================================================
-- Description: 20 AAV couvrant la syntaxe C avec prérequis en chaîne

INSERT INTO aav (id_aav, nom, libelle_integration, discipline, enseignement, type_aav, description_markdown, prerequis_ids, prerequis_externes_codes, code_prerequis_interdisciplinaire, aav_enfant_ponderation, type_evaluation, ids_exercices, prompts_fabrication_ids, regles_progression, is_active, version) VALUES
(1, 'Types entiers', 'les types entiers (int, short, long)', 'Programmation', 'Langage C', 'Atomique', 'Comprendre et utiliser les types entiers en C', '[]', '[]', NULL, '[]', 'Calcul Automatisé', '[101, 102]', '[1]', '{"seuil_succes": 0.8, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 3, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1),

(2, 'Type caractère', 'le type char et les caractères ASCII', 'Programmation', 'Langage C', 'Atomique', 'Maîtriser le type char et la table ASCII', '[1]', '[]', NULL, '[]', 'Calcul Automatisé', '[103, 104]', '[2]', '{"seuil_succes": 0.8, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 3, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1),

(3, 'Types flottants', 'les types flottants (float, double)', 'Programmation', 'Langage C', 'Atomique', 'Utiliser les nombres à virgule flottante', '[1]', '[]', NULL, '[]', 'Calcul Automatisé', '[105, 106]', '[3]', '{"seuil_succes": 0.8, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 3, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1),

(4, 'Déclaration de variables', 'la déclaration et initialisation de variables', 'Programmation', 'Langage C', 'Atomique', 'Maîtriser la déclaration de variables', '[1, 2, 3]', '[]', NULL, '[]', 'Calcul Automatisé', '[107, 108]', '[4]', '{"seuil_succes": 0.9, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 3, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1),

(5, 'Opérateurs arithmétiques', 'les opérateurs arithmétiques (+, -, *, /, %)', 'Programmation', 'Langage C', 'Atomique', 'Utiliser les opérateurs arithmétiques', '[1, 4]', '[]', NULL, '[]', 'Calcul Automatisé', '[109, 110]', '[5]', '{"seuil_succes": 0.8, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 3, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1),

(6, 'Opérateurs de comparaison', 'les opérateurs de comparaison (==, !=, <, >)', 'Programmation', 'Langage C', 'Atomique', 'Comparer des valeurs en C', '[1, 5]', '[]', NULL, '[]', 'Compréhension par Chute', '[111, 112]', '[6]', '{"seuil_succes": 0.7, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 2, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1),

(7, 'Opérateurs logiques', 'les opérateurs logiques (&&, ||, !)', 'Programmation', 'Langage C', 'Atomique', 'Combiner des conditions logiques', '[6]', '[]', NULL, '[]', 'Compréhension par Chute', '[113, 114]', '[7]', '{"seuil_succes": 0.7, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 2, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1),

(8, 'Structure if-else', 'les structures conditionnelles if-else', 'Programmation', 'Langage C', 'Atomique', 'Contrôler le flux avec if-else', '[6, 7]', '[]', NULL, '[]', 'Validation par Invention', '[115, 116]', '[8]', '{"seuil_succes": 0.8, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 2, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1),

(9, 'Boucle while', 'les boucles while', 'Programmation', 'Langage C', 'Atomique', 'Répéter des instructions avec while', '[6, 8]', '[]', NULL, '[]', 'Calcul Automatisé', '[117, 118]', '[9]', '{"seuil_succes": 0.8, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 3, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1),

(10, 'Boucle for', 'les boucles for', 'Programmation', 'Langage C', 'Atomique', 'Répéter avec la boucle for', '[9]', '[]', NULL, '[]', 'Calcul Automatisé', '[119, 120]', '[10]', '{"seuil_succes": 0.8, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 3, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1),

(11, 'Fonctions', 'la définition et l''appel de fonctions', 'Programmation', 'Langage C', 'Atomique', 'Structurer le code avec des fonctions', '[4, 8]', '[]', NULL, '[]', 'Validation par Invention', '[121, 122]', '[11]', '{"seuil_succes": 0.9, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 3, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1),

(12, 'Paramètres de fonctions', 'les paramètres et valeurs de retour', 'Programmation', 'Langage C', 'Atomique', 'Passer des données aux fonctions', '[11]', '[]', NULL, '[]', 'Calcul Automatisé', '[123, 124]', '[12]', '{"seuil_succes": 0.8, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 3, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1),

(13, 'Tableaux', 'la déclaration et utilisation des tableaux', 'Programmation', 'Langage C', 'Atomique', 'Stocker plusieurs valeurs', '[1, 4, 10]', '[]', NULL, '[]', 'Calcul Automatisé', '[125, 126]', '[13]', '{"seuil_succes": 0.8, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 3, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1),

(14, 'Chaînes de caractères', 'la manipulation des chaînes (string.h)', 'Programmation', 'Langage C', 'Atomique', 'Manipuler les chaînes de caractères', '[2, 13]', '[]', NULL, '[]', 'Calcul Automatisé', '[127, 128]', '[14]', '{"seuil_succes": 0.8, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 3, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1),

(15, 'Pointeurs', 'la compréhension des pointeurs', 'Programmation', 'Langage C', 'Atomique', 'Maîtriser les pointeurs', '[1, 4]', '[]', NULL, '[]', 'Compréhension par Chute', '[129, 130]', '[15]', '{"seuil_succes": 0.7, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 3, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1),

(16, 'Allocation mémoire', 'l''allocation dynamique (malloc, free)', 'Programmation', 'Langage C', 'Atomique', 'Gérer la mémoire dynamiquement', '[15]', '[]', NULL, '[]', 'Validation par Invention', '[131, 132]', '[16]', '{"seuil_succes": 0.9, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 3, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1),

(17, 'Structures (struct)', 'la définition de structures', 'Programmation', 'Langage C', 'Atomique', 'Créer des types personnalisés', '[4, 15]', '[]', NULL, '[]', 'Validation par Invention', '[133, 134]', '[17]', '{"seuil_succes": 0.8, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 2, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1),

(18, 'Fichiers', 'la lecture et écriture de fichiers', 'Programmation', 'Langage C', 'Atomique', 'Manipuler des fichiers', '[2, 15]', '[]', NULL, '[]', 'Validation par Invention', '[135, 136]', '[18]', '{"seuil_succes": 0.8, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 2, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1),

(19, 'Types de base', 'les types de base du langage C', 'Programmation', 'Langage C', 'Composite (Chapitre)', 'Chapitre: tous les types de base', '[]', '[]', NULL, '[[1, 0.25], [2, 0.25], [3, 0.5]]', 'Agrégation (Composite)', '[101, 102, 103, 104, 105, 106]', '[1, 2, 3]', '{"seuil_succes": 0.8, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 3, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1),

(20, 'Flux de contrôle', 'les structures de contrôle', 'Programmation', 'Langage C', 'Composite (Chapitre)', 'Chapitre: if, while, for', '[]', '[]', NULL, '[[8, 0.4], [9, 0.3], [10, 0.3]]', 'Agrégation (Composite)', '[115, 116, 117, 118, 119, 120]', '[8, 9, 10]', '{"seuil_succes": 0.8, "maitrise_requise": 1.0, "nombre_succes_consecutifs": 3, "nombre_jugements_pairs_requis": 3, "tolerance_jugement": 0.2}', 1, 1);

-- ============================================================
-- 2. TABLE: ontology_reference (GROUPE 1)
-- ============================================================

INSERT INTO ontology_reference (id_reference, discipline, aavs_ids_actifs, description) VALUES
(1, 'Langage C', '[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]', 'Ontologie complète de la syntaxe C pour débutants');

-- ============================================================
-- 3. TABLE: apprenant (GROUPE 2)
-- ============================================================
-- 5 profils d'apprenants variés pour tester tous les scénarios

INSERT INTO apprenant (id_apprenant, nom_utilisateur, email, ontologie_reference_id, statuts_actifs_ids, codes_prerequis_externes_valides, date_inscription, derniere_connexion, is_active) VALUES
-- Apprenant 1: Débutant complet (aucune connaissance)
(1, 'alice_debutante', 'alice@example.com', 1, '[]', '[]', '2026-01-15 10:00:00', '2026-02-20 14:30:00', 1),

-- Apprenant 2: En progression (quelques AAV commencés)
(2, 'bob_progressif', 'bob@example.com', 1, '[1, 2, 5, 6]', '[]', '2026-01-10 09:00:00', '2026-02-21 10:15:00', 1),

-- Apprenant 3: Avancé (presque tout maîtrisé)
(3, 'charlie_expert', 'charlie@example.com', 1, '[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]', '[]', '2025-11-01 08:00:00', '2026-02-21 16:45:00', 1),

-- Apprenant 4: Bloqué sur des prérequis (échecs répétés)
(4, 'david_bloque', 'david@example.com', 1, '[1, 2, 5, 6]', '[]', '2026-01-20 11:00:00', '2026-02-18 09:30:00', 1),

-- Apprenant 5: Révision nécessaire (maîtrise ancienne)
(5, 'eve_revision', 'eve@example.com', 1, '[1, 2, 3, 4, 5]', '[]', '2025-09-01 10:00:00', '2026-02-01 14:00:00', 1);

-- ============================================================
-- 4. TABLE: statut_apprentissage (GROUPE 3)
-- ============================================================
-- Statuts variés pour tester tous les opérateurs

INSERT INTO statut_apprentissage (id, id_apprenant, id_aav_cible, niveau_maitrise, historique_tentatives_ids, date_debut_apprentissage, date_derniere_session) VALUES
-- Alice (débutante): aucun statut (tous les AAV sont à 0)

-- Bob (en progression): quelques AAV en cours
(1, 2, 1, 0.85, '[1, 2, 3]', '2026-01-15 10:00:00', '2026-02-20 14:00:00'),  -- Types entiers: presque maîtrisé
(2, 2, 2, 0.60, '[4, 5]', '2026-01-16 11:00:00', '2026-02-19 10:00:00'),     -- Char: en cours
(3, 2, 5, 0.45, '[6, 7]', '2026-01-20 09:00:00', '2026-02-18 16:00:00'),     -- Opérateurs: commencé
(4, 2, 6, 0.30, '[8]', '2026-02-15 14:00:00', '2026-02-15 14:00:00'),        -- Comparaison: début

-- Charlie (expert): beaucoup d'AAV maîtrisés
(5, 3, 1, 1.00, '[9, 10, 11]', '2025-11-05 09:00:00', '2025-11-20 10:00:00'),     -- Types entiers: maîtrisé
(6, 3, 2, 1.00, '[12, 13, 14]', '2025-11-06 10:00:00', '2025-11-21 11:00:00'),   -- Char: maîtrisé
(7, 3, 3, 1.00, '[15, 16, 17]', '2025-11-10 11:00:00', '2025-11-25 14:00:00'),   -- Flottants: maîtrisé
(8, 3, 4, 1.00, '[18, 19, 20]', '2025-11-15 09:00:00', '2025-11-30 16:00:00'),   -- Variables: maîtrisé
(9, 3, 5, 1.00, '[21, 22, 23]', '2025-11-20 10:00:00', '2025-12-05 10:00:00'),   -- Arithmétiques: maîtrisé
(10, 3, 6, 1.00, '[24, 25]', '2025-11-25 11:00:00', '2025-12-10 14:00:00'),      -- Comparaison: maîtrisé
(11, 3, 7, 0.90, '[26, 27]', '2025-12-01 09:00:00', '2026-01-15 10:00:00'),       -- Logiques: presque maîtrisé
(12, 3, 8, 0.75, '[28, 29]', '2025-12-05 10:00:00', '2026-01-20 11:00:00'),       -- If-else: bien avancé
(13, 3, 9, 0.60, '[30, 31]', '2025-12-10 11:00:00', '2026-01-25 14:00:00'),        -- While: en cours
(14, 3, 10, 0.50, '[32]', '2025-12-15 09:00:00', '2026-01-30 10:00:00'),           -- For: commencé
(15, 3, 11, 0.40, '[33]', '2025-12-20 10:00:00', '2026-02-05 11:00:00'),           -- Fonctions: début
(16, 3, 12, 0.30, '[34]', '2025-12-25 11:00:00', '2026-02-10 14:00:00'),           -- Paramètres: début
(17, 3, 13, 0.20, '[]', '2026-01-05 09:00:00', NULL),                               -- Tableaux: non commencé
(18, 3, 14, 0.00, '[]', '2026-01-10 10:00:00', NULL),                               -- Chaînes: non commencé

-- David (bloqué): échecs répétés sur certains AAV
(19, 4, 1, 0.90, '[35, 36, 37]', '2026-01-25 10:00:00', '2026-02-15 14:00:00'),   -- Types entiers: bien
(20, 4, 2, 0.25, '[38, 39, 40, 41]', '2026-01-28 11:00:00', '2026-02-16 16:00:00'), -- Char: échecs répétés
(21, 4, 5, 0.20, '[42, 43, 44]', '2026-02-01 09:00:00', '2026-02-17 10:00:00'),   -- Opérateurs: échecs
(22, 4, 6, 0.10, '[45, 46]', '2026-02-10 14:00:00', '2026-02-18 11:00:00'),       -- Comparaison: échecs

-- Eve (révision): maîtrise ancienne à réviser
(23, 5, 1, 0.95, '[47, 48, 49]', '2025-09-10 10:00:00', '2025-10-01 14:00:00'),   -- Types entiers: maîtrisé depuis longtemps
(24, 5, 2, 0.90, '[50, 51, 52]', '2025-09-15 11:00:00', '2025-10-05 16:00:00'),   -- Char: maîtrisé anciennement
(25, 5, 3, 0.88, '[53, 54, 55]', '2025-09-20 09:00:00', '2025-10-10 10:00:00'),   -- Flottants: maîtrisé anciennement
(26, 5, 4, 0.85, '[56, 57, 58]', '2025-09-25 10:00:00', '2025-10-15 11:00:00'),   -- Variables: maîtrisé anciennement
(27, 5, 5, 0.82, '[59, 60, 61]', '2025-10-01 11:00:00', '2025-10-20 14:00:00');   -- Arithmétiques: maîtrisé anciennement

-- ============================================================
-- 5. TABLE: tentative (GROUPE 3)
-- ============================================================
-- Historique de tentatives pour calculer les statuts

INSERT INTO tentative (id, id_exercice_ou_evenement, id_apprenant, id_aav_cible, score_obtenu, date_tentative, est_valide, temps_resolution_secondes, metadata) VALUES
-- Bob: tentatives pour AAV 1 (Types entiers) - presque maîtrisé
(1, 101, 2, 1, 0.70, '2026-01-15 10:30:00', 1, 120, '{"exercice": "calcul_1"}'),
(2, 102, 2, 1, 0.80, '2026-01-20 14:00:00', 1, 100, '{"exercice": "calcul_2"}'),
(3, 101, 2, 1, 0.85, '2026-02-20 14:00:00', 1, 90, '{"exercice": "calcul_3"}'),

-- Bob: tentatives pour AAV 2 (Char) - en cours
(4, 103, 2, 2, 0.50, '2026-01-16 11:30:00', 1, 150, NULL),
(5, 104, 2, 2, 0.60, '2026-02-19 10:00:00', 1, 120, NULL),

-- Bob: tentatives pour AAV 5 (Opérateurs) - commencé
(6, 109, 2, 5, 0.40, '2026-01-20 09:30:00', 1, 180, NULL),
(7, 110, 2, 5, 0.45, '2026-02-18 16:00:00', 1, 160, NULL),

-- Bob: tentative pour AAV 6 (Comparaison) - début
(8, 111, 2, 6, 0.30, '2026-02-15 14:00:00', 0, 200, NULL),

-- Charlie: tentatives variées (maîtrisés)
(9, 101, 3, 1, 0.80, '2025-11-05 09:30:00', 1, 100, NULL),
(10, 102, 3, 1, 0.90, '2025-11-10 10:00:00', 1, 90, NULL),
(11, 101, 3, 1, 1.00, '2025-11-20 10:00:00', 1, 80, NULL),

-- David: tentatives avec échecs répétés sur AAV 2
(38, 103, 4, 2, 0.20, '2026-01-28 11:30:00', 0, 200, '{"erreur": "confusion_char_int"}'),
(39, 104, 4, 2, 0.15, '2026-02-05 14:00:00', 0, 220, '{"erreur": "confusion_char_int"}'),
(40, 103, 4, 2, 0.30, '2026-02-10 10:00:00', 0, 180, '{"erreur": "guillemets_simples"}'),
(41, 104, 4, 2, 0.25, '2026-02-16 16:00:00', 0, 190, '{"erreur": "guillemets_simples"}'),

-- David: échecs sur opérateurs (problème probable sur types entiers - prérequis)
(42, 109, 4, 5, 0.20, '2026-02-01 09:30:00', 0, 210, '{"erreur": "division_entiere"}'),
(43, 110, 4, 5, 0.25, '2026-02-08 11:00:00', 0, 200, '{"erreur": "modulo_negatif"}'),
(44, 109, 4, 5, 0.15, '2026-02-17 10:00:00', 0, 230, '{"erreur": "division_entiere"}'),

-- David: échecs sur comparaison
(45, 111, 4, 6, 0.10, '2026-02-10 14:30:00', 0, 240, '{"erreur": "operateur_affectation"}'),
(46, 112, 4, 6, 0.10, '2026-02-18 11:00:00', 0, 220, '{"erreur": "confusion_egalite"}');

-- ============================================================
-- 6. TABLE: activite_pedagogique (GROUPE 4)
-- ============================================================

INSERT INTO activite_pedagogique (id_activite, nom, description, type_activite, ids_exercices_inclus, discipline, niveau_difficulte, duree_estimee_minutes, created_by, created_at) VALUES
(1, 'Introduction aux types', 'Première activité: découvrir les types de base en C', 'pilotee', '[101, 102, 103, 104, 105]', 'Programmation', 'debutant', 30, 1, '2026-01-01 10:00:00'),
(2, 'Maîtriser les opérateurs', 'Activité sur les opérateurs arithmétiques et comparaison', 'pilotee', '[109, 110, 111, 112]', 'Programmation', 'intermediaire', 45, 1, '2026-01-05 14:00:00'),
(3, 'Contrôle de flux', 'If-else et boucles', 'prof_definie', '[115, 116, 117, 118, 119, 120]', 'Programmation', 'intermediaire', 60, 1, '2026-01-10 09:00:00'),
(4, 'Fonctions avancées', 'Définition et appel de fonctions', 'revision', '[121, 122, 123, 124]', 'Programmation', 'avance', 40, 1, '2026-01-15 11:00:00');

-- ============================================================
-- 7. TABLE: session_apprenant (GROUPE 4)
-- ============================================================
-- Sessions d'activités en cours ou terminées

INSERT INTO session_apprenant (id_session, id_activite, id_apprenant, date_debut, date_fin, statut, progression_pourcentage) VALUES
(1, 1, 2, '2026-02-20 10:00:00', NULL, 'en_cours', 60.0),  -- Bob en pleine activité
(2, 2, 3, '2026-02-18 14:00:00', '2026-02-18 15:30:00', 'terminee', 100.0),  -- Charlie a terminé
(3, 1, 4, '2026-02-18 09:00:00', NULL, 'en_cours', 30.0),  -- David en difficulté
(4, 3, 5, '2025-10-20 10:00:00', '2025-10-20 11:00:00', 'terminee', 100.0);  -- Eve ancienne session

-- ============================================================
-- 8. TABLE: prompt_fabrication_aav (GROUPE 8)
-- ============================================================

INSERT INTO prompt_fabrication_aav (id_prompt, cible_aav_id, type_exercice_genere, prompt_texte, version_prompt, created_by, date_creation, is_active, metadata) VALUES
(1, 1, 'Calcul Automatisé', 'Génère un exercice de calcul sur les types entiers. Demande à l''élève de prédire le résultat d''opérations avec int, short, long.', 1, 1, '2026-01-01 10:00:00', 1, '{"difficulte": "adaptive"}'),
(2, 2, 'Calcul Automatisé', 'Crée un exercice sur les caractères ASCII. L''élève doit convertir des caractères en codes et vice versa.', 1, 1, '2026-01-01 10:00:00', 1, NULL),
(3, 5, 'Calcul Automatisé', 'Génère des expressions arithmétiques à évaluer. Attention aux pièges de division entière.', 1, 1, '2026-01-02 11:00:00', 1, NULL),
(8, 8, 'Validation par Invention', 'Demande à l''élève d''écrire un programme utilisant if-else pour résoudre un problème donné.', 1, 1, '2026-01-05 14:00:00', 1, NULL),
(11, 11, 'Validation par Invention', 'Demande de créer une fonction avec paramètres et valeur de retour pour résoudre un problème.', 2, 1, '2026-01-10 09:00:00', 1, '{"prerequis_verifies": true}'),
(15, 15, 'Compréhension par Chute', 'Montre un code avec pointeurs contenant une erreur. L''élève doit identifier et corriger le problème.', 1, 1, '2026-01-15 16:00:00', 1, NULL),
(16, 16, 'Validation par Invention', 'Demande d''écrire un programme utilisant malloc et free correctement.', 1, 1, '2026-01-20 10:00:00', 1, NULL);

-- ============================================================
-- 9. TABLE: exercice_instance (GROUPE 8)
-- ============================================================
-- Instances d'exercices générés

INSERT INTO exercice_instance (id_exercice, id_prompt_source, titre, id_aav_cible, type_evaluation, contenu, difficulte, date_generation, nb_utilisations, taux_succes_moyen) VALUES
(101, 1, 'Calcul avec int', 1, 'Calcul Automatisé', '{"question": "Quel est le résultat de sizeof(int) sur un système 32 bits?", "reponse": 4}', 'debutant', '2026-01-01 10:00:00', 15, 0.75),
(102, 1, 'Limites des entiers', 1, 'Calcul Automatisé', '{"question": "Quelle est la valeur de INT_MAX?", "reponse": 2147483647}', 'intermediaire', '2026-01-01 11:00:00', 12, 0.70),
(109, 3, 'Division entière', 5, 'Calcul Automatisé', '{"question": "Quel est le résultat de 5/2 en C?", "reponse": 2}', 'debutant', '2026-01-02 14:00:00', 20, 0.65),
(110, 3, 'Opérateur modulo', 5, 'Calcul Automatisé', '{"question": "Quel est le résultat de 17 % 5?", "reponse": 2}', 'debutant', '2026-01-02 15:00:00', 18, 0.80),
(115, 8, 'Structure if simple', 8, 'Validation par Invention', '{"consigne": "Écrivez un programme qui affiche ''positif'' si x > 0"}', 'debutant', '2026-01-05 14:00:00', 10, 0.85),
(129, 15, 'Pointeur invalide', 15, 'Compréhension par Chute', '{"code": "int* p; *p = 5;", "erreur": "pointeur non initialisé", "correction": "int x; int* p = &x;"}', 'intermediaire', '2026-01-15 16:00:00', 8, 0.40),
(131, 16, 'Allocation simple', 16, 'Validation par Invention', '{"consigne": "Allouez un tableau de 10 int avec malloc"}', 'avance', '2026-01-20 10:00:00', 5, 0.75);

-- ============================================================
-- 10. TABLE: diagnostic_remediation (GROUPE 6)
-- ============================================================
-- Diagnostics d'échec avec causes racines

INSERT INTO diagnostic_remediation (id_diagnostic, id_apprenant, id_aav_source, aav_racines_defaillants, score_obtenu, date_diagnostic, profondeur_analyse, recommandations) VALUES
(1, 4, 5, '[1]', 0.20, '2026-02-17 10:30:00', 2, '{"parcours": [1], "message": "Revoir les types entiers avant les opérateurs"}'),
(2, 4, 6, '[2, 1]', 0.10, '2026-02-18 11:30:00', 3, '{"parcours": [1, 2], "message": "Maîtriser les types puis les caractères avant la comparaison"}'),
(3, 4, 2, '[1]', 0.25, '2026-02-16 16:30:00', 2, '{"parcours": [1], "message": "Revoir les types entiers pour mieux comprendre les caractères"}');

-- ============================================================
-- 11. TABLE: metrique_qualite_aav (GROUPE 7)
-- ============================================================
-- Métriques calculées pour l'analyse de qualité

INSERT INTO metrique_qualite_aav (id_metrique, id_aav, score_covering_ressources, taux_succes_moyen, est_utilisable, nb_tentatives_total, nb_apprenants_distincts, ecart_type_scores, date_calcul, periode_debut, periode_fin) VALUES
(1, 1, 0.90, 0.75, 1, 25, 4, 0.15, '2026-02-21 10:00:00', '2026-01-01', '2026-02-21'),
(2, 2, 0.80, 0.45, 0, 20, 3, 0.25, '2026-02-21 10:00:00', '2026-01-01', '2026-02-21'),  -- AAV problématique
(5, 5, 0.85, 0.55, 1, 30, 4, 0.20, '2026-02-21 10:00:00', '2026-01-01', '2026-02-21'),
(6, 6, 0.70, 0.40, 0, 15, 2, 0.30, '2026-02-21 10:00:00', '2026-01-01', '2026-02-21'),  -- Taux de succès faible
(15, 15, 0.75, 0.40, 0, 8, 1, 0.10, '2026-02-21 10:00:00', '2026-01-01', '2026-02-21'),  -- Pointeurs difficiles
(16, 16, 0.80, 0.75, 1, 5, 1, 0.15, '2026-02-21 10:00:00', '2026-01-01', '2026-02-21');

-- ============================================================
-- FIN DU DUMP
-- ============================================================
-- Résumé des données:
-- - 20 AAV (18 atomiques, 2 composites)
-- - 1 Ontologie
-- - 5 Apprenants (Alice, Bob, Charlie, David, Eve)
-- - 27 Statuts d'apprentissage
-- - 46 Tentatives
-- - 4 Activités pédagogiques
-- - 4 Sessions
-- - 7 Prompts de fabrication
-- - 7 Exercices
-- - 3 Diagnostics de remédiation
-- - 6 Métriques de qualité
-- ============================================================
