from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Base, Item, Category

engine = create_engine('sqlite:///itemcatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


category1 = Category(category_name="Art")
session.add(category1)
session.commit()

category2 = Category(category_name="Electronics")
session.add(category2)
session.commit()

category3 = Category(category_name="Fashion")
session.add(category3)
session.commit()

category4 = Category(category_name="Music")
session.add(category4)
session.commit()

category5 = Category(category_name="Home")
session.add(category5)
session.commit()

category6 = Category(category_name="Games")
session.add(category6)
session.commit()

category7 = Category(category_name="Motors")
session.add(category7)
session.commit()

category8 = Category(category_name="Health")
session.add(category8)
session.commit()

category9 = Category(category_name="Sports")
session.add(category9)
session.commit()

category10 = Category(category_name="Toys")
session.add(category10)
session.commit()




