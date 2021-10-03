import yaml

if __name__ == '__main__':
    stream = open('data.yaml', 'r', encoding="utf-8")
    dictionary = yaml.load_all(stream, Loader=yaml.FullLoader)
    for doc in dictionary:
        try:
            for key, value in doc.items():
                print(f'{key}: {value}')
        except:
            pass