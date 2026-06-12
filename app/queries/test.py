import matplotlib.pyplot as plt

data = {
    "Aditya": {
        "age": [10, 12, 14, 15, 16],
        "salary": [10000, 12010, 5200, 15899, 22377]
    },
    "Mit": {
        "age": [11, 13, 15, 17, 19],
        "salary": [9000, 11000, 15000, 18000, 22000]
    }
}

for person, values in data.items():
    plt.figure()
    plt.bar(values["age"], values["salary"])
    plt.title(person)
    plt.show()
