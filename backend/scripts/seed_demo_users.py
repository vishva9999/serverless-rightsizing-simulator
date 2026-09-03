"""
Development Seed Utility — Demo Users & Organization Initializer.

Populates development-only demo accounts for local testing:
  - Admin:   admin@example.com   / AdminPass123!
  - Analyst: analyst@example.com / AnalystPass123!
  - Viewer:  viewer@example.com  / ViewerPass123!

Usage:
  py scripts/seed_demo_users.py
"""

import sys
import os

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import init_db
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


def seed_demo():
    print("=" * 60)
    print("  Serverless Rightsizing Simulator -- Seed Demo Accounts")
    print("=" * 60)

    init_db()

    # 1. Create or get Demo Organization
    org_name = "Demo Enterprise"
    org = OrganizationRepository.get_by_name(org_name)
    if not org:
        org = OrganizationRepository.create(org_name, "Development demo organization workspace")
        print(f"Created organization: {org_name} (ID: {org['id']})")
    else:
        print(f"Using existing organization: {org_name} (ID: {org['id']})")

    demo_users = [
        ("admin@example.com", "AdminPass123!", "Alice Admin", "admin"),
        ("analyst@example.com", "AnalystPass123!", "Bob Analyst", "analyst"),
        ("viewer@example.com", "ViewerPass123!", "Charlie Viewer", "viewer"),
    ]

    for email, password, full_name, role in demo_users:
        existing = UserRepository.get_by_email(email)
        if not existing:
            pwd_hash = AuthService.hash_password(password)
            user = UserRepository.create(
                email=email,
                password_hash=pwd_hash,
                full_name=full_name,
                organization_id=org["id"],
                role=role,
                is_active=True
            )
            print(f"  [OK] Created demo user: {email} | Role: {role}")
        else:
            print(f"  [INFO] Demo user already exists: {email}")

    print("\n" + "=" * 60)
    print("  Demo Seed Credentials (DEVELOPMENT ONLY):")
    print("  1. Admin:   admin@example.com   / AdminPass123!")
    print("  2. Analyst: analyst@example.com / AnalystPass123!")
    print("  3. Viewer:  viewer@example.com  / ViewerPass123!")
    print("=" * 60)


if __name__ == "__main__":
    seed_demo()
