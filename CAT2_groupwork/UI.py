from backend import (
    FlockRegistry,
    Bird,
    DuplicateTagIDError,
    BirdNotFoundError,
)


def print_header(title: str):
    print("\n" + "=" * 60)
    print(title.center(60))
    print("=" * 60)


def print_flock_table(birds):
    if not birds:
        print("No birds in the registry yet.")
        return
    print(f"{'TAG ID':<8} | {'BREED':<10} | {'AGE':>4} | {'WEIGHT':>7} | "
          f"{'EGGS':<9} | HEALTH")
    print("-" * 60)
    for bird in birds:
        print(bird)


def prompt_new_bird() -> Bird:
    print("\n-- Add New Bird --")
    tag_id = input("Tag ID (e.g. PF-001): ").strip()
    breed = input("Breed (Broiler / Layer / Kienyeji): ").strip()
    age_weeks = int(input("Age (weeks): ").strip())
    weight_kg = float(input("Weight (kg): ").strip())
    egg_count = int(input("Egg count: ").strip())
    health_status = input(
        "Health status (Healthy / Sick / Critical) [Healthy]: "
    ).strip() or "Healthy"
    return Bird(tag_id, breed, age_weeks, weight_kg, egg_count, health_status)


def run_ui():
    registry = FlockRegistry()

    menu = """
1. Add bird
2. View all birds
3. Search bird by Tag ID
4. Edit bird
5. Delete bird
6. Exit
"""

    print_header("POULTRY FARM MANAGEMENT SYSTEM")

    while True:
        print(menu)
        choice = input("Select an option (1-6): ").strip()

        try:
            if choice == "1":
                bird = prompt_new_bird()
                registry.add_bird(bird)
                print(f"\n✔ Bird '{bird.tag_id}' added successfully.")

            elif choice == "2":
                print_header(f"FLOCK REGISTRY ({registry.count()} birds)")
                print_flock_table(registry.get_all_birds())

            elif choice == "3":
                tag_id = input("Enter Tag ID to search: ").strip()
                bird = registry.find_bird(tag_id)
                print("\n✔ Found:")
                print(bird)

            elif choice == "4":
                tag_id = input("Enter Tag ID to edit: ").strip()
                print("Leave a field blank to keep its current value.")
                current = registry.find_bird(tag_id)
                print(f"Current record: {current}")

                updates = {}
                new_weight = input("New weight (kg): ").strip()
                if new_weight:
                    updates["weight_kg"] = float(new_weight)
                new_age = input("New age (weeks): ").strip()
                if new_age:
                    updates["age_weeks"] = int(new_age)
                new_eggs = input("New egg count: ").strip()
                if new_eggs:
                    updates["egg_count"] = int(new_eggs)
                new_health = input("New health status: ").strip()
                if new_health:
                    updates["health_status"] = new_health

                updated = registry.edit_bird(tag_id, **updates)
                print(f"\n✔ Updated record: {updated}")

            elif choice == "5":
                tag_id = input("Enter Tag ID to delete: ").strip()
                removed = registry.delete_bird(tag_id)
                print(f"\n✔ Removed: {removed}")

            elif choice == "6":
                print("\nGoodbye!")
                break

            else:
                print("Invalid option, please choose 1-6.")

        except (DuplicateTagIDError, BirdNotFoundError, ValueError,
                AttributeError) as e:
            print(f"\n⚠ Error: {e}")


if __name__ == "__main__":
    run_ui()