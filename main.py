from assets.databases.BasicModel import BasicModel
from dotenv import load_dotenv

load_dotenv()

def main():

    db = BasicModel('products')
    print(db.get_all())

main()