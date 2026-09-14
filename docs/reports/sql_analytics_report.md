# TechStore - SQL Analytics Report

## 1. Objectif et architecture

La couche SQL Analytics consomme exclusivement le schéma PostgreSQL `dw`. Elle ne modifie ni RAW, Silver, Gold ni les tables DW. Elle fournit :

```text
PostgreSQL dw -> schema analytics views -> SQL analysis scripts -> Power BI
```

Le schéma `analytics` contient uniquement des vues agrégées réutilisables. Les scripts `01` à `09` exposent les analyses détaillées par domaine; `99_quality_checks.sql` vérifie les résultats analytiques.

## 2. Vues créées

| Vue                                 | Grain                             | Usage                                                |
| ----------------------------------- | --------------------------------- | ---------------------------------------------------- |
| `analytics.vw_sales_kpis`           | une ligne globale                 | cartes KPI exécutives                                |
| `analytics.vw_monthly_sales`        | une ligne par année/mois de vente | tendance, MoM et croissance                          |
| `analytics.vw_product_performance`  | un produit                        | classement et performance produit                    |
| `analytics.vw_customer_performance` | un client                         | valeur client et segmentation                        |
| `analytics.vw_store_performance`    | un magasin                        | classement magasins                                  |
| `analytics.vw_returns_analysis`     | un retour                         | exploration produit, magasin, client, date et raison |

## 3. Fichiers créés

- `00_create_views.sql` : schéma `analytics` et six vues.
- `01_sales_kpis.sql` : KPIs commerciaux globaux.
- `02_sales_trends.sql` : année, trimestre, mois, MoM et YoY.
- `03_product_analysis.sql` : top produits, marge, quantité, catégorie et marque.
- `04_customer_analysis.sql` : clients, commandes, panier moyen, retours et segmentation.
- `05_store_employee_analysis.sql` : magasins, employés et classements.
- `06_returns_analysis.sql` : taux, produits, magasins, clients, mois et motifs.
- `07_inventory_analysis.sql` : stock observé, risques et entrepôts.
- `08_payment_analysis.sql` : montants, méthodes, statuts et rapprochement.
- `09_business_kpis.sql` : KPIs exécutifs, canal, statut et livraison.
- `99_quality_checks.sql` : contrôles de cohérence de la couche analytique.

## 4. Définitions des KPI

- **Total Revenue** : `SUM(gross_amount)` au grain vente.
- **Net Revenue** : `SUM(net_amount)` après remise.
- **Total Cost** : `SUM(total_cost)`.
- **Gross Margin** : `SUM(margin_amount)`.
- **Gross Margin %** : `SUM(margin_amount) / SUM(net_amount)`, protégé par `NULLIF`.
- **Total Quantity Sold** : `SUM(quantity)`.
- **Number of Sales** : `COUNT(*)` dans `dw_fact_sales`.
- **Average Order Value** : `SUM(net_amount) / COUNT(*)`.
- **Average Unit Price** : `AVG(unit_price)`.
- **Average Discount** : `AVG(discount_pct)`.
- **Number of Customers** : `COUNT(DISTINCT customer_key)`.
- **Number of Products Sold** : `COUNT(DISTINCT product_key)`.
- **Number of Returned Sales** : `COUNT(*) FILTER (WHERE is_returned)`.
- **Return Rate** : ventes retournées / ventes totales.

Les montants déjà fiables dans les faits ne sont pas recalculés à partir des dimensions. Les jointures de date utilisent `dw_dim_date`.

## 5. Logique analytique importante

- Les tendances utilisent `sale_date_key` pour les ventes et `return_date_key` pour les retours.
- Les évolutions MoM et YoY utilisent `LAG` sur des périodes triées.
- Les agrégations produit, client et magasin partent des facts puis rejoignent les dimensions descriptives.
- La segmentation client est une segmentation SQL déterministe basée sur le revenu cumulé : `High Value` >= 10 000, `Medium Value` >= 3 000, sinon `Low Value`.
- L'inventaire respecte son grain réel : un événement par vente, produit et entrepôt. Il ne prétend pas représenter un snapshot quotidien.
- Les paiements sont rapprochés avec `net_amount` à la tolérance monétaire de 0,011.

## 6. Contrôles qualité

`99_quality_checks.sql` vérifie :

- présence des six vues;
- KPIs non négatifs;
- absence de division par zéro dans les KPI principaux;
- réconciliation marge = revenu net - coût;
- unicité des grains mensuel, produit, client et magasin;
- cohérence des dates mensuelles;
- cohérence des agrégations mensuelles avec `dw_fact_sales`;
- rapprochement paiements/ventes;
- cohérence quantité et stock inventaire.

Résultat d'exécution PostgreSQL : **12/12 contrôles PASS**.

## 7. KPI observés

Les KPI globaux retournés par `analytics.vw_sales_kpis` sont :

| KPI                      |         Valeur |
| ------------------------ | -------------: |
| Total Revenue            | 422 095 306,10 |
| Net Revenue              | 400 147 824,80 |
| Total Cost               | 284 682 045,70 |
| Gross Margin             | 115 465 779,10 |
| Gross Margin %           |      28,8558 % |
| Total Quantity Sold      |        540 337 |
| Number of Sales          |        320 000 |
| Average Order Value      |       1 250,46 |
| Average Unit Price       |         780,17 |
| Average Discount         |      5,20095 % |
| Number of Customers      |         24 999 |
| Number of Products Sold  |            600 |
| Number of Returned Sales |         16 192 |
| Return Rate              |         5,06 % |

## 8. Corrections effectuées

L'exécution initiale a révélé deux classements qui référençaient une colonne calculée non exposée par les vues (`return_rate`). Les scripts `03_product_analysis.sql` et `04_customer_analysis.sql` ont été corrigés pour calculer explicitement le taux à partir des colonnes disponibles. Les neuf scripts ont ensuite été rejoués avec succès.

## 9. Exécution PostgreSQL

Les scripts ont été exécutés sur PostgreSQL local dans la base `postgres`, avec les données DW réellement chargées. Les six vues ont été créées et les contrôles de `99_quality_checks.sql` ont retourné `PASS`.

Aucun mot de passe PostgreSQL n'est stocké dans ce projet.

## 10. Utilisation prévue dans Power BI

Power BI pourra se connecter aux vues `analytics.vw_sales_kpis`, `analytics.vw_monthly_sales`, `analytics.vw_product_performance`, `analytics.vw_customer_performance`, `analytics.vw_store_performance` et `analytics.vw_returns_analysis`. Les scripts détaillés restent disponibles pour les explorations SQL et la validation des indicateurs avant construction des dashboards.
