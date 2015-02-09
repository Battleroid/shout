from shout import db


def main():
    db.drop_all()
    db.create_all()


if __name__ == '__main__':
    main()