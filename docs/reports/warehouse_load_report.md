# TechStore - Warehouse Load Report

## Statut

**STEP 5 STATUS: PASS**

Le serveur PostgreSQL Windows est installé, le service `postgresql-x64-18` est démarré et le chargement réel a été exécuté dans la base `postgres` sur `localhost:5432` avec l'utilisateur `postgres`.

Le mot de passe a été saisi uniquement dans le terminal interactif. Il n'a pas été écrit dans le projet, l'audit ou ce rapport.

## Processus exécuté

Le chargeur [load_datawarehouse.py](../../src/warehouse/load_datawarehouse.py) :

1. exécute les DDL DW existants dans l'ordre;
2. utilise `TRUNCATE ... RESTART IDENTITY CASCADE` pour une réexécution déterministe;
3. charge les dimensions avant les facts;
4. récupère les surrogate keys depuis les dimensions;
5. transforme les business keys Gold en FK techniques;
6. charge les CSV avec PostgreSQL `COPY` par flux de blocs;
7. exécute les contrôles de [05_quality_checks.sql](../../sql/warehouse/05_quality_checks.sql) dans la transaction;
8. valide avant commit et écrit un audit JSON.

La stratégie `truncate/reload` est adaptée à ce projet de portfolio : elle est simple, idempotente et évite les doublons lors d'une nouvelle exécution. Une stratégie incrémentale ou SCD pourra être ajoutée lorsque le besoin d'historisation sera réel.

## Volumes Gold -> DW vérifiés

| Table DW            |    Gold |      DW | Statut |
| ------------------- | ------: | ------: | ------ |
| `dw_dim_customer`   |  24 999 |  24 999 | PASS   |
| `dw_dim_product`    |     600 |     600 | PASS   |
| `dw_dim_supplier`   |      60 |      60 | PASS   |
| `dw_dim_employee`   |     350 |     350 | PASS   |
| `dw_dim_store`      |      31 |      31 | PASS   |
| `dw_dim_warehouse`  |      31 |      31 | PASS   |
| `dw_dim_date`       |   1 854 |   1 854 | PASS   |
| `dw_fact_sales`     | 320 000 | 320 000 | PASS   |
| `dw_fact_returns`   |  16 192 |  16 192 | PASS   |
| `dw_fact_payments`  | 320 000 | 320 000 | PASS   |
| `dw_fact_inventory` | 320 000 | 320 000 | PASS   |

Les 11 tables DW sont présentes dans le schéma `dw`.

## Contrôles de validation

- PK uniques et non nulles : **PASS** sur les 11 tables.
- FK valides : **PASS**, 0 ligne orpheline sur les 15 relations vérifiées.
- Surrogate keys : **PASS**, distinctes et non nulles; les dimensions utilisent leurs clés techniques, et `dim_date` conserve `date_key`.
- Conservation des volumes Gold -> DW : **PASS**.
- Contrôles de [05_quality_checks.sql](../../sql/warehouse/05_quality_checks.sql) : **PASS** pour les 6 contrôles.
- Cohérence des montants, retours, paiements et inventaire : **PASS**.

## Audit

L'exécution réelle du script a généré [warehouse_load_audit.json](../../data/gold/warehouse_load_audit.json) avec :

- statut : `PASS`;
- 11 tables chargées;
- volumes source/destination identiques;
- validation PK/FK et surrogate keys réussie;
- contrôles SQL exécutés avec statut `PASS`.

## Réexécution

```powershell
python src/warehouse/load_datawarehouse.py
```

Le chargeur utilise `TRUNCATE / RESTART IDENTITY / CASCADE` dans une transaction : une nouvelle exécution recharge proprement les 11 tables sans doublons. Le mot de passe doit rester fourni par le terminal ou l'environnement de session, jamais par un fichier du projet.
