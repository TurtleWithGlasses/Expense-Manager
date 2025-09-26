"""
Migration script to move data from SQLite to PostgreSQL cloud database
"""
import os
import sys
from datetime import date
from config import config
from db import Database
from cloud_db import CloudDatabase

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    print("🔄 Starting data migration from SQLite to PostgreSQL...")
    
    # Check if cloud database is configured
    cloud_config = config.get("cloud_database", {})
    if not all([cloud_config.get("host"), cloud_config.get("database"), 
               cloud_config.get("user"), cloud_config.get("password")]):
        print("❌ Cloud database not configured. Please configure it first.")
        return False
    
    try:
        # Connect to both databases
        print("📡 Connecting to databases...")
        local_db = Database()
        cloud_db = CloudDatabase(
            db_type="postgresql",
            host=cloud_config["host"],
            port=cloud_config.get("port", 5432),
            database=cloud_config["database"],
            user=cloud_config["user"],
            password=cloud_config["password"]
        )
        
        # Migrate categories
        print("📂 Migrating categories...")
        categories = local_db.all_categories()
        for cat_id, cat_name in categories:
            try:
                cloud_db.add_category(cat_name)
                print(f"  ✅ {cat_name}")
            except ValueError:
                print(f"  ⚠️  {cat_name} (already exists)")
        
        # Migrate expenses
        print("💰 Migrating expenses...")
        expenses = local_db.expenses_in_range(date(2000, 1, 1), date.today())
        for exp_id, exp_date, exp_amount, exp_category, exp_note in expenses:
            # Get category ID from cloud database
            cloud_categories = cloud_db.all_categories()
            cat_id = None
            for cid, cname in cloud_categories:
                if cname == exp_category:
                    cat_id = cid
                    break
            
            if cat_id:
                cloud_db.add_expense(exp_date, exp_amount, cat_id, exp_note)
                print(f"  ✅ {exp_date} - {exp_category} - ${exp_amount}")
            else:
                print(f"  ❌ Category not found: {exp_category}")
        
        # Migrate incomes
        print("💵 Migrating incomes...")
        incomes = local_db.incomes_in_range(date(2000, 1, 1), date.today())
        for inc_id, inc_date, inc_amount, inc_source in incomes:
            cloud_db.add_income(inc_date, inc_amount, inc_source)
            print(f"  ✅ {inc_date} - {inc_source} - ${inc_amount}")
        
        # Migrate budgets
        print("📊 Migrating budgets...")
        budgets = local_db.get_budgets()
        for budget_id, budget_category, budget_amount, budget_period in budgets:
            cloud_db.add_budget(budget_category, budget_amount, budget_period)
            print(f"  ✅ {budget_category} - ${budget_amount} ({budget_period})")
        
        print("\n🎉 Migration completed successfully!")
        print("📝 Your data is now stored in the cloud database.")
        print("💡 You can now switch to cloud database in the settings.")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    finally:
        # Close connections
        if 'local_db' in locals():
            local_db.close()
        if 'cloud_db' in locals():
            cloud_db.close()

def main():
    """Main migration function"""
    print("🚀 Expense Manager - Cloud Migration Tool")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Please run this script from the Expense Manager directory")
        sys.exit(1)
    
    # Confirm migration
    print("\n⚠️  This will migrate your local data to the cloud database.")
    print("📋 Make sure you have:")
    print("   1. Configured cloud database settings")
    print("   2. Backed up your local database")
    print("   3. Stable internet connection")
    
    response = input("\n🤔 Do you want to continue? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Migration cancelled.")
        sys.exit(0)
    
    # Run migration
    success = migrate_data()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("🔄 Please restart the application to use the cloud database.")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
