class Command(BaseCommand):
    help = "Populates the database with initial realistic data."

    def handle(self, *args, **options):
        self.stdout.write("Populating database with realistic data...")
        admin_user = self.create_admin()
        users = self.create_users()
        categories = self.create_categories()
        houses = self.create_houses(users, categories)
        self.create_advertisements(houses)
        self.create_reviews(houses, users)
        self.stdout.write(self.style.SUCCESS("Database populated successfully!"))

    def create_admin(self):
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "first_name": "Admin",
                "last_name": "User",
                "email": "admin@example.com",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("adminpassword")
            admin.save()
        return admin

    def create_users(self):
        users_data = [
            {
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "johndoe@example.com",
                "address": "New York, USA",
                "mobile_number": "1234567890",
            },
            {
                "first_name": "Jane",
                "last_name": "Smith",
                "username": "janesmith",
                "email": "janesmith@example.com",
                "address": "Los Angeles, USA",
                "mobile_number": "1234567891",
            },
            {
                "first_name": "Alice",
                "last_name": "Johnson",
                "username": "alicej",
                "email": "alice@example.com",
                "address": "Chicago, USA",
                "mobile_number": "1234567892",
            },
            {
                "first_name": "Bob",
                "last_name": "Brown",
                "username": "bobbrown",
                "email": "bob@example.com",
                "address": "Houston, USA",
                "mobile_number": "1234567893",
            },
            {
                "first_name": "Emma",
                "last_name": "Wilson",
                "username": "emmaw",
                "email": "emma@example.com",
                "address": "San Francisco, USA",
                "mobile_number": "1234567894",
            },
            {
                "first_name": "Michael",
                "last_name": "Davis",
                "username": "michael",
                "email": "michael@example.com",
                "address": "Miami, USA",
                "mobile_number": "1234567895",
            },
            {
                "first_name": "Sarah",
                "last_name": "Miller",
                "username": "sarahm",
                "email": "sarah@example.com",
                "address": "Seattle, USA",
                "mobile_number": "1234567896",
            },
            {
                "first_name": "David",
                "last_name": "Moore",
                "username": "davidm",
                "email": "david@example.com",
                "address": "Boston, USA",
                "mobile_number": "1234567897",
            },
            {
                "first_name": "William",
                "last_name": "Taylor",
                "username": "williamt",
                "email": "william@example.com",
                "address": "Austin, USA",
                "mobile_number": "1234567898",
            },
            {
                "first_name": "Olivia",
                "last_name": "Anderson",
                "username": "oliviaa",
                "email": "olivia@example.com",
                "address": "San Diego, USA",
                "mobile_number": "1234567899",
            },
            {
                "first_name": "James",
                "last_name": "Thomas",
                "username": "jamest",
                "email": "james@example.com",
                "address": "Philadelphia, USA",
                "mobile_number": "1234567800",
            },
            {
                "first_name": "Isabella",
                "last_name": "Jackson",
                "username": "isabellaj",
                "email": "isabella@example.com",
                "address": "Phoenix, USA",
                "mobile_number": "1234567801",
            },
            {
                "first_name": "Benjamin",
                "last_name": "White",
                "username": "benjaminw",
                "email": "benjamin@example.com",
                "address": "San Antonio, USA",
                "mobile_number": "1234567802",
            },
            {
                "first_name": "Mia",
                "last_name": "Harris",
                "username": "miah",
                "email": "mia@example.com",
                "address": "San Jose, USA",
                "mobile_number": "1234567803",
            },
            {
                "first_name": "Lucas",
                "last_name": "Martin",
                "username": "lucasm",
                "email": "lucas@example.com",
                "address": "Fort Worth, USA",
                "mobile_number": "1234567804",
            },
            {
                "first_name": "Charlotte",
                "last_name": "Thompson",
                "username": "charlottet",
                "email": "charlotte@example.com",
                "address": "Columbus, USA",
                "mobile_number": "1234567805",
            },
            {
                "first_name": "Henry",
                "last_name": "Garcia",
                "username": "henryg",
                "email": "henry@example.com",
                "address": "San Francisco, USA",
                "mobile_number": "1234567806",
            },
            {
                "first_name": "Amelia",
                "last_name": "Martinez",
                "username": "ameliam",
                "email": "amelia@example.com",
                "address": "Jacksonville, USA",
                "mobile_number": "1234567807",
            },
            {
                "first_name": "Alexander",
                "last_name": "Robinson",
                "username": "alexanderr",
                "email": "alexander@example.com",
                "address": "Indianapolis, USA",
                "mobile_number": "1234567808",
            },
            {
                "first_name": "Evelyn",
                "last_name": "Clark",
                "username": "evelync",
                "email": "evelyn@example.com",
                "address": "San Francisco, USA",
                "mobile_number": "1234567809",
            },
        ]
        created_users = []
        for data in users_data:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "email": data["email"],
                },
            )
            if created:
                user.set_password("password123")
                user.save()
            user_account, _ = UserAccount.objects.get_or_create(
                user=user,
                defaults={
                    "address": data["address"],
                    "mobile_number": data["mobile_number"],
                    "image": "https://i.ibb.co.com/qMWG0D1j/user-avatar.png",
                    "is_verified": True,
                },
            )
            created_users.append(user_account)
        return created_users

    def create_categories(self):
        # Additional categories added.
        categories = [
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
        created_categories = []
        for category in categories:
            cat, _ = Category.objects.get_or_create(
                name=category, slug=slugify(category)
            )
            created_categories.append(cat)
        return created_categories

    def create_houses(self, users, categories):

        house_data = [
            {
                "title": "Luxury Apartment in NYC",
                "description": "A spacious, modern apartment in the heart of Manhattan with stunning skyline views.",
                "location": "Manhattan, New York, USA",
                "price": 2500.00,
                "owner": users[0],
            },
            {
                "title": "Beachside Villa in Miami",
                "description": "Enjoy ocean breezes and a private pool in this luxurious Miami villa.",
                "location": "Miami Beach, Florida, USA",
                "price": 5000.00,
                "owner": users[1],
            },
            {
                "title": "Cozy Studio in Downtown LA",
                "description": "A compact, stylish studio perfect for urban living in Los Angeles.",
                "location": "Downtown Los Angeles, California, USA",
                "price": 1500.00,
                "owner": users[2],
            },
            {
                "title": "Modern Condo in San Francisco",
                "description": "A beautifully designed condo with state-of-the-art amenities.",
                "location": "San Francisco, California, USA",
                "price": 3500.00,
                "owner": users[3],
            },
            {
                "title": "Suburban Cottage in Dallas",
                "description": "A charming cottage located in a quiet neighborhood with great schools.",
                "location": "Dallas, Texas, USA",
                "price": 2000.00,
                "owner": users[4],
            },
            {
                "title": "Downtown Loft in Chicago",
                "description": "A trendy loft in the vibrant city center of Chicago.",
                "location": "Chicago, Illinois, USA",
                "price": 3000.00,
                "owner": users[5],
            },
            {
                "title": "Penthouse Suite in New York",
                "description": "An opulent penthouse suite offering unparalleled views of the city.",
                "location": "New York, USA",
                "price": 8000.00,
                "owner": users[6],
            },
            {
                "title": "Country House in Nashville",
                "description": "A peaceful country house surrounded by nature and tranquility.",
                "location": "Nashville, Tennessee, USA",
                "price": 1800.00,
                "owner": users[7],
            },
            {
                "title": "Historic Mansion in Boston",
                "description": "A grand mansion with historic charm and modern comforts.",
                "location": "Boston, Massachusetts, USA",
                "price": 3200.00,
                "owner": users[8],
            },
            {
                "title": "Ski Chalet in Aspen",
                "description": "A cozy ski chalet with easy access to world-class slopes.",
                "location": "Aspen, Colorado, USA",
                "price": 2500.00,
                "owner": users[9],
            },
            {
                "title": "Small Studio in Los Angeles",
                "description": "A budget-friendly studio ideal for singles or couples.",
                "location": "Los Angeles, California, USA",
                "price": 1200.00,
                "owner": users[10],
            },
            {
                "title": "Lakefront Retreat in Minneapolis",
                "description": "A serene retreat with beautiful lake views and modern amenities.",
                "location": "Minneapolis, Minnesota, USA",
                "price": 2700.00,
                "owner": users[11],
            },
            {
                "title": "Eco-Friendly Home in Portland",
                "description": "A sustainable, eco-friendly home with innovative design.",
                "location": "Portland, Oregon, USA",
                "price": 2300.00,
                "owner": users[12],
            },
            {
                "title": "Luxury Townhouse in Washington, DC",
                "description": "A refined townhouse with elegant interiors and a prime location.",
                "location": "Washington, D.C., USA",
                "price": 4000.00,
                "owner": users[13],
            },
            {
                "title": "Bohemian Loft in San Diego",
                "description": "A creatively designed loft that combines modern comfort with artistic flair.",
                "location": "San Diego, California, USA",
                "price": 3100.00,
                "owner": users[14],
            },
        ]

        created_houses = []
        # Use the provided image for all houses
        house_image = (
            "https://i.ibb.co.com/0ySYJj5N/todd-kent-178j8t-Jr-Nlc-unsplash.jpg"
        )
        for data in house_data:
            data["image"] = house_image
            house = House.objects.create(**data)
            # Randomly assign 2 or 3 categories from the provided categories list
            num_categories = random.choice([2, 3])
            house_categories = random.sample(categories, num_categories)
            house.category.set(house_categories)
            created_houses.append(house)
        return created_houses

    def create_advertisements(self, houses):
        for house in houses:
            Advertisement.objects.get_or_create(
                house=house, defaults={"is_approved": True}
            )

    def create_reviews(self, houses, users):
        review_texts = [
            "Absolutely loved staying here. The location was perfect and the amenities exceeded my expectations.",
            "The property was clean and well-maintained. The host was friendly and responsive.",
            "A wonderful experience. The neighborhood is vibrant, and the house has all the modern conveniences.",
        ]
        for index, house in enumerate(houses):
            for i, review_text in enumerate(review_texts):
                Review.objects.create(
                    advertisement=house.advertisement,
                    user=users[(index + i) % len(users)],
                    rating=5 if i == 0 else 4 if i == 1 else 5,
                    text=review_text,
                )
