#!/usr/bin/env python3
"""
Script pour afficher la structure de la base de données ApplyFlow
"""
import sys
sys.path.insert(0, '/mnt/c/projets/ApplyFlow/backend')

from app.database import engine
from sqlalchemy import inspect

print("=" * 60)
print("  📊 STRUCTURE BASE DE DONNÉES APPLYFLOW")
print("=" * 60)
print()

inspector = inspect(engine)

# Liste des tables
tables = inspector.get_table_names()
print(f"🗃️  {len(tables)} tables trouvées:")
for table in tables:
    print(f"  • {table}")

print()
print("=" * 60)
print("  📋 DÉTAIL DES COLONNES PAR TABLE")
print("=" * 60)

for table_name in sorted(tables):
    print(f"\n📌 Table: {table_name}")
    print("-" * 60)
    
    columns = inspector.get_columns(table_name)
    
    print(f"{'Colonne':<30} {'Type':<20} {'Nullable':<10}")
    print("-" * 60)
    
    for col in columns:
        col_name = col['name']
        col_type = str(col['type'])
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        print(f"{col_name:<30} {col_type:<20} {nullable:<10}")
    
    # Foreign keys
    fks = inspector.get_foreign_keys(table_name)
    if fks:
        print(f"\n🔗 Foreign Keys:")
        for fk in fks:
            print(f"   {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")

print()
print("=" * 60)
print("✅ Analyse terminée!")
