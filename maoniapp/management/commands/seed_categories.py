from django.core.management.base import BaseCommand
from ...models.category import Category  # Replace 'app_name' with your app name

class Command(BaseCommand):
    help = "Seed the database with initial business categories"

    def handle(self, *args, **kwargs):
        categories = [
            "Agriculture",
            "ArtAndDesign",
            "Automotive",
            "BankAndFinance",
            "Chemical",
            "Construction",
            "Consulting",
            "ConsumerGoods",
            "Education",
            "Ecommerce",
            "Energy",
            "EnvironmentalServices",
            "Entertainment",
            "FashionAndApparel",
            "FoodAndBeverage",
            "GovernmentAndPublicSector",
            "Healthcare",
            "Hospitality",
            "InformationTechnology",
            "Insurance",
            "LegalServices",
            "Logistics",
            "MarketingAndAdvertising",
            "Media",
            "Mining",
            "Nonprofit",
            "Pharmaceutical",
            "PersonalCareAndBeauty",
            "ProfessionalServices",
            "RealEstate",
            "ResearchAndDevelopment",
            "Retail",
            "SportsAndRecreation",
            "Telecommunications",
            "Transportation",
            "Utilities",
            "WholesaleAndDistribution",
        ]


        for category_name in categories:
            category, created = Category.objects.get_or_create(name=category_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added category: {category_name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Category already exists: {category_name}"))
