# seed.py
from .models import Product, Category, db

def insert_categories():
    category1 = Category(category_name="Music")
    db.session.add(category1)
    db.session.commit()
    print('Inserted categories.')

def add_products():
    lorem = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum. It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for 'lorem ipsum' will uncover many web sites still in their infancy. Various versions have evolved over the years, sometimes by accident, sometimes on purpose (injected humour and the like)."
    dummy1 = Product(
                name='dummy 1',
                creator='dummy 1',
                image_thumbnail="media/uploads/dummy1.jpg",
                description=lorem,
                variants=[{'name': 'standard', 'price': 100, 'stock': 1}],
                category_id=1
            )
    dummy2 = Product(
                name='dummy 2',
                creator='dummy 2',
                image_thumbnail="media/uploads/dummy2.jpg",
                description=lorem,
                variants=[{'name': 'standard', 'price': 10, 'stock': 20}],
                category_id=1
            )
    dummy3 = Product(
                name='dummy 3',
                creator='dummy 3',
                image_thumbnail="media/uploads/dummy3.jpeg",
                description=lorem,
                variants=[{'name': 'standard', 'price': 20, 'stock': 5}],
                category_id=1
            )
    dummy4 = Product(
                name='dummy 4',
                creator='dummy 4',
                image_thumbnail="media/uploads/dummy4.jpeg",
                description=lorem,
                variants=[{'name': 'standard', 'price': 50, 'stock': 10}],
                category_id=1
            )
    dummy5 = Product(
                name='dummy 5',
                creator='dummy 5',
                image_thumbnail="media/uploads/dummy5.png",
                description=lorem,
                variants=[{'name': 'standard', 'price': 20, 'stock': 200}],
                category_id=1
            )
    dummies = []
    dummies.extend([dummy1, dummy2, dummy3, dummy4, dummy5])
    for dummy in dummies:
        db.session.add(dummy)
    db.session.commit()