import logging
import os
import random

import django

# ANSI color codes for colorful logging output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
BOLD = "\033[1m"
ITALIC = "\033[3m"
RESET = "\033[0m"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "house_rent.settings")
django.setup()

from account.models import User
from interactions.models import RentRequest, Review
from properties.models import Category, House

# Fixed image URLs
HOUSE_IMAGE_URL = "https://i.ibb.co/VWgQBg65/house.jpg"
USER_AVATAR_URL = "https://i.ibb.co/qMWG0D1/user-avatar.png"

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


def create_users():
    logger.info(f"{CYAN}Creating users...{RESET}")
    # Create one admin user
    admin_user, _ = User.objects.get_or_create(
        username="adminuser",
        defaults={
            "email": "admin@example.com",
            "role": "admin",
            "is_active": True,
            "is_email_verified": True,
            "first_name": "Admin",
            "last_name": "User",
            "image": USER_AVATAR_URL,
        },
    )
    admin_user.set_password("password123")
    admin_user.save()
    logger.info(f"{GREEN}{BOLD}Admin user created:{RESET} {admin_user.username}")

    # Create 19 regular users (total 20 including admin)
    first_names = [
        "John",
        "Alice",
        "Bob",
        "Charlie",
        "Diana",
        "Eve",
        "Frank",
        "Grace",
        "Heidi",
        "Ivan",
        "Judy",
        "Kevin",
        "Laura",
        "Mallory",
        "Niaj",
        "Olivia",
        "Peggy",
        "Quentin",
        "Rupert",
    ]
    last_names = [
        "Doe",
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Garcia",
        "Miller",
        "Davis",
        "Rodriguez",
        "Martinez",
        "Hernandez",
        "Lopez",
        "Gonzalez",
        "Wilson",
        "Anderson",
        "Thomas",
        "Taylor",
        "Moore",
    ]
    for i in range(1, 20):
        first_name = first_names[(i - 1) % len(first_names)]
        last_name = last_names[(i - 1) % len(last_names)]
        username = f"{first_name.lower()}_{last_name.lower()}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": f"{username}@example.com",
                "first_name": first_name,
                "last_name": last_name,
                "role": "user",
                "phone": "0123456789",
                "address": "123 Main St, City, Country",
                "is_active": True,
                "is_email_verified": True,
                "image": USER_AVATAR_URL,
            },
        )
        user.set_password("password123")
        user.save()
        if created:
            logger.info(
                f"{GREEN}{BOLD}User created:{RESET} {user.username} ({first_name} {last_name})"
            )
        else:
            logger.info(f"{YELLOW}{ITALIC}User already exists:{RESET} {user.username}")


def create_categories():
    logger.info(f"{CYAN}Creating categories...{RESET}")
    category_names = [
        "Apartment",
        "Villa",
        "Condo",
        "Studio",
        "Cottage",
        "Loft",
        "Townhouse",
        "Bungalow",
        "Penthouse",
        "Duplex",
        "Mansion",
    ]
    for cat in category_names:
        category, created = Category.objects.get_or_create(
            name=cat, defaults={"description": f"{cat} description"}
        )
        if created:
            logger.info(f"{GREEN}{BOLD}Category created:{RESET} {category.name}")
        else:
            logger.info(
                f"{YELLOW}{ITALIC}Category already exists:{RESET} {category.name}"
            )


def create_houses():
    logger.info(f"{CYAN}Creating houses...{RESET}")
    # Get all regular users (non-admin) to serve as potential owners.
    users = list(User.objects.filter(role="user"))
    if not users:
        logger.error(f"{RED}No regular users found. Cannot create houses.{RESET}")
        return
    categories = list(Category.objects.all())

    # Predefined house data with realistic details (we'll override owner and price).
    house_data = [
        {
            "title": "Luxury Apartment in NYC",
            "description": "A spacious, modern apartment in the heart of Manhattan with stunning skyline views.",
            "location": "Manhattan, New York, USA",
        },
        {
            "title": "Beachside Villa in Miami",
            "description": "Enjoy ocean breezes and a private pool in this luxurious Miami villa.",
            "location": "Miami Beach, Florida, USA",
        },
        {
            "title": "Cozy Studio in Downtown LA",
            "description": "A compact, stylish studio perfect for urban living in Los Angeles.",
            "location": "Downtown Los Angeles, California, USA",
        },
        {
            "title": "Modern Condo in San Francisco",
            "description": "A beautifully designed condo with state-of-the-art amenities.",
            "location": "San Francisco, California, USA",
        },
        {
            "title": "Suburban Cottage in Dallas",
            "description": "A charming cottage located in a quiet neighborhood with great schools.",
            "location": "Dallas, Texas, USA",
        },
        {
            "title": "Downtown Loft in Chicago",
            "description": "A trendy loft in the vibrant city center of Chicago.",
            "location": "Chicago, Illinois, USA",
        },
        {
            "title": "Penthouse Suite in New York",
            "description": "An opulent penthouse suite offering unparalleled views of the city.",
            "location": "New York, USA",
        },
        {
            "title": "Country House in Nashville",
            "description": "A peaceful country house surrounded by nature and tranquility.",
            "location": "Nashville, Tennessee, USA",
        },
        {
            "title": "Historic Mansion in Boston",
            "description": "A grand mansion with historic charm and modern comforts.",
            "location": "Boston, Massachusetts, USA",
        },
        {
            "title": "Ski Chalet in Aspen",
            "description": "A cozy ski chalet with easy access to world-class slopes.",
            "location": "Aspen, Colorado, USA",
        },
        {
            "title": "Small Studio in Los Angeles",
            "description": "A budget-friendly studio ideal for singles or couples.",
            "location": "Los Angeles, California, USA",
        },
        {
            "title": "Lakefront Retreat in Minneapolis",
            "description": "A serene retreat with beautiful lake views and modern amenities.",
            "location": "Minneapolis, Minnesota, USA",
        },
        {
            "title": "Eco-Friendly Home in Portland",
            "description": "A sustainable, eco-friendly home with innovative design.",
            "location": "Portland, Oregon, USA",
        },
        {
            "title": "Luxury Townhouse in Washington, DC",
            "description": "A refined townhouse with elegant interiors and a prime location.",
            "location": "Washington, D.C., USA",
        },
        {
            "title": "Bohemian Loft in San Diego",
            "description": "A creatively designed loft that combines modern comfort with artistic flair.",
            "location": "San Diego, California, USA",
        },
        {
            "title": "Modern Villa in Beverly Hills",
            "description": "A sleek, contemporary villa with luxurious finishes in Beverly Hills.",
            "location": "Beverly Hills, California, USA",
        },
        {
            "title": "Urban Penthouse in Chicago",
            "description": "A stylish penthouse offering panoramic city views in Chicago.",
            "location": "Chicago, Illinois, USA",
        },
        {
            "title": "Countryside Farmhouse in Vermont",
            "description": "A charming farmhouse with a rustic feel and plenty of space.",
            "location": "Vermont, USA",
        },
        {
            "title": "Beachfront Bungalow in San Diego",
            "description": "A cozy bungalow steps from the beach, perfect for a summer getaway.",
            "location": "San Diego, California, USA",
        },
        {
            "title": "High-rise Condo in Seattle",
            "description": "A modern condo in a high-rise building in the heart of Seattle.",
            "location": "Seattle, Washington, USA",
        },
        {
            "title": "Cozy Cabin in Aspen",
            "description": "A snug cabin offering a rustic escape in the snowy mountains.",
            "location": "Aspen, Colorado, USA",
        },
        {
            "title": "Spacious Loft in Atlanta",
            "description": "An expansive loft in downtown Atlanta with a modern industrial vibe.",
            "location": "Atlanta, Georgia, USA",
        },
        {
            "title": "Contemporary House in Austin",
            "description": "A sleek, modern house with open-concept design in Austin.",
            "location": "Austin, Texas, USA",
        },
        {
            "title": "Mediterranean Villa in San Diego",
            "description": "A charming villa with Mediterranean style architecture in San Diego.",
            "location": "San Diego, California, USA",
        },
        {
            "title": "Elegant Mansion in Beverly Hills",
            "description": "A grand, elegant mansion with lush gardens and opulent interiors.",
            "location": "Beverly Hills, California, USA",
        },
    ]

    for idx, data in enumerate(house_data, start=1):
        # Override the owner and price with random values
        data["owner"] = random.choice(users)
        data["price"] = round(random.uniform(500, 10000), 2)
        data["images"] = HOUSE_IMAGE_URL

        # First 15 houses will be approved, the rest unapproved.
        approved = True if idx <= 15 else False

        house, created = House.objects.get_or_create(
            title=data["title"],
            defaults={
                "owner": data["owner"],
                "description": data["description"],
                "location": data["location"],
                "price": data["price"],
                "images": data["images"],
                "approved": approved,
            },
        )
        # Assign 1 to 3 random categories
        available_categories = list(categories)
        num_cats = random.randint(1, min(3, len(available_categories)))
        chosen_categories = random.sample(available_categories, num_cats)
        house.categories.set(chosen_categories)
        house.save()

        if created:
            status_str = "approved" if approved else "unapproved"
            logger.info(
                f"{GREEN}{BOLD}House created:{RESET} {house.title} (Owner: {house.owner.username}, Price: ${house.price}, Status: {status_str})"
            )
        else:
            logger.info(f"{YELLOW}{ITALIC}House already exists:{RESET} {house.title}")


def create_reviews():
    logger.info(f"{CYAN}Creating reviews...{RESET}")
    review_texts = [
        "Absolutely loved staying here. The location was perfect and the amenities exceeded my expectations.",
        "The property was clean and well-maintained. The host was friendly and responsive.",
        "A wonderful experience. The neighborhood is vibrant, and the house has all the modern conveniences.",
    ]
    houses = House.objects.all()
    users = list(User.objects.filter(role="user"))
    for house in houses:
        num_reviews = random.randint(1, 3)
        for j in range(num_reviews):
            possible_reviewers = [u for u in users if u != house.owner]
            reviewer = (
                random.choice(possible_reviewers) if possible_reviewers else house.owner
            )
            comment = random.choice(review_texts)
            if not house.reviews.filter(reviewer=reviewer).exists():
                Review.objects.create(
                    house=house,
                    reviewer=reviewer,
                    rating=random.randint(1, 5),
                    comment=comment,
                )
                logger.info(
                    f"{GREEN}{BOLD}Review created for{RESET} {house.title} by {reviewer.username}"
                )


def create_rent_requests():
    logger.info(f"{CYAN}Creating rent requests...{RESET}")
    houses = list(House.objects.all())
    users = list(User.objects.filter(role="user"))
    for house in houses:
        possible_requesters = [u for u in users if u != house.owner]
        if possible_requesters and not house.rent_requests.exists():
            requester = random.choice(possible_requesters)
            RentRequest.objects.get_or_create(
                house=house,
                tenant=requester,
                defaults={
                    "status": "pending",
                    "message": f"I would like to rent {house.title} for one month.",
                    "duration": 30,
                },
            )
            logger.info(
                f"{GREEN}{BOLD}Rent request created for{RESET} {house.title} by {requester.username}"
            )


if __name__ == "__main__":
    logger.info(f"{MAGENTA}{BOLD}Starting database population...{RESET}")
    create_users()
    create_categories()
    create_houses()
    create_reviews()
    create_rent_requests()
    logger.info(f"{MAGENTA}{BOLD}Dummy data populated successfully!{RESET}")
