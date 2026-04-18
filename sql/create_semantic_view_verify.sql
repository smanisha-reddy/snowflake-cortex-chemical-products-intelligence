CALL SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML(
  'CHEM_DB.CURATED',
  $$
name: chemical_products_semantic
description: >
  Semantic view for chemical product data. Provides dimensions for product attributes,
  company and brand information, chemical identifiers, and category classification.
  Includes time dimensions for product lifecycle tracking and measures for
  chemical and product counting.

tables:
  - name: CHEMICAL_PRODUCTS
    description: >
      Curated chemical product records including product names, company and brand
      associations, chemical identifiers (CAS numbers), and category classifications.
      Tracks product lifecycle dates from initial listing through discontinuation.
    base_table:
      database: CHEM_DB
      schema: CURATED
      table: CHEMICAL_PRODUCTS
    primary_key:
      columns:
        - CDPHID

    dimensions:
      - name: CDPHID
        synonyms:
          - "product ID"
          - "chemical product ID"
          - "product key"
        description: Unique identifier for each chemical product record.
        data_type: TEXT
        expr: CDPHID

      - name: PRODUCTNAME
        synonyms:
          - "product name"
          - "product"
          - "product title"
        description: The commercial name of the chemical product.
        data_type: TEXT
        expr: PRODUCTNAME

      - name: COMPANYNAME
        synonyms:
          - "company"
          - "company name"
          - "manufacturer"
          - "vendor"
        description: The name of the company that manufactures or distributes the product.
        data_type: TEXT
        expr: COMPANYNAME

      - name: BRANDNAME
        synonyms:
          - "brand"
          - "brand name"
          - "product line"
        description: The brand name under which the product is marketed.
        data_type: TEXT
        expr: BRANDNAME

      - name: PRIMARYCATEGORY
        synonyms:
          - "primary category"
          - "main category"
          - "category"
        description: The top-level classification category of the chemical product.
        data_type: TEXT
        expr: PRIMARYCATEGORY

      - name: SUBCATEGORY
        synonyms:
          - "subcategory"
          - "sub-category"
          - "secondary category"
        description: The secondary classification category providing finer product grouping.
        data_type: TEXT
        expr: SUBCATEGORY

      - name: CASNUMBER
        synonyms:
          - "CAS number"
          - "CAS"
          - "CAS registry number"
          - "chemical abstract number"
        description: The Chemical Abstracts Service registry number identifying the chemical substance.
        data_type: TEXT
        expr: CASNUMBER

      - name: CHEMICALNAME
        synonyms:
          - "chemical name"
          - "chemical"
          - "substance name"
          - "chemical substance"
        description: The scientific or common name of the chemical substance in the product.
        data_type: TEXT
        expr: CHEMICALNAME

    time_dimensions:
      - name: INITIAL_DATE
        synonyms:
          - "initial date"
          - "first listed date"
          - "introduction date"
          - "start date"
        description: The date the chemical product was first listed or introduced.
        data_type: DATE
        expr: INITIAL_DATE

      - name: RECENT_DATE
        synonyms:
          - "recent date"
          - "last updated date"
          - "most recent date"
          - "latest date"
        description: The most recent date the chemical product record was updated or confirmed active.
        data_type: DATE
        expr: RECENT_DATE

      - name: DISCONTINUED_DATE
        synonyms:
          - "discontinued date"
          - "end date"
          - "removal date"
          - "discontinuation date"
        description: The date the chemical product was discontinued or removed from the market.
        data_type: DATE
        expr: DISCONTINUED_DATE

    metrics:
      - name: TOTAL_CHEMICAL_COUNT
        synonyms:
          - "total chemicals"
          - "chemical count"
          - "number of chemicals"
        description: Total count of chemical product records.
        expr: COUNT(CDPHID)

      - name: DISTINCT_PRODUCT_COUNT
        synonyms:
          - "distinct products"
          - "unique products"
          - "product count"
          - "number of products"
        description: Count of distinct chemical products by product name.
        expr: COUNT(DISTINCT PRODUCTNAME)

verified_queries:
  - name: top_companies_by_product_count
    question: Which companies have the most chemical products?
    sql: |
      SELECT
        COMPANYNAME,
        COUNT(CDPHID) AS TOTAL_PRODUCTS
      FROM CHEM_DB.CURATED.CHEMICAL_PRODUCTS
      GROUP BY COMPANYNAME
      ORDER BY TOTAL_PRODUCTS DESC
      LIMIT 10

  - name: top_categories_by_product_count
    question: What are the top primary categories by number of products?
    sql: |
      SELECT
        PRIMARYCATEGORY,
        COUNT(CDPHID) AS TOTAL_PRODUCTS
      FROM CHEM_DB.CURATED.CHEMICAL_PRODUCTS
      GROUP BY PRIMARYCATEGORY
      ORDER BY TOTAL_PRODUCTS DESC
      LIMIT 10

  - name: products_by_chemical
    question: Which products contain a specific chemical?
    sql: |
      SELECT
        CHEMICALNAME,
        PRODUCTNAME,
        COMPANYNAME,
        BRANDNAME,
        PRIMARYCATEGORY
      FROM CHEM_DB.CURATED.CHEMICAL_PRODUCTS
      WHERE CHEMICALNAME IS NOT NULL
      ORDER BY CHEMICALNAME, PRODUCTNAME

  - name: discontinued_products_by_year
    question: How many products were discontinued each year?
    sql: |
      SELECT
        YEAR(DISCONTINUED_DATE) AS DISCONTINUED_YEAR,
        COUNT(CDPHID) AS DISCONTINUED_COUNT
      FROM CHEM_DB.CURATED.CHEMICAL_PRODUCTS
      WHERE DISCONTINUED_DATE IS NOT NULL
      GROUP BY YEAR(DISCONTINUED_DATE)
      ORDER BY DISCONTINUED_YEAR DESC
  $$,
  TRUE
);
