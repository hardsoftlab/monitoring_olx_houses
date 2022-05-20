from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///college.db', echo=True)
Base = declarative_base()

Session = sessionmaker(bind=engine)


class Advert(Base):
    __tablename__ = 'adverts'

    id = Column(String, primary_key=True)
    name = Column(String)
    url = Column(String)

    price = Column(String)
    date = Column(String)
    image_url = Column(String)

    published = Column(Boolean, default=False)


Base.metadata.create_all(engine)


def get_or_create_advert(url, title=None, price=None, date=None, image_url=None):
    sess = Session()

    while True:
        adv_instance = sess.query(Advert).filter(Advert.url == url).first()
        if adv_instance is None:
            sess.add(
                Advert(
                    id=url,
                    name=title,
                    url=url,
                    price=price,
                    date=date,
                    image_url=image_url
                )
            )
            sess.commit()
        else:
            break


def get_unpublished_adverts():
    sess = Session()
    adverts = sess.query(Advert).filter(Advert.published == False).all()
    print(adverts)
    return adverts, sess
