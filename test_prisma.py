#!/usr/bin/env python3
from prisma import Prisma

print("Initializing Prisma client...")
prisma = Prisma()

print("Connecting to database...")
prisma.connect()

try:
    # Try a simple query
    print("Testing a query...")
    count = prisma.contact.count()
    print(f"Contact count: {count}")
    
    print("✅ Successfully connected to the database!")
finally:
    prisma.disconnect() 