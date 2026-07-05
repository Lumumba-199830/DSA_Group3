# Defines a class called Bird to represent a bird in the poultry farm
class Bird:

    # Constructor
    def __init__(self, tag_id, breed, age, weight, egg_count, health_status):
        self.tag_id = tag_id
        self.breed = breed
        self.age = age
        self.weight = weight
        self.egg_count = egg_count
        self.health_status = health_status

    # Displays bird information
    def __str__(self):
        return (
            f"Tag ID: {self.tag_id}\n"
            f"Breed: {self.breed}\n"
            f"Age: {self.age} weeks\n"
            f"Weight: {self.weight} kg\n"
            f"Egg Count: {self.egg_count}\n"
            f"Health Status: {self.health_status}"
        )


# Hash Table Class
class HashTable:

    # Constructor
    def __init__(self, size=1009):

        self.size = size

        # Creates empty buckets for chaining
        self.table = [[] for _ in range(size)]

    # Hash Function
    def hash_function(self, tag_id):

        hash_value = 0

        for char in tag_id:
            hash_value = (hash_value * 31 + ord(char)) % self.size

        return hash_value

    # Insert Bird
    def insert(self, bird):

        index = self.hash_function(bird.tag_id)

        # Prevent duplicate Tag IDs
        for item in self.table[index]:

            if item.tag_id == bird.tag_id:
                print("Bird already exists!")
                return

        self.table[index].append(bird)

    # Search Bird
    def search(self, tag_id):

        index = self.hash_function(tag_id)

        for bird in self.table[index]:

            if bird.tag_id == tag_id:
                return bird

        return None

    # Delete Bird
    def delete(self, tag_id):

        index = self.hash_function(tag_id)

        for i, bird in enumerate(self.table[index]):

            if bird.tag_id == tag_id:

                del self.table[index][i]

                return True

        return False



# START OF MENU SYSTEM


hash_table = HashTable()

while True:

    print("\n===== POULTRY FARM MANAGEMENT SYSTEM =====")
    print("1. Add Bird")
    print("2. Search Bird")
    print("3. Delete Bird")
    print("4. Exit")

    choice = input("Enter your choice: ")

    # ADD BIRD
    if choice == "1":

        tag_id = input("Enter Tag ID: ")
        breed = input("Enter Breed: ")
        age = int(input("Enter Age (weeks): "))
        weight = float(input("Enter Weight (kg): "))
        egg_count = int(input("Enter Egg Count: "))
        health_status = input("Enter Health Status: ")

        bird = Bird(
            tag_id,
            breed,
            age,
            weight,
            egg_count,
            health_status
        )

        hash_table.insert(bird)

        print("Bird added successfully!")

    # SEARCH BIRD
    elif choice == "2":

        tag_id = input("Enter Tag ID to search: ")

        result = hash_table.search(tag_id)

        if result:

            print("\nBird Found")
            print(result)

        else:

            print("Bird not found.")

    # DELETE BIRD
    elif choice == "3":

        tag_id = input("Enter Tag ID to delete: ")

        if hash_table.delete(tag_id):

            print("Bird deleted successfully!")

        else:

            print("Bird not found.")

    # EXIT SYSTEM
    elif choice == "4":

        print("Exiting system...")
        break

    # INVALID OPTION
    else:

        print("Invalid choice. Please try again.")