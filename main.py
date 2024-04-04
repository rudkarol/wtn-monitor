from monitor import Monitor
from csv_loader import CsvLoader


if __name__ == '__main__':
    print('1. Start monitor')
    print('2. Update wtn_acceptable.csv')

    option = input('Choose option: ')

    if option == '1':
        monitor = Monitor()
        monitor.start()
    elif option == '2':
        csv_loader = CsvLoader()
        csv_loader.update_file()
