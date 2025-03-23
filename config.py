import os

class Config:
    SECRET_KEY = 'hbnwdvbn ajnbsjn ahe'
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.getcwd(), 'database.sqlite3')}"


    # Stripe API Keys
    STRIPE_PUBLIC_KEY = 'pk_test_51Q4rrWK6Gwg9YiFhcAAJMss0QK8WkRngL2vJ718oRMpdpYxlvBAoh4gLO8RSqddeUVnswSYE7rjVycVvh9mThScD00EPokYAUf'
    STRIPE_SECRET_KEY = 'sk_test_51Q4rrWK6Gwg9YiFhSpTjzv87IYQ3QvXKXuNHrYaVmCAbVtZZN0aXifBEZZKWkVw4Ig3j9dKG9vSiuLrpolUyNgjA00CYwwpSpc'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
